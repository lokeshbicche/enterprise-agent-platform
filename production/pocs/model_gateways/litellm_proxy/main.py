"""Call a model alias through the local LiteLLM Proxy."""

import os
import sys

from openai import OpenAI


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit(
            'Usage: python -m agents.production.pocs.model_gateways.litellm_proxy.main "Your question"'
        )

    client = OpenAI(
        base_url=os.environ.get("LITELLM_BASE_URL", "http://localhost:4000/v1"),
        api_key=os.environ["LITELLM_API_KEY"],
        timeout=30,
        max_retries=1,
    )
    response = client.chat.completions.create(
        model="enterprise-chat",
        messages=[{"role": "user", "content": question}],
        max_tokens=300,
    )
    print(response.choices[0].message.content or "")


if __name__ == "__main__":
    main()
