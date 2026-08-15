import os
import sys
import logging
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from pydantic import BaseModel, Field

import importlib
try:
    fastapi_mod = importlib.import_module("fastapi")
    FastAPI = fastapi_mod.FastAPI
    HTTPException = fastapi_mod.HTTPException
    CORSMiddleware = importlib.import_module("fastapi.middleware.cors").CORSMiddleware
except ImportError:
    raise RuntimeError(
        "fastapi is required to run this application. "
        "Install it with 'pip install fastapi[all]'"
    ) from None

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from ai_agent import get_response_from_ai_agent, DEFAULT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ALLOWED_MODEL_NAMES = [
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "llama-3.3-70b-versatile",
    "gpt-4o-mini",
]


class ChatRequest(BaseModel):
    model_name: str = Field(default="gpt-4o-mini", description="Model identifier, e.g. gpt-4o-mini")
    model_provider: str = Field(default="OpenAI", description="Provider: 'OpenAI' or 'Groq'")
    system_prompt: str = Field(default=DEFAULT_SYSTEM_PROMPT, description="System prompt for the agent")
    messages: List[str] = Field(default_factory=list, description="Conversation messages; last one is used as query")
    allow_search: bool = Field(default=False, description="Enable Tavily web-search tool")


class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    used_mock: bool = False
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    title: str
    openai_key_configured: bool
    groq_key_configured: bool
    tavily_key_configured: bool


app = FastAPI(
    title="AI Agent Chatbot API",
    description="LangGraph-powered AI Agent Chatbot with OpenAI/Groq + optional Tavily web search.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _provider_requires_key(provider: str) -> bool:
    prov = (provider or "").strip().lower()
    if prov == "groq":
        return not bool(os.environ.get("GROQ_API_KEY"))
    if prov == "openai":
        return not bool(os.environ.get("OPENAI_API_KEY"))
    return True


@app.get("/", response_model=HealthResponse, tags=["meta"])
async def root():
    return HealthResponse(
        status="ok",
        title=app.title,
        openai_key_configured=bool(os.environ.get("OPENAI_API_KEY")),
        groq_key_configured=bool(os.environ.get("GROQ_API_KEY")),
        tavily_key_configured=bool(os.environ.get("TAVILY_API_KEY")),
    )


@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health():
    return await root()


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat_endpoint(request: ChatRequest):
    if request.model_name not in ALLOWED_MODEL_NAMES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid model name",
                "allowed_models": ALLOWED_MODEL_NAMES,
            },
        )

    if isinstance(request.messages, list) and len(request.messages) > 0:
        query_text = request.messages[-1]
    else:
        query_text = ""

    if not query_text or not str(query_text).strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "Empty query. Please provide at least one message."},
        )

    use_mock = _provider_requires_key(request.model_provider)

    error_text: Optional[str] = None
    final_response: Optional[str] = None

    try:
        final_response = get_response_from_ai_agent(
            llm_id=request.model_name,
            query=query_text,
            allow_search=request.allow_search,
            system_prompt=request.system_prompt,
            provider=request.model_provider,
            use_mock=use_mock,
        )
    except Exception as e:
        error_text = str(e)
        logger.warning("Agent init/invoke failed (%s). Retrying with mock/dry-run.", error_text)
        if not use_mock:
            try:
                final_response = get_response_from_ai_agent(
                    llm_id=request.model_name,
                    query=query_text,
                    allow_search=False,
                    system_prompt=request.system_prompt,
                    provider=request.model_provider,
                    use_mock=True,
                )
                use_mock = True
            except Exception:
                final_response = None

    if final_response is None:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Agent error: {error_text or 'Unknown error'}"},
        )

    return ChatResponse(
        response=final_response,
        model=request.model_name,
        provider=request.model_provider,
        used_mock=use_mock,
        error=error_text,
    )


if __name__ == "__main__":
    try:
        uvicorn = importlib.import_module("uvicorn")
    except ImportError:
        raise RuntimeError(
            "uvicorn is required to run this application. "
            "Install it with 'pip install uvicorn'"
        ) from None
    uvicorn.run(app, host="0.0.0.0", port=8000)
