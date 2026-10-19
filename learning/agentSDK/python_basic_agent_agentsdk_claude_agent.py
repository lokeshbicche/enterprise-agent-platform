"""
python_basic_agent_agentsdk_claude_agent.py - Basic agent built with the Claude Agent SDK AGENT SDK.

AGENT SDK = a framework that runs the agent loop for you. In python_basic_agent_without_AI.py
and the python_basic_agent_modelsdk_*.py files we wrote PERCEIVE -> THINK -> ACT -> OBSERVE ->
RESPOND ourselves. Here the Claude Agent SDK does THINK -> ACT -> OBSERVE (the tool-calling loop)
and memory internally: we only give it a model, instructions and plain Python functions as tools.
Only the ClaudeAgentSDKAgent class below is framework-specific; compare any two
python_basic_agent_agentsdk_*.py files to see how agent SDKs differ.

Install:
    pip install claude-agent-sdk

Setup (environment variables):
    ANTHROPIC_API_KEY=sk-ant-...   (optional: ANTHROPIC_MODEL, default claude-haiku-4-5)
    The SDK runs the Claude Code CLI under the hood (bundled with the pip package).
    If the SDK is not installed or not configured, this file runs the rule-based agent from
    the no-AI agent instead, so it always runs.

Run:
    python -m agents.with_agent_sdk.python_basic_agent_agentsdk_claude_agent          # interactive chat mode
    python -m agents.with_agent_sdk.python_basic_agent_agentsdk_claude_agent --demo   # run a scripted demo and exit

Requires: Python 3.10+ and the packages above.
"""

import asyncio
import os
import sys
from typing import Dict, List

from agents.without_ai.python_basic_agent_without_AI import calculator_tool, reverse_text_tool, time_tool, word_count_tool
from agents.without_ai.python_basic_agent_without_AI import main as fallback_main

try:
    from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, TextBlock,
                                  create_sdk_mcp_server, tool)
except ImportError:
    ClaudeSDKClient = None

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

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
    if ClaudeSDKClient is None:
        return 'pip install claude-agent-sdk'
    return "" if API_KEY else "set ANTHROPIC_API_KEY"


class ClaudeAgentSDKAgent:
    """Agent built with the Claude Agent SDK: tools are served to Claude as an in-process MCP server."""

    def __init__(self) -> None:
        self.name = "ClaudeAgentSDK-Agent"
        self.model_name = MODEL
        sdk_tools = [self._wrap(func) for func in TOOLS]
        server = create_sdk_mcp_server(name="basic", version="1.0.0", tools=sdk_tools)
        options = ClaudeAgentOptions(
            model=MODEL,
            system_prompt=INSTRUCTIONS,
            mcp_servers={"basic": server},
            tools=[],  # turn off Claude Code's built-in tools (files, shell, ...) - only ours
            allowed_tools=[f"mcp__basic__{func.__name__}" for func in TOOLS],
            max_turns=6,
        )
        self.loop = asyncio.new_event_loop()  # one loop keeps the CLI session (memory) alive
        self.client = ClaudeSDKClient(options=options)
        self.loop.run_until_complete(self.client.connect())

    @staticmethod
    def _wrap(func):
        """Turn a plain function into a Claude SDK tool (async, dict in -> MCP content out)."""
        params = {name: str for name in func.__code__.co_varnames[: func.__code__.co_argcount]}

        async def handler(args: dict) -> dict:
            return {"content": [{"type": "text", "text": func(**args)}]}

        return tool(func.__name__, (func.__doc__ or "").strip().splitlines()[0], params)(handler)

    async def _ask(self, user_input: str) -> str:
        await self.client.query(user_input)
        texts = []
        async for message in self.client.receive_response():
            if isinstance(message, AssistantMessage):
                texts += [block.text for block in message.content if isinstance(block, TextBlock)]
        return texts[-1] if texts else ""

    def run(self, user_input: str) -> str:
        return self.loop.run_until_complete(self._ask(user_input))


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


def ask(agent: "ClaudeAgentSDKAgent", user_input: str) -> str:
    try:
        return agent.run(user_input)
    except Exception as exc:  # network/API problems must not crash the program
        return f"Error from the agent SDK: {exc}"


def run_demo(agent: "ClaudeAgentSDKAgent") -> None:
    for goal in DEMO_GOALS:
        print(f"\nYou: {goal}")
        print(f"{agent.name}: {ask(agent, goal)}")
        print("-" * 70)
    print(f"Facts stored by the remember tool: {FACTS}")


def run_interactive(agent: "ClaudeAgentSDKAgent") -> None:
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
        print(f"[SETUP] Claude Agent SDK is not ready: {reason}")
        print("[SETUP] Running the rule-based agent instead.\n")
        fallback_main(argv)
        return
    agent = ClaudeAgentSDKAgent()
    print(f"[SETUP] {agent.name} built with Claude Agent SDK, model: {agent.model_name}")
    if "--demo" in argv:
        run_demo(agent)
    else:
        run_interactive(agent)


if __name__ == "__main__":
    main(sys.argv[1:])
