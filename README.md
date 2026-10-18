# enterprise-agent-platform

A basic AI agent written in **plain Python** (standard library only, no AI frameworks) to understand how an agent works.

## The agent loop

```
PERCEIVE -> THINK -> ACT -> OBSERVE -> REMEMBER -> RESPOND
```

| Step     | Method in `python_basic_agent_without_AI.py` | What it does                                            |
|----------|----------------------------|---------------------------------------------------------|
| Perceive | `BasicAgent.perceive()`    | Receives the user goal and stores it in memory          |
| Think    | `BasicAgent.think()`       | Splits the goal into sub-tasks and picks a tool for each |
| Act      | `BasicAgent.act()`         | Runs the chosen tool                                    |
| Observe  | `BasicAgent.observe()`     | Records the tool result in memory                       |
| Respond  | `BasicAgent.respond()`     | Combines results into the final answer                  |

Tools: `calculator`, `time`, `word_count`, `reverse`, `remember`, `recall`, `help`.
In a production agent the `think()` step would call an LLM; here it is rule-based so the flow is easy to follow.

## Run (Python 3.8+)

```bash
python python_basic_agent_without_AI.py           # interactive chat
python python_basic_agent_without_AI.py --demo    # scripted demo
python -m unittest -v           # tests
```

Example prompts: `calculate (12 + 8) * 3`, `remember my name is Bicche`, `what is my name`,
`what time is it and then calculate 2 ^ 10`, `count words in cats and dogs`, `reverse hello`.

## Extend it

```python
from python_basic_agent_without_AI import BasicAgent, Tool

agent = BasicAgent()
agent.register_tool(Tool("upper", "Uppercase text", lambda text: text.upper()))
```
Then add a rule for it in `BasicAgent._choose_tool()`.

## With AI: raw HTTP vs SDK

Same agent, same tools — **only the THINK step changes**: the goal and tool list are sent to an LLM,
which returns the plan as JSON. Two versions, identical except for `call_llm()`:

| File | How it calls the LLM | Install |
|------|----------------------|---------|
| `python_basic_agent_with_AI_rawhttp.py` | Raw HTTP with built-in `urllib` (you build URL, headers, JSON) | nothing |
| `python_basic_agent_with_AI_sdk.py` | Official OpenAI SDK (`client.chat.completions.create`) | `pip install openai` |

Compare any two files in VS Code: select both → right-click → *Compare Selected*.

```powershell
# OpenAI (cloud, needs key)
$env:LLM_API_KEY="sk-..."                                   # optional: $env:LLM_MODEL (default gpt-4o-mini)
# or Ollama (local, free, no key)
$env:LLM_BASE_URL="http://localhost:11434/v1"; $env:LLM_MODEL="llama3.2"

python python_basic_agent_with_AI_rawhttp.py --demo
python python_basic_agent_with_AI_sdk.py --demo
```
Without a key/server (or without the SDK installed) both fall back to the rule-based planner, so they always run.
