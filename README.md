# enterprise-agent-platform

A basic AI agent written in **plain Python** (standard library only, no AI frameworks) to understand how an agent works.

## The agent loop

```
PERCEIVE -> THINK -> ACT -> OBSERVE -> REMEMBER -> RESPOND
```

| Step     | Method in `basic_agent.py` | What it does                                            |
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
python basic_agent.py           # interactive chat
python basic_agent.py --demo    # scripted demo
python -m unittest -v           # tests
```

Example prompts: `calculate (12 + 8) * 3`, `remember my name is Bicche`, `what is my name`,
`what time is it and then calculate 2 ^ 10`, `count words in cats and dogs`, `reverse hello`.

## Extend it

```python
from basic_agent import BasicAgent, Tool

agent = BasicAgent()
agent.register_tool(Tool("upper", "Uppercase text", lambda text: text.upper()))
```
Then add a rule for it in `BasicAgent._choose_tool()`.
