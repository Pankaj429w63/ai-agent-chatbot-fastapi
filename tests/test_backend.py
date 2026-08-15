import pytest
from fastapi.testclient import TestClient

from backend import app, ALLOWED_MODEL_NAMES


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_health(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "title" in body
    for k in ("openai_key_configured", "groq_key_configured", "tavily_key_configured"):
        assert k in body
        assert isinstance(body[k], bool)


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_endpoint_mock_mode(client):
    payload = {
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI",
        "system_prompt": "You are helpful",
        "messages": ["What is Python?"],
        "allow_search": False,
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 200, f"body: {r.text}"
    body = r.json()
    assert body["model"] == "gpt-4o-mini"
    assert body["provider"] == "OpenAI"
    assert "response" in body
    assert isinstance(body["used_mock"], bool)
    assert body["used_mock"] is True


def test_chat_endpoint_groq_provider_mock(client):
    payload = {
        "model_name": "mixtral-8x7b-32768",
        "model_provider": "Groq",
        "system_prompt": "You are helpful",
        "messages": ["Hello"],
        "allow_search": False,
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "Groq"
    assert body["model"] == "mixtral-8x7b-32768"
    assert isinstance(body["used_mock"], bool)


def test_chat_endpoint_empty_messages_rejected(client):
    payload = {
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI",
        "system_prompt": "You are helpful",
        "messages": [],
        "allow_search": False,
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 400


def test_chat_endpoint_invalid_model_rejected(client):
    payload = {
        "model_name": "definitely-not-a-real-model",
        "model_provider": "OpenAI",
        "system_prompt": "p",
        "messages": ["hi"],
        "allow_search": False,
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 400
    body = r.json()
    assert "allowed_models" in body["detail"]


def test_frontend_payload_schema_matches_backend(client):
    """Simulate the exact JSON the Streamlit frontend sends."""
    payload = {
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI",
        "system_prompt": "Act as an AI chatbot who is smart and friendly",
        "messages": ["Tell me about FastAPI."],
        "allow_search": False,
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    for key in ("response", "model", "provider", "used_mock"):
        assert key in body
    assert isinstance(body["response"], str)
    assert len(body["response"]) > 0
