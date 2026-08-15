<p align="center">
  <h1 align="center">
    <img src="https://img.shields.io/badge/🤖-AI_Agent_Chatbot_with_FastAPI-white?style=for-the-badge&logoColor=white" alt="Shield"/>
    &nbsp; AI Agent Chatbot with FastAPI
  </h1>
</p>

<p align="center">
  <h3 align="center">
    Intelligent Conversational Agent using LangGraph, FastAPI, Streamlit & Multi-Provider LLM Integration
  </h3>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FASTAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/LANGGRAPH-0078D4?style=for-the-badge&logo=openbankproject&logoColor=white" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/STREAMLIT-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/UVICORN-4B0082?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Uvicorn"/>
  <img src="https://img.shields.io/badge/OPENAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/GROQ-F55036?style=for-the-badge&logo=semanticrelease&logoColor=white" alt="Groq"/>
  <img src="https://img.shields.io/badge/PYDANTIC-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic"/>
  <img src="https://img.shields.io/badge/PYTEST-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest"/>
  <img src="https://img.shields.io/badge/LICENSE-MIT-brightgreen?style=for-the-badge" alt="MIT"/>
</p>

---

## 🚀 An End-to-End AI Chatbot System with LangGraph ReAct Agents, FastAPI Backend, Streamlit UI, Optional Web Search, and Graceful Local Fallback

---

## 📌 Overview

**AI Agent Chatbot with FastAPI** is a clean, beginner-friendly but professionally structured Gen AI application that demonstrates a production-style three-tier architecture:

-   **🤖 AI Agent Layer** — A ReAct-style agent built with **LangGraph** that can use an optional **Tavily** web-search tool.
-   **⚡ API Layer** — A typed, validated **FastAPI** backend exposing `/chat`, `/health`, and auto-documented Swagger/Redoc endpoints.
-   **🎨 UI Layer** — A polished **Streamlit** frontend with configurable provider/model, system prompt, web-search toggle, backend connectivity indicator, and multi-turn chat history.
-   **🧪 Test Layer** — A `pytest` suite (10 tests) covering the agent dry-run, API health, validation rules, and frontend↔backend contract.

The project is designed to **run out of the box without any API keys** by falling back to a `mock/dry-run` mode when a provider key is missing. Real inference is enabled simply by setting environment variables — no code changes required.

---

## ✨ Key Features

| #  | Feature | Description |
|----|---------|-------------|
| 1  | **Multi-Provider LLM Support** | Plug-and-play between **OpenAI** and **Groq** via config |
| 2  | **LangGraph ReAct Agent** | Reason + Act loop with configurable system prompt |
| 3  | **Optional Web Search** | Tavily search tool integration via `allow_search` flag |
| 4  | **Graceful Mock Mode** | Works without API keys — returns canned response for local dev |
| 5  | **Strong Typing** | Full Pydantic v2 request/response models with validation |
| 6  | **Auto-Generated API Docs** | Swagger UI at `/docs`, Redoc at `/redoc`, OpenAPI at `/openapi.json` |
| 7  | **CORS Enabled** | Ready for browser / cross-origin frontends |
| 8  | **Streamlit Chat UI** | Chat history, sidebar config, live backend health probe |
| 9  | **Comprehensive Test Suite** | 10 pytest tests, no paid API calls required |
| 10 | **Zero Hardcoded Secrets** | All credentials via `.env` / OS environment only |
| 11 | **Beginner Friendly CLI** | `ai_agent.py --dry-run` usable directly from terminal |

---

## 🏗️ System Architecture

