# rag_retrieval.py
"""
Robust RAG (Retrieval-Augmented Generation) helpers.

Exports (kept stable for agent.py integration):
 - retrieve_relevant_context(query, n_results=5, filter_type=None) -> Optional[dict]
 - retrieve_sales_data(query, n_results=5) -> str
 - retrieve_marketing_data(query, n_results=5) -> str
 - retrieve_combined_data(query, n_results=5) -> str

Notes:
 - Expects `vector_db.query_vectordb(collection, query, n_results, filter_dict)` and
   `vector_db.initialize_chromadb()` to exist in your repo. If missing, functions
   degrade gracefully and return a helpful string.
"""
from typing import Any, Dict, List, Optional, Union
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# Try to import user-provided vector DB adapter functions
try:
    from vector_db import query_vectordb, initialize_chromadb  # type: ignore
except Exception:
    query_vectordb = None
    initialize_chromadb = None
    logger.debug("vector_db adapter not found; retrieval functions will return placeholders.")


def retrieve_relevant_context(query: str, n_results: int = 5, filter_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve raw results from the vector DB. Returns a dict or None on failure."""
    if initialize_chromadb is None or query_vectordb is None:
        logger.warning("vector_db functions not available; cannot fetch real context.")
        return None

    try:
        _, collection = initialize_chromadb()
    except Exception as e:
        logger.exception("Failed to initialize vector DB collection: %s", e)
        return None

    filter_dict = {"type": filter_type} if filter_type else None

    try:
        results = query_vectordb(collection, query, n_results=n_results, filter_dict=filter_dict)
        # Some adapters may return a list of docs directly; normalize common simple shapes here
        if isinstance(results, list):
            return {"documents": [results], "metadatas": [[]], "distances": [[]]}
        return results
    except Exception as e:
        logger.exception("Vector DB query failed: %s", e)
        return None


def format_retrieval_results(results: Optional[Dict[str, Any]]) -> Union[str, List[Dict[str, Any]]]:
    """Normalize and format raw retrieval results into a list of items or a string message."""
    if not results:
        return "No relevant information found."

    try:
        documents_block = results.get("documents")
        metadatas_block = results.get("metadatas")
        distances_block = results.get("distances")

        # Handle nested list shapes like [ [doc1, doc2, ...] ]
        if isinstance(documents_block, list) and documents_block and isinstance(documents_block[0], list):
            documents = documents_block[0]
            metadatas = metadatas_block[0] if metadatas_block and isinstance(metadatas_block, list) and metadatas_block else [{}] * len(documents)
            distances = distances_block[0] if distances_block and isinstance(distances_block, list) and distances_block else [0.0] * len(documents)
        else:
            documents = documents_block or []
            metadatas = metadatas_block if metadatas_block else [{} for _ in documents]
            distances = distances_block if distances_block else [0.0 for _ in documents]

        if not documents:
            return "No relevant information found."

        formatted: List[Dict[str, Any]] = []
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            if doc is None:
                continue
            try:
                relevance_score = max(0.0, min(1.0, 1.0 - float(dist)))
            except Exception:
                relevance_score = 1.0
            item = {
                "rank": i + 1,
                "relevance_score": relevance_score,
                "type": (meta or {}).get("type", "unknown"),
                "content": doc if isinstance(doc, str) else str(doc),
                "metadata": meta or {},
            }
            formatted.append(item)
        return formatted
    except Exception as e:
        logger.exception("Failed to format retrieval results: %s", e)
        return "No relevant information found."


def _safe_currency(val: Any) -> str:
    """Format numeric currency safely for inclusion in prompts."""
    try:
        if val is None:
            return "N/A"
        v = float(val)
        if abs(v - int(v)) < 0.001:
            return f"${int(v):,}"
        return f"${v:,.2f}"
    except Exception:
        return str(val)


def create_context_string(formatted_context: Union[str, List[Dict[str, Any]]], max_items: int = 5) -> str:
    """Create a single prompt-ready context string for the LLM."""
    if isinstance(formatted_context, str):
        return formatted_context

    parts: List[str] = ["Retrieved relevant information:"]
    count = 0
    for item in formatted_context:
        if count >= max_items:
            break
        count += 1
        parts.append(f"\n{item['rank']}. [{item['type'].upper()}] (Relevance: {item['relevance_score']:.2f})")
        content = item["content"]
        if len(content) > 2000:
            content = content[:2000] + " ...[truncated]"
        parts.append(f"   {content}")

        meta = item.get("metadata", {}) or {}
        meta_parts = []
        if item["type"] == "sales":
            product = meta.get("product") or meta.get("product_name") or "N/A"
            revenue = _safe_currency(meta.get("revenue"))
            region = meta.get("region", "N/A")
            quarter = meta.get("quarter", "N/A")
            meta_parts.append(f"Product: {product}")
            meta_parts.append(f"Revenue: {revenue}")
            meta_parts.append(f"Region: {region}")
            meta_parts.append(f"Quarter: {quarter}")
        elif item["type"] == "marketing":
            campaign = meta.get("campaign_name") or meta.get("campaign") or "N/A"
            channel = meta.get("channel", "N/A")
            budget = _safe_currency(meta.get("budget"))
            conversions = meta.get("conversions", "N/A")
            meta_parts.append(f"Campaign: {campaign}")
            meta_parts.append(f"Channel: {channel}")
            meta_parts.append(f"Budget: {budget}")
            meta_parts.append(f"Conversions: {conversions}")
        else:
            if isinstance(meta, dict):
                if "source" in meta:
                    meta_parts.append(f"Source: {meta['source']}")
                if "id" in meta:
                    meta_parts.append(f"ID: {meta['id']}")

        if meta_parts:
            parts.append("   " + " | ".join(meta_parts))

    if count == 0:
        return "No relevant information found."
    return "\n".join(parts)


# Convenience wrappers used by agent.py
def retrieve_sales_data(query: str, n_results: int = 5) -> str:
    results = retrieve_relevant_context(query, n_results=n_results, filter_type="sales")
    formatted = format_retrieval_results(results)
    return create_context_string(formatted)


def retrieve_marketing_data(query: str, n_results: int = 5) -> str:
    results = retrieve_relevant_context(query, n_results=n_results, filter_type="marketing")
    formatted = format_retrieval_results(results)
    return create_context_string(formatted)


def retrieve_combined_data(query: str, n_results: int = 5) -> str:
    results = retrieve_relevant_context(query, n_results=n_results)
    formatted = format_retrieval_results(results)
    return create_context_string(formatted)


if __name__ == "__main__":
    print("RAG retrieval smoke test")
    q = "Top performing products in North America"
    ctx = retrieve_combined_data(q, n_results=3)
    try:
        print("\nContext:\n", ctx)
    except Exception:
        print("\nContext (raw):", json.dumps(ctx, indent=2) if isinstance(ctx, (dict, list)) else str(ctx))
