"""A stateless LangChain agent that looks up sample delivery information."""

import sys
from typing import Any


_ORDERS = {
    "ORD-100": "In transit. The estimated delivery is Tuesday.",
    "ORD-200": "Label created. The carrier has not picked up the parcel yet.",
}


def run_agent(question: str) -> None:
    try:
        from langchain.agents import create_agent
        from langchain.tools import tool
    except ImportError as exc:
        raise SystemExit(
            "LangChain is not installed. Run: python -m pip install langchain langchain-openai"
        ) from exc

    @tool
    def lookup_order(order_id: str) -> str:
        """Look up the current delivery status for a sample order ID."""
        status = _ORDERS.get(order_id.strip().upper())
        return status or f"Order {order_id} was not found in the in-memory sample data."

    agent = create_agent(
        model="openai:gpt-4o-mini",
        tools=[lookup_order],
        system_prompt=(
            "You are a concise order-support agent. Use lookup_order for order status. "
            "Only report the status returned by the tool; do not invent tracking details."
        ),
    )
    result: Any = agent.invoke({"messages": [{"role": "user", "content": question}]})
    for message in reversed(result["messages"]):
        if getattr(message, "type", None) == "ai" and message.content:
            print(message.content)
            return
    print("The agent returned no text response.")


def main() -> None:
    if "--demo" in sys.argv[1:]:
        question = "Where is order ORD-100?"
    else:
        question = input("Ask about a sample order: ").strip()
    run_agent(question)


if __name__ == "__main__":
    main()
