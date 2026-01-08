#!/usr/bin/env python3
"""
agent.py — Multi-Agent report generator (AutoGen preferred, GROQ fallback)

Provides:
 - generate_report_with_autogen_multiagent(...)  # main flow
 - generate_report_with_rag(...)  # backward-compatible wrapper
 - generate_custom_report(...)  # single-prompt helper

Behavior:
 - If AutoGen + UserProxyAgent.initiate_chat is usable -> use AutoGen agents.
 - Otherwise fall back to a GROQ OpenAI-compatible endpoint (messages payload).
"""
from typing import Optional, List
import os
import time
import traceback
import json

# Load env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# HTTP client
try:
    import requests
    from requests.exceptions import RequestException, HTTPError, Timeout as RequestsTimeout
except Exception:
    requests = None
    RequestException = HTTPError = RequestsTimeout = Exception

# RAG retrieval (your module)
try:
    from rag_retrieval import retrieve_combined_data, retrieve_sales_data, retrieve_marketing_data
except Exception:
    # placeholder fallbacks in case import fails at runtime
    def retrieve_combined_data(q, n_results=5): return f"[RAG missing] {q}"
    def retrieve_sales_data(q, n_results=5): return f"[RAG missing] {q}"
    def retrieve_marketing_data(q, n_results=5): return f"[RAG missing] {q}"

# Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or None
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
MODEL_NAME = os.getenv("GROQ_MODEL", os.getenv("MODEL_NAME", None))  # set in .env

TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.4"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
RETRY_COUNT = int(os.getenv("OPENAI_RETRY_COUNT", "3"))
RETRY_BACKOFF = float(os.getenv("OPENAI_RETRY_BACKOFF", "2.0"))

# fallback models list (optional override via GROQ_FALLBACK_MODELS)
fallback_env = os.getenv("GROQ_FALLBACK_MODELS", "")
if fallback_env.strip():
    GROQ_FALLBACK_MODELS = [m.strip() for m in fallback_env.split(",") if m.strip()]
else:
    GROQ_FALLBACK_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "groq/compound", "groq/compound-mini"]

# AutoGen detection
AUTOGEN_AVAILABLE = False
try:
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent  # type: ignore
    AUTOGEN_AVAILABLE = True
    print("[agent] AutoGen import succeeded")
except Exception:
    print("[agent] AutoGen not importable; will use GROQ fallback if configured")


