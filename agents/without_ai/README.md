# Agent Without AI

A framework-free, rule-based agent written in Python's standard library. It demonstrates the agent loop:

```text
PERCEIVE -> THINK -> ACT -> OBSERVE -> REMEMBER -> RESPOND
```

The planner selects tools using rules; no LLM, API key, or extra package is needed.

## Run

From the repository root:

```powershell
python -m agents.without_ai.python_basic_agent_without_AI
python -m agents.without_ai.python_basic_agent_without_AI --demo
```

The example includes `calculator`, `time`, `word_count`, `reverse`, `remember`, `recall`, and `help` tools. See [the implementation](python_basic_agent_without_AI.py).

## Tests

Run the tests from the repository root:

```powershell
python -m unittest discover -s agents/without_ai -v
```
