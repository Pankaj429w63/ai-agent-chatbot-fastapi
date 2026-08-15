import pytest

from ai_agent import get_response_from_ai_agent, DEFAULT_SYSTEM_PROMPT


def test_dry_run_contains_query():
    query = "unit test query"
    res = get_response_from_ai_agent(llm_id="gpt-4o-mini", query=query, use_mock=True)
    assert "[MOCK ANSWER]" in res
    assert query in res


def test_dry_run_includes_system_prompt_default():
    res = get_response_from_ai_agent(llm_id="gpt-4o-mini", query="x", use_mock=True)
    assert DEFAULT_SYSTEM_PROMPT in res


def test_dry_run_custom_system_prompt():
    custom = "You are a helpful pirate"
    res = get_response_from_ai_agent(
        llm_id="mixtral-8x7b-32768",
        query="hello",
        use_mock=True,
        system_prompt=custom,
        allow_search=True,
    )
    assert custom in res
    assert "[MOCK ANSWER]" in res
