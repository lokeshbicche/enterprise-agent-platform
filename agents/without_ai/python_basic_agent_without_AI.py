"""
python_basic_agent_without_AI.py - A simple, framework-free AI agent written in plain Python.

What is an agent?
    An agent is a program that repeatedly:
        1. PERCEIVES  - receives input (a goal / user message) from its environment
        2. THINKS     - decides what to do next (plans which tool to use)
        3. ACTS       - executes an action (calls a tool)
        4. OBSERVES   - looks at the result of that action
        5. REMEMBERS  - stores what happened so later decisions can use it
    ...until the goal is achieved, then it RESPONDS.

    Real-world agents use a Large Language Model (LLM) for the "THINK" step.
    Here the "brain" is a simple rule-based planner so you can see the agent
    loop clearly, with no external libraries, API keys, or AI frameworks.

Run:
    python -m agents.without_ai.python_basic_agent_without_AI          # interactive chat mode
    python -m agents.without_ai.python_basic_agent_without_AI --demo   # run a scripted demo and exit

Requires: Python 3.8+ (standard library only).
"""

import ast
import operator
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# 1. TOOLS - the actions an agent is able to perform
# ---------------------------------------------------------------------------

@dataclass
class Tool:
    """A capability the agent can use. Each tool takes a string and returns a string."""

    name: str
    description: str
    func: Callable[[str], str]

    def run(self, tool_input: str) -> str:
        try:
            return self.func(tool_input)
        except Exception as exc:  # a tool failure must never crash the agent
            return f"Error while running tool '{self.name}': {exc}"


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float:
    """Evaluate a math expression tree safely (no use of Python's eval())."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("only numbers and + - * / // % ** ( ) are allowed")


def calculator_tool(expression: str) -> str:
    expression = expression.replace("^", "**").strip()
    if not expression:
        return "Please give me a math expression, e.g. 'calculate 12 * (3 + 4)'."
    result = _safe_eval(ast.parse(expression, mode="eval"))
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return f"{expression} = {result}"


def time_tool(_: str) -> str:
    return "The current date and time is " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def word_count_tool(text: str) -> str:
    words = text.split()
    return f"The text has {len(words)} word(s) and {len(text)} character(s)."


def reverse_text_tool(text: str) -> str:
    return f"Reversed text: {text[::-1]}"


# ---------------------------------------------------------------------------
# 2. MEMORY - what the agent remembers between steps and conversations
# ---------------------------------------------------------------------------

@dataclass
class Memory:
    """Short-term memory (conversation history) + long-term memory (facts)."""

    history: List[Dict[str, str]] = field(default_factory=list)
    facts: Dict[str, str] = field(default_factory=dict)

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def remember(self, key: str, value: str) -> None:
        self.facts[key.strip().lower()] = value.strip()

    def recall(self, key: str) -> Optional[str]:
        return self.facts.get(key.strip().lower())


# ---------------------------------------------------------------------------
# 3. PLAN - the decision the agent makes in the THINK step
# ---------------------------------------------------------------------------

@dataclass
class Step:
    """One planned action: which tool to call and with what input."""

    tool_name: str
    tool_input: str
    reason: str


# ---------------------------------------------------------------------------
# 4. THE AGENT - perceive -> think -> act -> observe -> remember -> respond
# ---------------------------------------------------------------------------

# Split "A and B" / "A then B" / "A; B" into sub-tasks, but only when the next
# part starts with a command word (so "count words in cats and dogs" stays whole).
_COMMAND_WORDS = r"(?:calculate|compute|solve|what|who|remember|recall|count|how many|word count|reverse|help)\b"
_TASK_SEPARATOR = r"\s*;\s*|\s+(?:and then|then|and)\s+(?=" + _COMMAND_WORDS + r")"


class BasicAgent:
    def __init__(self, name: str = "BasicAgent", verbose: bool = True, max_steps: int = 5):
        self.name = name
        self.verbose = verbose
        self.max_steps = max_steps  # safety guard: an agent loop must always terminate
        self.memory = Memory()
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()

    # ----- tool registry --------------------------------------------------

    def register_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def _register_default_tools(self) -> None:
        self.register_tool(Tool("calculator", "Evaluate a math expression", calculator_tool))
        self.register_tool(Tool("time", "Get the current date and time", time_tool))
        self.register_tool(Tool("word_count", "Count words in a text", word_count_tool))
        self.register_tool(Tool("reverse", "Reverse a piece of text", reverse_text_tool))
        self.register_tool(Tool("remember", "Store a fact: 'remember <key> is <value>'", self._remember_tool))
        self.register_tool(Tool("recall", "Recall a stored fact: 'what is <key>'", self._recall_tool))
        self.register_tool(Tool("help", "List what the agent can do", self._help_tool))

    def _remember_tool(self, text: str) -> str:
        match = re.match(r"(?:my\s+)?(.+?)\s+(?:is|=|are)\s+(.+)", text, re.IGNORECASE)
        if not match:
            return "Use the format: remember <thing> is <value>"
        key, value = match.group(1), match.group(2)
        self.memory.remember(key, value)
        return f"Got it. I will remember that {key.strip()} is {value.strip()}."

    def _recall_tool(self, key: str) -> str:
        value = self.memory.recall(key)
        if value is None:
            return f"I don't know what {key.strip()} is yet. Teach me with 'remember {key.strip()} is ...'."
        return f"{key.strip()} is {value}."

    def _help_tool(self, _: str) -> str:
        lines = ["I can use these tools:"]
        lines += [f"  - {t.name}: {t.description}" for t in self.tools.values()]
        lines.append("Combine tasks with 'and' / 'then', e.g. 'calculate 2+3 and what time is it'.")
        return "\n".join(lines)

    # ----- the agent loop --------------------------------------------------

    def log(self, message: str) -> None:
        if self.verbose:
            print(message)

    def perceive(self, user_input: str) -> str:
        """PERCEIVE: take input from the environment and store it in memory."""
        user_input = user_input.strip()
        self.memory.add("user", user_input)
        self.log(f"\n[PERCEIVE] Goal received: {user_input!r}")
        return user_input

    def think(self, goal: str) -> List[Step]:
        """THINK: break the goal into sub-tasks and pick a tool for each one.

        In an LLM-powered agent, this is where the model would reason. Here we
        use simple keyword rules so the decision process is easy to follow.
        """
        sub_tasks = [t.strip() for t in re.split(_TASK_SEPARATOR, goal, flags=re.IGNORECASE) if t.strip()]
        plan = [self._choose_tool(task) for task in sub_tasks]
        plan = plan[: self.max_steps]
        self.log(f"[THINK]    Planned {len(plan)} step(s):")
        for i, step in enumerate(plan, 1):
            self.log(f"           {i}. use '{step.tool_name}' with input {step.tool_input!r} -> {step.reason}")
        return plan

    def _choose_tool(self, task: str) -> Step:
        lower = task.lower()

        if lower in {"help", "?"} or "what can you do" in lower:
            return Step("help", "", "user asked for help")

        match = re.match(r"remember\s+(?:that\s+)?(.+)", task, re.IGNORECASE)
        if match:
            return Step("remember", match.group(1), "user wants me to store a fact")

        if re.search(r"\b(time|date|today)\b", lower):
            return Step("time", "", "task mentions time/date")

        match = re.match(r"(?:calculate|compute|solve|what is|what's)\s+([\d\s.+\-*/%^()]+)\??$", task, re.IGNORECASE)
        if match and re.search(r"\d", match.group(1)):
            return Step("calculator", match.group(1).strip(), "task is a math expression")
        if re.fullmatch(r"[\d\s.+\-*/%^()]+", task) and re.search(r"\d\s*[+\-*/%^]", task):
            return Step("calculator", task, "input looks like a math expression")

        match = re.match(r"(?:count words in|word count of|how many words in)\s+(.+)", task, re.IGNORECASE)
        if match:
            return Step("word_count", match.group(1).strip("'\" "), "user wants a word count")

        match = re.match(r"reverse\s+(.+)", task, re.IGNORECASE)
        if match:
            return Step("reverse", match.group(1).strip("'\" "), "user wants text reversed")

        match = re.match(r"(?:what is|what's|who is|recall)\s+(?:my\s+)?(.+?)\??$", task, re.IGNORECASE)
        if match:
            return Step("recall", match.group(1), "user is asking about a stored fact")

        return Step("unknown", task, "no tool matches this task")

    def act(self, step: Step) -> str:
        """ACT: execute the chosen tool."""
        tool = self.tools.get(step.tool_name)
        if tool is None:
            self.log("[ACT]      No suitable tool found")
            return f"Sorry, I don't know how to '{step.tool_input}' yet. Type 'help' to see what I can do."
        self.log(f"[ACT]      Running tool '{tool.name}'")
        return tool.run(step.tool_input)

    def observe(self, step: Step, result: str) -> None:
        """OBSERVE + REMEMBER: record the result so the agent can learn from it."""
        self.memory.add("tool", f"{step.tool_name}: {result}")
        self.log(f"[OBSERVE]  {result}")

    def respond(self, results: List[str]) -> str:
        """RESPOND: combine all observations into a final answer."""
        answer = "\n".join(results) if results else "I had nothing to do."
        self.memory.add("agent", answer)
        return answer

    def run(self, user_input: str) -> str:
        """Run one full agent cycle for a single user goal."""
        goal = self.perceive(user_input)
        if not goal:
            return "Please tell me what you want me to do. Type 'help' for options."
        plan = self.think(goal)
        results = []
        for step in plan:
            result = self.act(step)
            self.observe(step, result)
            results.append(result)
        return self.respond(results)


# ---------------------------------------------------------------------------
# 5. ENTRY POINTS
# ---------------------------------------------------------------------------

def run_demo() -> None:
    agent = BasicAgent()
    demo_goals = [
        "help",
        "calculate (12 + 8) * 3",
        "remember my name is Bicche",
        "what is my name",
        "what time is it and then calculate 2 ^ 10",
        "count words in agents perceive think act and observe",
        "reverse hello agent",
        "calculate 10 / 0",
        "sing me a song",
    ]
    for goal in demo_goals:
        answer = agent.run(goal)
        print(f"[RESPOND]  {agent.name}: {answer}")
        print("-" * 70)
    print(f"Memory facts stored: {agent.memory.facts}")
    print(f"History entries: {len(agent.memory.history)}")


def run_interactive() -> None:
    agent = BasicAgent()
    print(f"{agent.name} is ready. Type 'help' to see what I can do, or 'exit' to quit.")
    while True:
        try:
            user_input = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_input.strip().lower() in {"exit", "quit", "bye"}:
            print("Goodbye!")
            break
        answer = agent.run(user_input)
        print(f"{agent.name}: {answer}")


def main(argv: List[str]) -> None:
    if "--demo" in argv:
        run_demo()
    else:
        run_interactive()


if __name__ == "__main__":
    main(sys.argv[1:])