# -------------------------
# Helpers
# -------------------------
def _truncate_context(context: str, max_chars: int = 14000) -> str:
    if not context:
        return context
    if len(context) <= max_chars:
        return context
    head = context[: max_chars // 2]
    tail = context[- (max_chars // 2) :]
    return head + "\n\n[...context truncated...]\n\n" + tail


def _groq_models_list():
    """Attempt to GET /openai/v1/models from Groq (helpful when model selection fails)."""
    if requests is None:
        return None, "requests not installed", None
    parsed_url = GROQ_API_URL
    # Build models URL from base path
    # Example: if GROQ_API_URL == https://api.groq.com/openai/v1/chat/completions
    # models endpoint is https://api.groq.com/openai/v1/models
    base = None
    try:
        from urllib.parse import urlparse, urljoin
        p = urlparse(parsed_url)
        base = f"{p.scheme}://{p.netloc}"
        models_url = urljoin(base, "/openai/v1/models")
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"} if GROQ_API_KEY else {}
        r = requests.get(models_url, headers=headers, timeout=20)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return r.status_code, body, models_url
    except Exception as e:
        return None, str(e), base


# -------------------------
# GROQ helper (OpenAI-compatible messages)
# -------------------------
def _groq_chat(prompt: str, system_message: Optional[str] = None, model: Optional[str] = MODEL_NAME) -> str:
    """
    Send an OpenAI-compatible `messages` payload to Groq.
    Automatically attempts fallback models if Groq returns model_decommissioned or model_not_found.
    """
    if requests is None:
        raise RuntimeError("requests package not installed. Install `requests` to use GROQ fallback.")
    api_key = GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")
    api_url = GROQ_API_URL or os.environ.get("GROQ_API_URL", "")
    if not api_key or not api_url:
        raise RuntimeError("GROQ_API_KEY or GROQ_API_URL not set. Put them in .env or config.py")

    if not model:
        status, body, url = _groq_models_list()
        raise RuntimeError(
            "No GROQ_MODEL configured. Set GROQ_MODEL in .env to a model you have access to.\n"
            f"Attempted models list endpoint returned status={status} body={json.dumps(body, indent=2) if isinstance(body,(dict,list)) else body}\n"
            f"Models endpoint tried: {url}"
        )

    safe_prompt = _truncate_context(prompt, max_chars=14000)
    safe_system = _truncate_context(system_message or "", max_chars=2000)
    messages = []
    if safe_system:
        messages.append({"role": "system", "content": safe_system})
    messages.append({"role": "user", "content": safe_prompt})

    # candidate models: requested model then fallback list
    candidates = [model] + [m for m in GROQ_FALLBACK_MODELS if m != model]

    last_exc = None
    for candidate in candidates:
        attempt = 0
        while attempt < RETRY_COUNT:
            attempt += 1
            payload = {
                "model": candidate,
                "messages": messages,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            try:
                resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
                if resp.status_code >= 400:
                    try:
                        body = resp.json()
                    except Exception:
                        body = resp.text
                    # If model error suggests decommission or not found -> break to next candidate
                    code = None
                    if isinstance(body, dict):
                        err = body.get("error", {})
                        code = err.get("code") or err.get("type")
                    if code and ("model_decommissioned" in str(code) or "model_not_found" in str(code)):
                        print(f"[agent][_groq_chat] Groq rejected model '{candidate}': {body}")
                        break  # try next model candidate
                    raise RuntimeError(f"GROQ API error: status={resp.status_code} body={json.dumps(body) if isinstance(body,(dict,list)) else body}")
                # parse success
                resp_json = resp.json()
                if isinstance(resp_json, dict) and "choices" in resp_json and isinstance(resp_json["choices"], list) and resp_json["choices"]:
                    choice = resp_json["choices"][0]
                    if isinstance(choice, dict) and "message" in choice and isinstance(choice["message"], dict):
                        return str(choice["message"].get("content", "")).strip()
                    if isinstance(choice, dict) and "text" in choice:
                        return str(choice.get("text", "")).strip()
                # alternate shapes
                if isinstance(resp_json, dict) and "outputs" in resp_json and isinstance(resp_json["outputs"], list) and resp_json["outputs"]:
                    out0 = resp_json["outputs"][0]
                    if isinstance(out0, dict):
                        for k in ("content", "text", "output"):
                            if k in out0:
                                return str(out0[k]).strip()
                return json.dumps(resp_json, indent=2)
            except (RequestsTimeout, RequestException) as e:
                last_exc = e
                print(f"[agent][_groq_chat] Attempt {attempt} transient error for model {candidate}: {e}")
                if attempt >= RETRY_COUNT:
                    break
                time.sleep(RETRY_BACKOFF ** (attempt - 1))
                continue
            except Exception as e:
                last_exc = e
                print(f"[agent][_groq_chat] Attempt {attempt} error for model {candidate}: {e}")
                if attempt >= RETRY_COUNT:
                    break
                time.sleep(RETRY_BACKOFF ** (attempt - 1))
                continue
        # next candidate
        print(f"[agent][_groq_chat] Trying next model candidate after '{candidate}' (if any)")
    # exhausted candidates; return models list for helpful error
    status, body, url = _groq_models_list()
    raise RuntimeError(
        f"GROQ: all model candidates failed. Last exception: {last_exc}\n"
        f"Attempted models: {candidates}\n"
        f"Models endpoint returned status={status} body={json.dumps(body, indent=2) if isinstance(body,(dict,list)) else body}\n"
        f"Please set GROQ_MODEL to a model you have access to (update .env)."
    )


# -------------------------
# AutoGen helpers (best-effort)
# -------------------------
def create_autogen_config():
    return {
        "config_list": [
            {
                "model": MODEL_NAME or "llama-3.3-70b-versatile",
                "api_key": GROQ_API_KEY or os.environ.get("GROQ_API_KEY", ""),
            }
        ],
        "temperature": TEMPERATURE,
        "timeout": 120,
        "cache_seed": None,
    }


def _try_create_assistant(role_name: str, system_message: str):
    """Try a few constructor signatures for AssistantAgent; raise on last failure."""
    if not AUTOGEN_AVAILABLE:
        raise RuntimeError("AutoGen not available")
    last_exc = None
    tries = [
        ({"name": role_name, "system_message": system_message, "llm_config": create_autogen_config()}, False),
        ({"name": role_name, "system_message": system_message}, False),
        ((role_name, system_message, create_autogen_config()), True),
        ((role_name, system_message), True),
        ({"name": role_name, "prompt": system_message, "llm_config": create_autogen_config()}, False),
    ]
    for arg, positional in tries:
        try:
            if positional:
                if isinstance(arg, tuple):
                    return AssistantAgent(*arg)
            else:
                if isinstance(arg, dict):
                    return AssistantAgent(**arg)
        except Exception as e:
            last_exc = e
            continue
    # final fallback
    try:
        return AssistantAgent(role_name)
    except Exception as e:
        raise last_exc or e


def _try_create_user_proxy():
    if not AUTOGEN_AVAILABLE:
        raise RuntimeError("AutoGen not available")
    last_exc = None
    tries = [
        ({"name": "user_proxy", "human_input_mode": "NEVER", "max_consecutive_auto_reply": 0, "code_execution_config": False, "default_auto_reply": ""}, False),
        (("user_proxy",), True),
        ({"name": "user_proxy"}, False),
    ]
    for arg, positional in tries:
        try:
            if positional and isinstance(arg, tuple):
                return UserProxyAgent(*arg)
            elif isinstance(arg, dict):
                return UserProxyAgent(**arg)
        except Exception as e:
            last_exc = e
            continue
    # final fallback: try with name only
    try:
        return UserProxyAgent("user_proxy")
    except Exception as e:
        raise last_exc or e


def create_data_analyst_agent_autogen():
    system_message = """You are a Senior Data Analyst specializing in sales and marketing analytics.
You receive RAG-provided context and must be precise and data-driven."""
    return _try_create_assistant("data_analyst", system_message)


def create_report_writer_agent_autogen():
    system_message = """You are a Professional Report Writer specialized in business reporting.
Produce clear, actionable executive reports with sections and recommendations."""
    return _try_create_assistant("report_writer", system_message)


def create_user_proxy_autogen():
    return _try_create_user_proxy()


# -------------------------
# Main multi-agent flow (AutoGen or GROQ fallback)
# -------------------------
def generate_report_with_autogen_multiagent(query: str, report_type: str = "combined", n_results: int = 8) -> str:
    print("\n[ReportGen] Starting Multi-Agent Analysis...")
    if report_type == "sales":
        context = retrieve_sales_data(query, n_results=n_results)
    elif report_type == "marketing":
        context = retrieve_marketing_data(query, n_results=n_results)
    else:
        context = retrieve_combined_data(query, n_results=n_results)

    context = _truncate_context(context, max_chars=14000)

    # Try AutoGen only if user_proxy.initiate_chat exists
    if AUTOGEN_AVAILABLE:
        try:
            user_proxy = create_user_proxy_autogen()
            if user_proxy and hasattr(user_proxy, "initiate_chat"):
                print("[ReportGen] AutoGen + user_proxy detected — using AutoGen flow")
                analyst = create_data_analyst_agent_autogen()
                writer = create_report_writer_agent_autogen()

                analysis_prompt = f"""Based on the following data retrieved from our database, please analyze and identify key insights:

Query: {query}

{context}

Please provide:
1. Key metrics and numbers
2. Notable trends
3. Top performers
4. Areas of concern
5. Data-driven insights"""

                user_proxy.initiate_chat(analyst, message=analysis_prompt, max_turns=1)
                analyst_findings = user_proxy.last_message(analyst)["content"]

                report_prompt = f"""Based on the data analyst's findings, create a comprehensive professional report.

Original Query: {query}

Data Analyst's Findings:
{analyst_findings}

Create a detailed report with these sections:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Insights and Trends
5. Recommendations

Make it professional, clear, and actionable."""

                user_proxy.initiate_chat(writer, message=report_prompt, max_turns=1)
                final_report = user_proxy.last_message(writer)["content"]
                print("[ReportGen] AutoGen flow complete.")
                return final_report
            else:
                print("[ReportGen] AutoGen available but user_proxy.initiate_chat not usable — skipping AutoGen and using GROQ fallback")
        except Exception as e:
            print(f"[ReportGen] AutoGen flow failed (falling back): {e}")
            traceback.print_exc()

    # GROQ fallback
    print("[ReportGen] Using GROQ fallback for analysis + report generation...")
    if not (GROQ_API_KEY or os.environ.get("GROQ_API_KEY")):
        raise RuntimeError("Neither AutoGen nor GROQ configured. Set GROQ_API_KEY and GROQ_API_URL in .env")

    analyst_system = "You are a Senior Data Analyst specializing in sales and marketing analytics. Be precise and analytical."
    analysis_prompt = f"""Based on the following data retrieved from our database, please analyze and identify key insights.

Query: {query}

{context}

Please provide:
1. Key metrics and numbers
2. Notable trends
3. Top performers
4. Areas of concern
5. Data-driven insights"""

    analyst_findings = _groq_chat(analysis_prompt, system_message=analyst_system, model=MODEL_NAME)
    if not analyst_findings:
        raise RuntimeError("GROQ returned empty analyst findings")

    writer_system = "You are a Professional Report Writer specialized in business reporting. Write clear, actionable executive-level reports."
    report_prompt = f"""Based on the data analyst's findings below, create a comprehensive professional report.

Original Query: {query}

Data Analyst's Findings:
{analyst_findings}

Create a detailed report with these sections:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Insights and Trends
5. Recommendations

Make it professional, clear, and actionable."""

    final_report = _groq_chat(report_prompt, system_message=writer_system, model=MODEL_NAME)
    if not final_report:
        raise RuntimeError("GROQ returned empty final report")

    print("[ReportGen] GROQ flow complete.")
    return final_report


# Backwards-compatible wrapper expected by older code
def generate_report_with_rag(query: str, report_type: str = "combined", n_results: int = 5) -> str:
    return generate_report_with_autogen_multiagent(query, report_type=report_type, n_results=n_results)


def generate_custom_report(prompt_with_context: str) -> str:
    """Single-step custom prompt (analyst-like)."""
    if AUTOGEN_AVAILABLE:
        try:
            user_proxy = create_user_proxy_autogen()
            if user_proxy and hasattr(user_proxy, "initiate_chat"):
                analyst = create_data_analyst_agent_autogen()
                user_proxy.initiate_chat(analyst, message=prompt_with_context, max_turns=1)
                return user_proxy.last_message(analyst)["content"]
        except Exception:
            pass
    # fallback to GROQ
    return _groq_chat(prompt_with_context, system_message="You are a data analyst. Be precise and base your analysis on the context.", model=MODEL_NAME)


# Quick test when run directly
if __name__ == "__main__":
    q = "Analyze the top performing products and their sales trends"
    try:
        print(generate_report_with_rag(q, report_type="sales", n_results=5))
    except Exception as e:
        print("Error:", e)
