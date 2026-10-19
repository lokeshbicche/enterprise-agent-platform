"""Demonstrate simple request validation, tool allowlisting, and output scanning."""

import json
import re
import sys
from dataclasses import dataclass

MAX_INPUT_CHARS = 2_000
ALLOWED_TOOLS = frozenset({"catalog_search", "faq_lookup"})
DEMO_SECRET = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str
    sanitized_output: str | None = None


def validate_request(text: str) -> GuardrailResult:
    if not text.strip():
        return GuardrailResult(False, "empty_input")
    if len(text) > MAX_INPUT_CHARS:
        return GuardrailResult(False, "input_too_long")
    return GuardrailResult(True, "accepted")


def authorize_tool(tool_name: str, allowed_tools: frozenset[str] = ALLOWED_TOOLS) -> GuardrailResult:
    if tool_name not in allowed_tools:
        return GuardrailResult(False, "tool_not_allowlisted")
    return GuardrailResult(True, "tool_allowed")


def inspect_output(text: str) -> GuardrailResult:
    redacted = DEMO_SECRET.sub("[REDACTED DEMO SECRET]", text)
    if redacted != text:
        return GuardrailResult(False, "demo_secret_pattern", redacted)
    return GuardrailResult(True, "output_passed", text)


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo to see request, tool, and output checks.")
    results = {
        "valid_request": validate_request("Look up our return policy."),
        "unknown_tool": authorize_tool("execute_shell"),
        "unsafe_output": inspect_output("Do not expose sk-demoCredential123456."),
    }
    print(
        json.dumps(
            {name: result.__dict__ for name, result in results.items()},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