```
                        ┌──────────────────────────┐
                        │       Streamlit UI       │
                        │  (app/frontend.py)        │
                        │  • Sidebar config        │
                        │  • Chat history          │
                        │  • Backend health probe  │
                        └───────────┬──────────────┘
                                    │  HTTPS/JSON (POST /chat)
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                                │
│                        (app/backend.py)                               │
│  ┌────────────┐   ┌────────────────────┐   ┌──────────────────────┐  │
│  │ Pydantic   │──▶│ CORS + Error       │──▶│  LangGraph Agent     │  │
│  │ Validation │   │ Handling           │   │  (ReAct + Tools)     │  │
│  └────────────┘   └────────────────────┘   └──────────┬───────────┘  │
└───────────────────────────────────────────────────────┼──────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────┐
                              ▼                         ▼             ▼
                     ┌──────────────────┐      ┌────────────────┐  ┌─────────────┐
                     │ OpenAI / Groq    │      │ Tavily Search  │  │ Local Mock  │
                     │ LLM Providers    │      │ (web results)  │  │ Fallback    │
                     └──────────────────┘      └────────────────┘  └─────────────┘
```

---

## 🧠 AI Pipeline (LangGraph ReAct Agent)

1.  **Input Parsing** — `system_prompt` + last message from `messages[]` are composed into agent state.
2.  **Provider & Model Routing** — `ChatOpenAI` or `ChatGroq` is selected based on the `model_provider` field.
3.  **Tool Binding** — If `allow_search=True`, the `TavilySearchResults` tool is bound to the agent.
4.  **ReAct Loop (LangGraph)** — The agent iterates: *Thought → Action → Observation* until a final answer is produced.
5.  **Graceful Degradation** — If the provider is unreachable or unauthenticated, the endpoint retries in `mock/dry-run` mode rather than returning 500.
6.  **Local Transform Fallback (optional)** — If `transformers`+`torch` are installed, runtime LLM failures fall back to a local `gpt2` pipeline.
7.  **Structured Response** — Final answer, model, provider, and `used_mock` flag are returned as typed JSON.

---

## 🤖 Models Used

| Provider | Model ID | Context | Use Case |
|----------|----------|---------|----------|
| **OpenAI** | `gpt-4o-mini` | 128k tokens | Fast, cost-effective general-purpose chat |
| **Groq** | `llama-3.3-70b-versatile` | 128k tokens | Open-weight, high-speed inference |
| **Groq** | `mixtral-8x7b-32768` | 32k tokens | Mixture-of-experts multilingual chat |
| **Groq** | `llama3-70b-8192` | 8k tokens | Balanced Llama 3 70B option |

> 💡 Models are validated server-side. Requests for any model outside the allowed list return HTTP 400 with the list of permitted identifiers.

---

## 🛠️ Technology Stack

| Category | Library | Purpose |
|----------|---------|---------|
| **Language** | Python 3.11+ | Runtime |
| **Backend** | FastAPI 0.115+ | Typed REST API |
| **ASGI** | Uvicorn | Async web server |
| **Validation** | Pydantic v2 | Request/response schemas |
| **Agent Orchestration** | LangGraph 0.2+ | ReAct agent runtime |
| **Core Abstractions** | LangChain Core | Messages, runnables |
| **Tool Integrations** | LangChain Community | Tavily search tool |
| **LLM Provider (OpenAI)** | langchain-openai | ChatOpenAI adapter |
| **LLM Provider (Groq)** | langchain-groq | ChatGroq adapter |
| **Search (optional)** | Tavily API | Real-time web search |
| **Frontend** | Streamlit 1.35+ | Interactive chat UI |
| **Configuration** | python-dotenv | `.env` file loading |
| **HTTP Client** | Requests | Frontend → backend calls |
| **Testing** | pytest + httpx + TestClient | Unit + API contract tests |

---

## 📁 Project Structure

```
ai-agent-chatbot-with-fastapi/
├── app/
│   ├── __init__.py
│   ├── ai_agent.py        # LangGraph ReAct agent + CLI entrypoint
│   ├── backend.py         # FastAPI app, routes, schemas, CORS
│   └── frontend.py        # Streamlit chat UI
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # sys.path bootstrap for pytest
│   ├── test_ai_agent.py   # 3 tests for dry-run agent behaviour
│   └── test_backend.py    # 7 tests for API health + validation + contract
├── .env.example           # Safe template for environment variables
├── .gitignore             # Secrets, cache, venv, IDE files ignored
├── LICENSE                # MIT
├── README.md              # This file
└── requirements.txt       # Authoritative dependency manifest
```

---

## ✅ Prerequisites

