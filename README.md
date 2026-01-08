# AI Sales & Marketing Report Generator

> Production-grade, agentic RAG system for automated analytics reporting — built for reliability, explainability and production readiness.

---

## Project summary

A complete end-to-end pipeline that retrieves sales & marketing data from a vector store (ChromaDB), performs multi-agent analysis (Microsoft AutoGen when available, GROQ/OpenAI-compatible fallback), generates polished executive reports, produces publication-quality visualizations, and delivers results via **HTML email (embedded charts)** and **Telegram**. This repository includes an interactive Streamlit demo, a scheduler for automated runs, and modular adapters for vector DBs and delivery channels.

---

## Key highlights (recruiter-friendly)

* Agentic multi-agent orchestration: Data Analyst + Report Writer agents coordinated by a User Proxy for auditable reasoning.
* RAG-powered context: robust retrieval and prompt-safe formatting for LLM inputs.
* GROQ / OpenAI-compatible fallback with retry and model fallback semantics.
* Multi-channel delivery: HTML email with inline charts + Telethon-based Telegram sender (supports sync/async exports).
* Production-first: scheduler (timezone aware), safe truncation, logging, and modular architecture.

---

## Quick start

1. Clone the repo and open it in VS Code.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Copy the `.env` content below into `.env` in the project root (for local testing only):

```env
OPENAI_API_KEY=
GMAIL_USER=ayushaks9990@gmail.com
GMAIL_APP_PASSWORD=
RECIPIENT_EMAIL=ayushaks999@gmail.com
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_PHONE=+916290591230
GROQ_API_KEY=
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=llama-3.3-70b-versatile
```

> **Security note:** the `.env` content above was provided for demonstration by the project owner. **Do not commit `.env` or any secret values to source control.** Use a secrets manager (GitHub Secrets, AWS/GCP/Azure secret stores) in production.

---

## Run the project

* Streamlit demo (interactive):

```bash
streamlit run app.py
```

* Generate charts locally:

```bash
python -c "from visualizations import generate_all_charts; print(generate_all_charts())"
```

* Send a test Telegram message (may prompt for login the first time):

```bash
python telegram_sender.py --test
```

* Run full scheduled pipeline once (test mode):

```bash
python scheduler.py now
```

---

## Files & structure (high level)

* `agent.py` — multi-agent orchestration (AutoGen preferred, GROQ fallback)
* `rag_retrieval.py` — vector DB normalization and prompt context creation
* `vector_db.py` — ChromaDB ingestion and query adapters
* `visualizations.py` — matplotlib charts + `generate_all_charts()`
* `email_sender_html.py` — HTML email + embedded images + attachments
* `telegram_sender.py` — Telethon integration for file delivery
* `scheduler.py` — timezone-aware schedule and `now` testing mode
* `app.py` — Streamlit frontend for demos and manual report generation

---

## Screenshots

Below are the screenshots saved in the `screenshots/` folder of this repo. They are embedded here for quick review in the GitHub README (relative paths):

<p align="center">
  <img src="screenshots/Report%20(1).png" alt="Report 1" width="700"/>
</p>

<p align="center">
  <img src="screenshots/Report%20(2).png" alt="Report 2" width="700"/>
</p>

### Email previews

<p align="center">
  <img src="screenshots/gmail1.png" alt="Gmail 1" width="600"/>
  <img src="screenshots/gmail2.png" alt="Gmail 2" width="600"/>
</p>

### Telegram previews

<p align="center">
  <img src="screenshots/tele1.png" alt="Telegram 1" width="600"/>
  <img src="screenshots/tele2.png" alt="Telegram 2" width="600"/>
</p>

---
