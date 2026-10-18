"""Call OpenRouter using its OpenAI-compatible chat completions API."""

import os
import sys

from openai import OpenAI


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit(
            'Usage: python -m agents.production.pocs.model_gateways.openrouter.main "Your question"'
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        timeout=30,
        max_retries=1,
    )
    response = client.chat.completions.create(
        model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        messages=[{"role": "user", "content": question}],
        max_tokens=300,
    )
    print(response.choices[0].message.content or "")


if __name__ == "__main__":
    main()
