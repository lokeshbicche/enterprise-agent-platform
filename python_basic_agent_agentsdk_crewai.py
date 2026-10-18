"""
python_basic_agent_agentsdk_crewai.py - Basic agent built with the CrewAI AGENT SDK.

AGENT SDK = a framework that runs the agent loop for you. In python_basic_agent_without_AI.py
and the python_basic_agent_modelsdk_*.py files we wrote PERCEIVE -> THINK -> ACT -> OBSERVE ->
RESPOND ourselves. Here the CrewAI does THINK -> ACT -> OBSERVE (the tool-calling loop)
and memory internally: we only give it a model, instructions and plain Python functions as tools.
Only the CrewAIAgent class below is framework-specific; compare any two
python_basic_agent_agentsdk_*.py files to see how agent SDKs differ.

Install:
    pip install crewai

Setup (environment variables):
    OpenAI:  OPENAI_API_KEY=sk-...   (optional: OPENAI_MODEL, default gpt-4o-mini)
    Ollama (free, local, no key):  OPENAI_BASE_URL=http://localhost:11434/v1  OPENAI_MODEL=llama3.2
    If the SDK is not installed or not configured, this file runs the rule-based agent from
    python_basic_agent_without_AI.py instead, so it always runs (keep both files in the same folder).

Run:
    python python_basic_agent_agentsdk_crewai.py          # interactive chat mode
    python python_basic_agent_agentsdk_crewai.py --demo   # run a scripted demo and exit

Requires: Python 3.10+ and the packages above.
"""

import os
import sys
from typing import Dict, List

from python_basic_agent_without_AI import calculator_tool, reverse_text_tool, time_tool, word_count_tool
from python_basic_agent_without_AI import main as fallback_main

os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
try:
    from crewai import LLM, Agent, Crew, Task
    from crewai.tools import tool
except ImportError:
    Crew = None

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
    if Crew is None:
        return 'pip install crewai'
    if not (API_KEY or BASE_URL):
        return "set OPENAI_API_KEY (or OPENAI_BASE_URL for a local Ollama server)"
    return ""


class CrewAIAgent:
    """Agent built with CrewAI: an Agent (role/goal/backstory) does a Task inside a Crew."""

    def __init__(self) -> None:
        self.name = "CrewAI-Agent"
        self.model_name = MODEL
        llm = LLM(model=f"openai/{MODEL}", api_key=API_KEY or "none", base_url=BASE_URL, temperature=0)
        self.agent = Agent(role="Helpful assistant", goal="Answer the user's request using the tools",
                           backstory=INSTRUCTIONS, tools=[tool(func) for func in TOOLS], llm=llm, verbose=False)
        self.history: List[str] = []  # CrewAI tasks are one-shot, so we pass recent history ourselves

    def run(self, user_input: str) -> str:
        context = "\n".join(self.history[-6:]) or "(none)"
        task = Task(description=f"Conversation so far:\n{context}\n\nUser request: {user_input}",
                    expected_output="A short, direct answer for the user.", agent=self.agent)
        answer = str(Crew(agents=[self.agent], tasks=[task], verbose=False).kickoff().raw)
        self.history += [f"User: {user_input}", f"Agent: {answer}"]
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


def ask(agent: "CrewAIAgent", user_input: str) -> str:
    try:
        return agent.run(user_input)
    except Exception as exc:  # network/API problems must not crash the program
        return f"Error from the agent SDK: {exc}"


def run_demo(agent: "CrewAIAgent") -> None:
    for goal in DEMO_GOALS:
        print(f"\nYou: {goal}")
        print(f"{agent.name}: {ask(agent, goal)}")
        print("-" * 70)
    print(f"Facts stored by the remember tool: {FACTS}")


def run_interactive(agent: "CrewAIAgent") -> None:
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
        print(f"[SETUP] CrewAI is not ready: {reason}")
        print("[SETUP] Running the rule-based agent from python_basic_agent_without_AI.py instead.\n")
        fallback_main(argv)
        return
    agent = CrewAIAgent()
    print(f"[SETUP] {agent.name} built with CrewAI, model: {agent.model_name}")
    if "--demo" in argv:
        run_demo(agent)
    else:
        run_interactive(agent)


if __name__ == "__main__":
    main(sys.argv[1:])
