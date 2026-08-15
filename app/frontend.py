import os
import time
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    import streamlit as st
except Exception:
    import sys
    sys.exit("Missing dependency 'streamlit'. Install it with: pip install streamlit")

try:
    import requests
except Exception:
    import sys
    sys.exit("Missing dependency 'requests'. Install it with: pip install requests")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_NAME = "AI Agent Chatbot"
TAGLINE = "LangGraph · FastAPI · Streamlit"

API_URL = os.environ.get("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")

MODEL_NAMES_GROQ = [
    ("llama-3.3-70b-versatile", "Llama 3.3 70B Versatile (Groq)", "128k context, fast open-weight"),
    ("mixtral-8x7b-32768", "Mixtral 8x7B MoE (Groq)", "32k context, multilingual expert"),
    ("llama3-70b-8192", "Llama 3 70B (Groq)", "8k context, balanced Llama 3"),
]

MODEL_NAMES_OPENAI = [
    ("gpt-4o-mini", "GPT-4o Mini (OpenAI)", "128k context, fast & cost-effective"),
]

DEFAULT_SYSTEM_PROMPT = (
    "You are a smart, friendly, and helpful AI chatbot. "
    "Think step-by-step before you answer. Be clear, concise, and politely curious. "
    "If you do not know the answer, say so honestly instead of guessing."
)

WELCOME_MESSAGE = (
    "👋 Hi there! I'm your AI Agent powered by LangGraph and FastAPI. "
    "Pick a **provider + model** in the sidebar, tweak the **system prompt** if you want, "
    "optionally enable **Web Search**, and then ask me anything below. 🚀"
)

# ============================================================
# Page config & session bootstrap
# ============================================================
st.set_page_config(
    page_title=f"{PROJECT_NAME}",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug": "https://github.com/Pankaj429w63/ai-agent-chatbot-fastapi/issues",
        "About": f"**{PROJECT_NAME}** — {TAGLINE}. MIT Licensed.",
    },
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE, "ts": time.time()}
    ]
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
if "last_model" not in st.session_state:
    st.session_state.last_model = None
if "last_provider" not in st.session_state:
    st.session_state.last_provider = None
if "last_was_mock" not in st.session_state:
    st.session_state.last_was_mock = None


