"""
python_basic_agent_agentsdk_google_adk.py - Basic agent built with the Google Agent Development Kit (ADK) AGENT SDK.

AGENT SDK = a framework that runs the agent loop for you. In python_basic_agent_without_AI.py
and the python_basic_agent_modelsdk_*.py files we wrote PERCEIVE -> THINK -> ACT -> OBSERVE ->
RESPOND ourselves. Here the Google Agent Development Kit (ADK) does THINK -> ACT -> OBSERVE (the tool-calling loop)
and memory internally: we only give it a model, instructions and plain Python functions as tools.
Only the GoogleADKAgent class below is framework-specific; compare any two
python_basic_agent_agentsdk_*.py files to see how agent SDKs differ.

Install:
    pip install google-adk litellm mcp

Setup (environment variables):
    Gemini (default):  GOOGLE_API_KEY=...  (free key at https://aistudio.google.com; optional: GEMINI_MODEL)
    or OpenAI / Ollama through LiteLLM:  OPENAI_API_KEY=sk-...  or  OPENAI_BASE_URL=http://localhost:11434/v1
    If the SDK is not installed or not configured, this file runs the rule-based agent from
    python_basic_agent_without_AI.py instead, so it always runs (keep both files in the same folder).

Run:
    python python_basic_agent_agentsdk_google_adk.py          # interactive chat mode
    python python_basic_agent_agentsdk_google_adk.py --demo   # run a scripted demo and exit

Requires: Python 3.10+ and the packages above.
"""

import asyncio
import os
import sys
from typing import Dict, List

from python_basic_agent_without_AI import calculator_tool, reverse_text_tool, time_tool, word_count_tool
from python_basic_agent_without_AI import main as fallback_main

try:
    from google.adk.agents import Agent
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.runners import InMemoryRunner
    from google.genai import types
except ImportError:
    Agent = None

GEMINI_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("OPENAI_BASE_URL") or None
USE_OPENAI = not GEMINI_KEY and bool(API_KEY or BASE_URL)  # ADK uses Gemini by default, others via LiteLLM
if GEMINI_KEY:
    os.environ.setdefault("GOOGLE_API_KEY", GEMINI_KEY)

# ---------------------------------------------------------------------------
# 1. TOOLS - the same tools as python_basic_agent_without_AI.py, as plain typed
#    functions. The agent SDK reads the names, type hints and docstrings to tell
#    the LLM what each tool does.
# ---------------------------------------------------------------------------

FACTS: Dict[str, str] = {}


def calculator(expression: str) -> str:
    """Evaluate a math expression such as '(12 + 8) * 3' or '2 ^ 10'.

    Args:
        expression: The math expression to evaluate.
    """
    try:
        return calculator_tool(expression)
    except Exception as exc:  # return errors to the LLM instead of crashing
        return f"Error: {exc}"


def get_time() -> str:
    """Get the current date and time."""
    return time_tool("")


def word_count(text: str) -> str:
    """Count the words and characters in a text.

    Args:
        text: The text to count.
    """
    return word_count_tool(text)


def reverse_text(text: str) -> str:
    """Reverse a piece of text.

    Args:
        text: The text to reverse.
    """
    return reverse_text_tool(text)


def remember(key: str, value: str) -> str:
    """Store a fact about the user, e.g. key='name', value='Bicche'.

    Args:
        key: The name of the fact.
        value: The value of the fact.
    """
    FACTS[key.strip().lower()] = value.strip()
    return f"Remembered: {key} is {value}."


def recall(key: str) -> str:
    """Look up a fact stored earlier with remember.

    Args:
        key: The name of the fact, e.g. 'name'.
    """
    return FACTS.get(key.strip().lower(), f"I don't know {key} yet.")


TOOLS = [calculator, get_time, word_count, reverse_text, remember, recall]

INSTRUCTIONS = (
    "You are a helpful basic agent. Always use the tools for math, time, word counts, "
    "reversing text and remembering or recalling facts. If no tool fits the request, "
    "say you cannot do it. Keep answers short."
)


# ---------------------------------------------------------------------------
# 2. THE AGENT SDK CLASS - the only framework-specific code in this file
# ---------------------------------------------------------------------------

def missing_reason() -> str:
    """Return why the agent SDK can't run yet ("" means ready)."""
    if Agent is None:
        return 'pip install google-adk litellm mcp'
    if not (GEMINI_KEY or API_KEY or BASE_URL):
        return "set GOOGLE_API_KEY (Gemini) or OPENAI_API_KEY / OPENAI_BASE_URL"
    return ""


class GoogleADKAgent:
    """Agent built with Google ADK: Agent + Runner + Session run the tool loop for us."""

    def __init__(self) -> None:
        self.name = "GoogleADK-Agent"
        if USE_OPENAI:
            model = LiteLlm(model=f"openai/{MODEL}", api_key=API_KEY or "none", api_base=BASE_URL)
            self.model_name = MODEL
        else:
            model = GEMINI_MODEL
            self.model_name = GEMINI_MODEL
        self.agent = Agent(name="basic_agent", model=model, instruction=INSTRUCTIONS, tools=TOOLS)
        self.runner = InMemoryRunner(agent=self.agent, app_name="basic_agent_app")
        session = asyncio.run(self.runner.session_service.create_session(app_name="basic_agent_app", user_id="user"))
        self.session_id = session.id  # the session is the conversation memory

    def run(self, user_input: str) -> str:
        message = types.Content(role="user", parts=[types.Part(text=user_input)])
        answer = ""
        for event in self.runner.run(user_id="user", session_id=self.session_id, new_message=message):
            if event.is_final_response() and event.content and event.content.parts:
                answer = "".join(part.text or "" for part in event.content.parts)
        return answer


# ---------------------------------------------------------------------------
# 3. ENTRY POINTS - same demo goals as the other files
# ---------------------------------------------------------------------------

DEMO_GOALS = [
    "calculate (12 + 8) * 3",
    "remember my name is Bicche",
    "what is my name",
    "what time is it and then calculate 2 ^ 10",
    "count words in agents perceive think act and observe",
    "reverse hello agent",
    "calculate 10 / 0",
    "sing me a song",
]


def ask(agent: "GoogleADKAgent", user_input: str) -> str:
    try:
        return agent.run(user_input)
    except Exception as exc:  # network/API problems must not crash the program
        return f"Error from the agent SDK: {exc}"


def run_demo(agent: "GoogleADKAgent") -> None:
    for goal in DEMO_GOALS:
        print(f"\nYou: {goal}")
        print(f"{agent.name}: {ask(agent, goal)}")
        print("-" * 70)
    print(f"Facts stored by the remember tool: {FACTS}")


def run_interactive(agent: "GoogleADKAgent") -> None:
    print(f"{agent.name} is ready. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Goodbye!")
            break
        if user_input:
            print(f"{agent.name}: {ask(agent, user_input)}")


def main(argv: List[str]) -> None:
    reason = missing_reason()
    if reason:
        print(f"[SETUP] Google Agent Development Kit (ADK) is not ready: {reason}")
        print("[SETUP] Running the rule-based agent from python_basic_agent_without_AI.py instead.\n")
        fallback_main(argv)
        return
    agent = GoogleADKAgent()
    print(f"[SETUP] {agent.name} built with Google Agent Development Kit (ADK), model: {agent.model_name}")
    if "--demo" in argv:
        run_demo(agent)
    else:
        run_interactive(agent)


if __name__ == "__main__":
    main(sys.argv[1:])
