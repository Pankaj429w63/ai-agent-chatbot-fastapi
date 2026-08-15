import os
import logging
import argparse
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = "Act as an AI chatbot who is smart and friendly"


def get_response_from_ai_agent(llm_id: str,
                               query: str,
                               allow_search: bool = False,
                               system_prompt: Optional[str] = None,
                               provider: str = "OpenAI",
                               use_mock: bool = False) -> str:
    if use_mock:
        logger.info("Dry-run/mock mode enabled; returning canned response.")
        return f"[MOCK ANSWER] Query: {query} -- (system_prompt: {system_prompt or DEFAULT_SYSTEM_PROMPT})"

    try:
        from langgraph.prebuilt import create_react_agent
        from langchain_core.messages.ai import AIMessage
    except Exception as e:
        raise RuntimeError("Required agent libraries not installed: " + str(e))

    try:
        if provider == "Groq":
            from langchain_groq import ChatGroq
            llm = ChatGroq(model=llm_id)
        else:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model=llm_id)
    except Exception as e:
        raise RuntimeError("Required LLM library not installed or failed to init: " + str(e))

    tools = []
    if allow_search:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            tools.append(TavilySearchResults(max_results=2))
        except Exception as e:
            logger.warning("Tavily search tool unavailable: %s", e)

    state_modifier = system_prompt if system_prompt is not None else DEFAULT_SYSTEM_PROMPT

    agent = None
    try:
        agent = create_react_agent(model=llm, tools=tools, state_modifier=state_modifier)
    except TypeError as e:
        logger.warning("create_react_agent signature mismatch, retrying without state_modifier: %s", e)
        try:
            agent = create_react_agent(model=llm, tools=tools)
        except Exception:
            try:
                from langchain.agents import create_agent as create_react_agent_alt
                agent = create_react_agent_alt(model=llm, tools=tools)
            except Exception as e2:
                raise RuntimeError("Failed to create agent with available APIs: " + str(e2))
    except Exception as e:
        raise RuntimeError("Failed to create agent: " + str(e))

    messages_state = [{"role": "system", "content": state_modifier}, {"role": "user", "content": query}]
    state = {"messages": messages_state}

    try:
        response = agent.invoke(state)
    except Exception as invoke_err:
        logger.warning("Agent invocation failed: %s. Attempting local-transformers fallback.", invoke_err)
        try:
            import importlib
            transformers = importlib.import_module("transformers")
            pipeline = getattr(transformers, "pipeline")
            gen = pipeline("text-generation", model="gpt2")
            out = gen(query, max_length=200, do_sample=True, top_k=50)
            text = out[0].get("generated_text") if isinstance(out, list) and isinstance(out[0], dict) else str(out)
            return text
        except Exception as fallback_err:
            raise RuntimeError(
                "Agent invocation failed and local transformers fallback unavailable: " + str(fallback_err)
            ) from invoke_err

    messages = None
    if isinstance(response, dict):
        messages = response.get("messages") or response.get("outputs") or response.get("output")
    else:
        messages = getattr(response, "messages", None) or getattr(response, "outputs", None)

    if not messages:
        try:
            response = agent.invoke({"messages": query})
            if isinstance(response, dict):
                messages = response.get("messages") or response.get("outputs")
            else:
                messages = getattr(response, "messages", None) or getattr(response, "outputs", None)
        except Exception:
            raise RuntimeError("Agent returned no messages")

    ai_messages = []
    for m in messages:
        if isinstance(m, AIMessage):
            ai_messages.append(getattr(m, "content", ""))
        elif isinstance(m, dict):
            ai_messages.append(m.get("content") or m.get("text") or str(m))
        else:
            ai_messages.append(getattr(m, "content", str(m)))

    if not ai_messages:
        return str(messages)

    return ai_messages[-1]


def _cli_main():
    parser = argparse.ArgumentParser(description="Run ai_agent.get_response_from_ai_agent from CLI")
    parser.add_argument("--provider", default="OpenAI", choices=["OpenAI", "Groq"], help="LLM provider")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model id to use")
    parser.add_argument("--query", default="Tell me about the trends in crypto markets", help="User query")
    parser.add_argument("--allow-search", action="store_true", help="Enable Tavily search tool")
    parser.add_argument("--system-prompt", default=DEFAULT_SYSTEM_PROMPT, help="System prompt to use")
    parser.add_argument("--dry-run", action="store_true", help="Return a canned response without calling external APIs")
    args = parser.parse_args()

    try:
        result = get_response_from_ai_agent(llm_id=args.model,
                                           query=args.query,
                                           allow_search=args.allow_search,
                                           system_prompt=args.system_prompt,
                                           provider=args.provider,
                                           use_mock=args.dry_run)
        print(result)
    except Exception as e:
        logger.error("Failed to get response from agent: %s", e)
        raise


if __name__ == "__main__":
    _cli_main()