# ============================================================
# Inline CSS for a premium, human-quality look
# ============================================================
def _inject_style():
    st.markdown(
        """
        <style>
            /* Gradient header */
            .app-header {
                padding: 1.4rem 1.6rem 1.2rem;
                border-radius: 14px;
                background: linear-gradient(135deg, #1f2937 0%, #111827 40%, #0ea5e9 160%);
                color: #ffffff;
                box-shadow: 0 10px 30px rgba(14, 165, 233, 0.18);
                margin-bottom: 1.4rem;
            }
            .app-header h1 { margin: 0; font-size: 2rem; letter-spacing: -0.02em; }
            .app-header p  { margin: 0.4rem 0 0; opacity: 0.88; font-size: 0.98rem; }

            /* Chip badges */
            .chip-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.9rem; }
            .chip {
                display: inline-flex; align-items: center; gap: 0.4rem;
                background: rgba(255,255,255,0.10);
                padding: 0.28rem 0.7rem; border-radius: 999px;
                font-size: 0.78rem; color: #f8fafc;
                border: 1px solid rgba(255,255,255,0.14);
                backdrop-filter: blur(4px);
            }
            .chip .dot {
                width: 8px; height: 8px; border-radius: 50%; display: inline-block;
                box-shadow: 0 0 0 3px rgba(255,255,255,0.08);
            }
            .dot.on  { background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,0.25); }
            .dot.off { background: #ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,0.22); }
            .dot.warn{ background: #f59e0b; box-shadow: 0 0 0 3px rgba(245,158,11,0.22); }

            /* Sidebar card */
            .sidebar-card {
                border: 1px solid rgba(148,163,184,0.18);
                background: linear-gradient(180deg, rgba(15,23,42,0.60), rgba(15,23,42,0.35));
                border-radius: 12px; padding: 0.9rem 1rem; margin-bottom: 0.9rem;
            }
            .sidebar-card h4 { margin: 0 0 0.5rem; font-size: 0.82rem; letter-spacing: 0.08em;
                               text-transform: uppercase; color: #38bdf8; }
            .sidebar-card .muted { font-size: 0.78rem; color: #94a3b8; }

            /* Chat bubbles */
            .bubble {
                padding: 0.9rem 1.05rem;
                border-radius: 16px;
                line-height: 1.55;
                word-wrap: break-word;
                border: 1px solid transparent;
                margin-bottom: 0.2rem;
            }
            .bubble.user {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: #ffffff;
                border-top-right-radius: 4px;
                border-color: rgba(255,255,255,0.08);
            }
            .bubble.assistant {
                background: rgba(30, 41, 59, 0.55);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-top-left-radius: 4px;
                color: #e5e7eb;
            }
            .meta {
                font-size: 0.7rem; color: #64748b; margin-top: 0.15rem;
                display: flex; gap: 0.5rem; flex-wrap: wrap;
            }
            .meta span { opacity: 0.9; }

            /* Footer signature */
            .app-footer {
                margin-top: 3rem; padding-top: 1rem; border-top: 1px solid rgba(148,163,184,0.18);
                text-align: center; color: #64748b; font-size: 0.78rem;
            }

            /* Compact the top padding */
            .block-container { padding-top: 1.2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


_inject_style()


# ============================================================
# Helpers
# ============================================================
@st.cache_data(ttl=5, show_spinner=False)
def _probe_backend(url: str):
    try:
        r = requests.get(f"{url}/health", timeout=3)
        if r.ok:
            return True, r.json()
        return False, {"status_code": r.status_code, "text": r.text}
    except Exception as e:
        return False, {"error": str(e)}


def _bool_dot(b: bool, if_missing_label: str = "Not set") -> str:
    return (
        f'<span class="chip"><span class="dot on"></span> Configured</span>'
        if b
        else f'<span class="chip"><span class="dot off"></span> {if_missing_label}</span>'
    )


def _status_dot(ok: bool) -> str:
    return (
        f'<span class="chip"><span class="dot on"></span> Backend online</span>'
        if ok
        else f'<span class="chip"><span class="dot off"></span> Backend unreachable</span>'
    )


def _fmt_time(ts: float) -> str:
    try:
        return time.strftime("%H:%M:%S", time.localtime(ts))
    except Exception:
        return ""


# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    # ---- Backend status card ----
    backend_ok, backend_info = _probe_backend(API_URL)

    st.markdown(
        f"""
        <div class="sidebar-card">
          <h4>🔌 Backend</h4>
          <div style="font-size:0.9rem; font-weight:600; margin-bottom:0.35rem;">
            {API_URL}
          </div>
          <div class="muted">Health probe every 5 s</div>
          <div class="chip-row">{_status_dot(backend_ok)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if backend_ok and isinstance(backend_info, dict):
        st.markdown(
            f"""
            <div class="sidebar-card">
              <h4>🔐 API Keys</h4>
              <div class="chip-row">
                {_bool_dot(backend_info.get("openai_key_configured", False), "OPENAI_API_KEY")}
                {_bool_dot(backend_info.get("groq_key_configured", False),   "GROQ_API_KEY")}
                {_bool_dot(backend_info.get("tavily_key_configured", False), "TAVILY_API_KEY")}
              </div>
              <p class="muted" style="margin-top:0.6rem;">
                Keys are never shown or logged — only presence is reported.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Model card ----
    st.markdown('<div class="sidebar-card"><h4>🧠 Provider & Model</h4>', unsafe_allow_html=True)
    provider = st.radio(
        "Provider",
        ("Groq", "OpenAI"),
        horizontal=True,
        label_visibility="collapsed",
    )

    if provider == "Groq":
        models = MODEL_NAMES_GROQ
        fmt = lambda x: x[1]
    else:
        models = MODEL_NAMES_OPENAI
        fmt = lambda x: x[1]

    selected_display = st.selectbox(
        "Model",
        models,
        index=0,
        format_func=fmt,
        label_visibility="collapsed",
    )
    selected_model_id, selected_model_label, selected_model_desc = selected_display

    st.markdown(
        f'<div class="muted">💡 {selected_model_desc}</div></div>',
        unsafe_allow_html=True,
    )

    # ---- Agent behaviour card ----
    st.markdown('<div class="sidebar-card"><h4>🎭 Agent Behaviour</h4>', unsafe_allow_html=True)
    system_prompt = st.text_area(
        "System prompt",
        value=DEFAULT_SYSTEM_PROMPT,
        height=150,
        label_visibility="collapsed",
        help="Defines the persona, tone, and guardrails of the AI agent.",
    )
    allow_web_search = st.checkbox(
        "🌐 Enable Web Search (Tavily)",
        value=False,
        help="Requires TAVILY_API_KEY on the backend. Uses TavilySearchResults (max 2).",
    )
    st.markdown(
        f'<div class="muted">Requests so far: **{st.session_state.request_count}**</div></div>',
        unsafe_allow_html=True,
    )

    # ---- Actions ----
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🧹 Clear chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": WELCOME_MESSAGE, "ts": time.time()}
            ]
            st.session_state.last_model = None
            st.session_state.last_provider = None
            st.session_state.last_was_mock = None
            st.rerun()
    with c2:
        if st.button("🔄 Re-check backend", use_container_width=True):
            _probe_backend.clear()
            st.rerun()

    st.markdown("---")
    st.caption(
        f"🏗️ **{PROJECT_NAME}** — {TAGLINE}  \n"
        f"FastAPI docs → [`/docs`]({API_URL}/docs) · [`/redoc`]({API_URL}/redoc)"
    )

# ============================================================
# Main header
# ============================================================
st.markdown(
    f"""
    <div class="app-header">
      <h1>🤖 {PROJECT_NAME}</h1>
      <p>Intelligent conversational agent — {TAGLINE}. ReAct + optional web search, graceful mock fallback.</p>
      <div class="chip-row">
        <span class="chip"><span class="dot {'on' if backend_ok else 'off'}"></span>
          {'Backend online' if backend_ok else 'Backend offline — mock only or start backend'}</span>
        <span class="chip">🧠 {selected_model_label}</span>
        <span class="chip">🏢 Provider: {provider}</span>
        <span class="chip">{'🌐 Web search ON' if allow_web_search else '🌐 Web search OFF'}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Chat history
# ============================================================
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        ts = msg.get("ts") or time.time()
        extra = msg.get("meta", {})

        if role == "user":
            a1, a2 = st.columns([7, 1])
            with a1:
                st.empty()
            with a2:
                st.markdown(
                    f'<div class="bubble user">{content}</div>'
                    f'<div class="meta" style="justify-content:flex-end;"><span>You · {_fmt_time(ts)}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            b1, b2 = st.columns([1, 7])
            with b1:
                badges = []
                if extra.get("model"):
                    badges.append(f"🧠 {extra['model']}")
                if extra.get("provider"):
                    badges.append(f"🏢 {extra['provider']}")
                if extra.get("used_mock"):
                    badges.append("🧪 Mock")
                badge_str = "  ·  ".join(badges)
                st.markdown(
                    f'<div class="bubble assistant">{content}</div>'
                    f'<div class="meta"><span>🤖 Assistant · {_fmt_time(ts)}</span>'
                    + (f"<span>{badge_str}</span>" if badge_str else "")
                    + "</div>",
                    unsafe_allow_html=True,
                )

# ============================================================
# Input
# ============================================================
user_input = st.chat_input("Ask anything — try 'Explain LangGraph in 3 bullets' or 'Give me 5 study tips for exams'")

if user_input:
    user_text = str(user_input).strip()
    if not user_text:
        st.warning("Please enter a non-empty message.")
    else:
        st.session_state.messages.append(
            {"role": "user", "content": user_text, "ts": time.time()}
        )
        st.session_state.request_count += 1

        with chat_container:
            u1, u2 = st.columns([7, 1])
            with u1:
                st.empty()
            with u2:
                st.markdown(
                    f'<div class="bubble user">{user_text}</div>'
                    f'<div class="meta" style="justify-content:flex-end;"><span>You · {_fmt_time(time.time())}</span></div>',
                    unsafe_allow_html=True,
                )

        conversation_messages = [
            m["content"] for m in st.session_state.messages if m["role"] == "user"
        ]

        payload = {
            "model_name": selected_model_id,
            "model_provider": provider,
            "system_prompt": system_prompt,
            "messages": conversation_messages,
            "allow_search": allow_web_search,
        }

        assistant_placeholder = st.empty()
        with chat_container:
            c1, c2 = st.columns([1, 7])
            with c1:
                with assistant_placeholder.container():
                    with st.spinner("🤔 Thinking…"):
                        final_text = None
                        used_mock = False
                        error_banner = None
                        response_meta = {}

                        try:
                            r = requests.post(
                                f"{API_URL}/chat", json=payload, timeout=180
                            )
                        except Exception as e:
                            error_banner = (
                                f"❌ Could not reach backend at `{API_URL}/chat`: **{e}**  \n"
                                "Start the backend with  \n"
                                "`python -m uvicorn app.backend:app --host 0.0.0.0 --port 8000 --reload`"
                            )
                        else:
                            if r.status_code != 200:
                                try:
                                    detail = r.json()
                                    if isinstance(detail, dict) and "detail" in detail:
                                        detail = detail["detail"]
                                except Exception:
                                    detail = r.text
                                error_banner = (
                                    f"⚠️ Backend replied **HTTP {r.status_code}**  \n```\n{detail}\n```"
                                )
                            else:
                                try:
                                    data = r.json()
                                except Exception:
                                    final_text = r.text
                                    data = {}

                                if isinstance(data, dict) and data.get("error"):
                                    error_banner = f"🧠 Agent error:  \n> {data['error']}"

                                if final_text is None and isinstance(data, dict):
                                    final_text = (
                                        data.get("response")
                                        or data.get("reply")
                                        or data.get("text")
                                        or data.get("message")
                                    )
                                    if final_text is None:
                                        final_text = str(data)
                                    used_mock = bool(data.get("used_mock", False))
                                    response_meta = {
                                        "model": data.get("model") or selected_model_id,
                                        "provider": data.get("provider") or provider,
                                        "used_mock": used_mock,
                                    }

                        if error_banner:
                            st.error(error_banner)
                            final_text = final_text or (
                                "I couldn't get a valid answer. See the error banner above."
                            )
                            response_meta.setdefault("model", selected_model_id)
                            response_meta.setdefault("provider", provider)

                        st.session_state.last_model = response_meta.get("model")
                        st.session_state.last_provider = response_meta.get("provider")
                        st.session_state.last_was_mock = used_mock

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": final_text,
                                "ts": time.time(),
                                "meta": response_meta,
                            }
                        )

        st.rerun()

# ============================================================
# Footer
# ============================================================
st.markdown(
    f"""
    <div class="app-footer">
      Made with 🤖 FastAPI · LangGraph · Streamlit &nbsp;·&nbsp;
      <a href="{API_URL}/docs" target="_blank">API Docs</a> &nbsp;·&nbsp;
      <a href="https://github.com/Pankaj429w63/ai-agent-chatbot-fastapi" target="_blank">GitHub</a> &nbsp;·&nbsp;
      MIT License
    </div>
    """,
    unsafe_allow_html=True,
)
