"""
python_basic_agent_agentsdk_smolagents.py - Basic agent built with the Hugging Face smolagents AGENT SDK.

AGENT SDK = a framework that runs the agent loop for you. In python_basic_agent_without_AI.py
and the python_basic_agent_modelsdk_*.py files we wrote PERCEIVE -> THINK -> ACT -> OBSERVE ->
RESPOND ourselves. Here the Hugging Face smolagents does THINK -> ACT -> OBSERVE (the tool-calling loop)
and memory internally: we only give it a model, instructions and plain Python functions as tools.
Only the SmolAgentsAgent class below is framework-specific; compare any two
python_basic_agent_agentsdk_*.py files to see how agent SDKs differ.

Install:
    pip install "smolagents[openai]"

Setup (environment variables):
    OpenAI:  OPENAI_API_KEY=sk-...   (optional: OPENAI_MODEL, default gpt-4o-mini)
    Ollama (free, local, no key):  OPENAI_BASE_URL=http://localhost:11434/v1  OPENAI_MODEL=llama3.2
    If the SDK is not installed or not configured, this file runs the rule-based agent from
    python_basic_agent_without_AI.py instead, so it always runs (keep both files in the same folder).

Run:
    python python_basic_agent_agentsdk_smolagents.py          # interactive chat mode
    python python_basic_agent_agentsdk_smolagents.py --demo   # run a scripted demo and exit

Requires: Python 3.10+ and the packages above.
"""

import os
import sys
from typing import Dict, List

from python_basic_agent_without_AI import calculator_tool, reverse_text_tool, time_tool, word_count_tool
from python_basic_agent_without_AI import main as fallback_main

try:
    import smolagents
    from smolagents import ToolCallingAgent, tool
except ImportError:
    smolagents = None

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("OPENAI_BASE_URL") or None  # e.g. http://localhost:11434/v1 for Ollama

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
    if smolagents is None:
        return 'pip install "smolagents[openai]"'
    if not (API_KEY or BASE_URL):
        return "set OPENAI_API_KEY (or OPENAI_BASE_URL for a local Ollama server)"
    return ""


class SmolAgentsAgent:
    """Agent built with smolagents: ToolCallingAgent finishes by calling its final_answer tool."""

    def __init__(self) -> None:
        self.name = "smolagents-Agent"
        self.model_name = MODEL
        model_cls = getattr(smolagents, "OpenAIModel", None) or smolagents.OpenAIServerModel  # renamed in 1.2x
        model = model_cls(model_id=MODEL, api_base=BASE_URL, api_key=API_KEY or "none")
        self.agent = ToolCallingAgent(tools=[tool(func) for func in TOOLS], model=model, instructions=INSTRUCTIONS,
                                      max_steps=5, verbosity_level=0)  # 0 = quiet; try 2 to watch every step

    def run(self, user_input: str) -> str:
        return str(self.agent.run(user_input, reset=False))  # reset=False keeps memory between turns


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


def ask(agent: "SmolAgentsAgent", user_input: str) -> str:
    try:
        return agent.run(user_input)
    except Exception as exc:  # network/API problems must not crash the program
        return f"Error from the agent SDK: {exc}"


def run_demo(agent: "SmolAgentsAgent") -> None:
    for goal in DEMO_GOALS:
        print(f"\nYou: {goal}")
        print(f"{agent.name}: {ask(agent, goal)}")
        print("-" * 70)
    print(f"Facts stored by the remember tool: {FACTS}")


def run_interactive(agent: "SmolAgentsAgent") -> None:
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
        print(f"[SETUP] Hugging Face smolagents is not ready: {reason}")
        print("[SETUP] Running the rule-based agent from python_basic_agent_without_AI.py instead.\n")
        fallback_main(argv)
        return
    agent = SmolAgentsAgent()
    print(f"[SETUP] {agent.name} built with Hugging Face smolagents, model: {agent.model_name}")
    if "--demo" in argv:
        run_demo(agent)
    else:
        run_interactive(agent)


if __name__ == "__main__":
    main(sys.argv[1:])