-   **Python 3.11 or newer** (3.13 recommended and tested)
-   **pip** / **venv** (ships with Python)
-   (Optional) **API Keys**:
    -   [OpenAI API Key](https://platform.openai.com/api-keys) for OpenAI models
    -   [Groq API Key](https://console.groq.com/keys) for Groq models
    -   [Tavily API Key](https://tavily.com/) for web-search tool

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Pankaj429w63/ai-agent-chatbot-fastapi.git
cd ai-agent-chatbot-with-fastapi
```

### 2. Create and activate a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔐 Environment Variables & `.env.example`

Copy the provided `.env.example` to `.env` and fill in only the providers you intend to use. The application runs without keys in `mock/dry-run` mode automatically.

```bash
# Linux/macOS
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

**.env** contents (edit with your keys — **never commit this file**):
```env
OPENAI_API_KEY=sk-...            # optional
GROQ_API_KEY=gsk_...             # optional
TAVILY_API_KEY=tvly-...          # optional, required only for web search
BACKEND_API_URL=http://127.0.0.1:8000   # optional, for Streamlit frontend
```

> 🔒 **Security Note:** `.env` is listed in `.gitignore`. Never commit secrets, keys, or credentials to version control.

---

## ▶️ How to Start the Backend

Run the FastAPI + Uvicorn backend on port 8000:

```bash
# From repository root
python -m uvicorn app.backend:app --host 0.0.0.0 --port 8000 --reload
```

Or, for the direct backend entry-point:
```bash
python app/backend.py
```

Once running, explore the auto-generated docs:

-   **Swagger UI**: 👉 http://127.0.0.1:8000/docs
-   **ReDoc**: 👉 http://127.0.0.1:8000/redoc
-   **Health check**: 👉 http://127.0.0.1:8000/health

---

## 🎨 How to Start the Frontend

In a **second terminal** (with the same venv activated):

```bash
streamlit run app/frontend.py
```

Streamlit will print a local URL (default: http://localhost:8501).

> The sidebar probes `/health` on load and shows the backend connectivity status. It also lists which keys are currently configured (without revealing them).

---

## 🖥️ Using the Agent from the CLI

You don't need to run the API or UI to try the agent. The dry-run mode is fully headless:

```bash
# Mock/dry-run (no API keys required)
python app/ai_agent.py --dry-run --query "What is LangGraph?"

# Real provider with key already in env
python app/ai_agent.py --provider OpenAI --model gpt-4o-mini --query "Explain FastAPI in 3 sentences."

# With web search (TAVILY_API_KEY needed)
python app/ai_agent.py --provider Groq --model llama-3.3-70b-versatile --allow-search --query "Latest AI news this week"
```

---

## 📡 API Endpoints & Examples

### `GET /` — Root / Meta health check
```bash
curl -s http://127.0.0.1:8000/ | python -m json.tool
```
```json
{
    "status": "ok",
    "title": "AI Agent Chatbot API",
    "openai_key_configured": false,
    "groq_key_configured": true,
    "tavily_key_configured": false
}
```

### `GET /health` — Alias for `/`

### `POST /chat` — Submit a query to the agent

**Request body (JSON):**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model_name` | string | `"gpt-4o-mini"` | Model id, must be in allowed list |
| `model_provider` | string | `"OpenAI"` | `"OpenAI"` or `"Groq"` |
| `system_prompt` | string | default agent prompt | Persona for the agent |
| `messages` | string[] | `[]` | Conversation; last element = current query |
| `allow_search` | bool | `false` | Enable Tavily search tool |

**Example via curl:**
```bash
curl -s -X POST http://127.0.0.1:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"model_name\":\"gpt-4o-mini\",\"model_provider\":\"OpenAI\",\"system_prompt\":\"You are a concise tutor\",\"messages\":[\"Explain pydantic in 2 sentences\"],\"allow_search\":false}"
```

**Response (JSON):**
```json
{
    "response": "[MOCK ANSWER] Query: Explain pydantic in 2 sentences -- (system_prompt: You are a concise tutor)",
    "model": "gpt-4o-mini",
    "provider": "OpenAI",
    "used_mock": true,
    "error": null
}
```

> When a real key is available, `used_mock` will be `false` and `response` will contain the provider's live generation.

---

## 🧪 Testing Instructions

The full `pytest` suite uses `TestClient` + dry-run mode — **no paid API calls are made**.

```bash
# From repo root
python -m pytest -v tests/
```

Expected output:
```
collected 10 items
tests/test_ai_agent.py::test_dry_run_contains_query PASSED
tests/test_ai_agent.py::test_dry_run_includes_system_prompt_default PASSED
tests/test_ai_agent.py::test_dry_run_custom_system_prompt PASSED
tests/test_backend.py::test_root_health PASSED
tests/test_backend.py::test_health_endpoint PASSED
tests/test_backend.py::test_chat_endpoint_mock_mode PASSED
tests/test_backend.py::test_chat_endpoint_groq_provider_mock PASSED
tests/test_backend.py::test_chat_endpoint_empty_messages_rejected PASSED
tests/test_backend.py::test_chat_endpoint_invalid_model_rejected PASSED
tests/test_backend.py::test_frontend_payload_schema_matches_backend PASSED

10 passed
```

---

## 🔧 Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies not installed in active env | Activate venv, then `pip install -r requirements.txt` |
| Streamlit shows *"Backend not reachable"* | FastAPI not started, or wrong `BACKEND_API_URL` | Start backend on port 8000; set `BACKEND_API_URL` env var if needed |
| `400 Invalid model name` | Model name not in `ALLOWED_MODEL_NAMES` | Use one of: `gpt-4o-mini`, `mixtral-8x7b-32768`, `llama-3.3-70b-versatile`, `llama3-70b-8192` |
| Response always starts with `[MOCK ANSWER]` | Provider's API key is missing from env | Set `OPENAI_API_KEY` or `GROQ_API_KEY` in your `.env` and restart the backend |
| Tavily tool silently disabled | `TAVILY_API_KEY` not set or `langchain-community` failed to load | Set the key; verify `allow_search` is `true` in the request |
| Port `8000` already in use | Another process listening there | Kill the old process, or bind uvicorn to another port (`--port 8001`) and update `BACKEND_API_URL` |
| `pytest` fails with import errors | Test paths not set up | Always run pytest **from the repo root**; `conftest.py` bootstraps `app/` on `sys.path` |

---

## 🔐 Security Note

-   **Never commit `.env`** — it is already in `.gitignore`.
-   **Never paste real keys into chat, issues, or screenshots.** This project uses environment variables only.
-   No keys are printed, logged, or echoed back by the API. The `/health` endpoint only reports whether each key is **configured or not** (booleans).
-   CORS currently allows `*` (great for local development). For production deployment, restrict `allow_origins` to your known domains.
-   Deploy behind a reverse proxy (nginx, Caddy, Traefik) with TLS termination before exposing this service publicly.

---

## 🌟 Future Improvements

Contributions and forks are welcome. Potential roadmap items:

-   💬 **Streaming responses** via Server-Sent Events (`text/event-stream`) for real-time token-by-token UX.
-   📚 **Persistent chat sessions** with SQLite/PostgreSQL and per-user `thread_id`.
-   🔐 **Authentication** (API key in header, OAuth2 with JWT, or signed cookies).
-   🛠️ **Additional tools** — SQL query, code interpreter, file upload, vector-store RAG.
-   🪛 **Additional providers** — Anthropic, Azure OpenAI, Ollama (local), vLLM, OpenRouter.
-   🐳 **Docker / Compose** packaging for one-command `docker compose up`.
-   ⚙️ **CI/CD** — GitHub Actions to run `pytest` on every PR.
-   📈 **Rate limiting, usage tracking, structured logging** (middleware).
-   🧩 **Frontend rewrite** in React/Next.js for more advanced UI control.

---

## 📄 License

This project is released under the **MIT License**.

See [LICENSE](LICENSE) for the full text.

---

<p align="center">
  <sub>Built with ❤️ using FastAPI, LangGraph & Streamlit.</sub>
</p>
