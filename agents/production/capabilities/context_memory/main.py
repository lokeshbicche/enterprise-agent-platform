"""Store a short conversation and approved facts in an in-memory SQLite database."""

import json
import sqlite3
import sys

MAX_HISTORY = 3
MAX_CONTEXT_CHARS = 700


def create_store() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE messages (session_id TEXT, sequence INTEGER, role TEXT, content TEXT, "
        "PRIMARY KEY (session_id, sequence))"
    )
    connection.execute(
        "CREATE TABLE facts (session_id TEXT, fact_key TEXT, fact_value TEXT, "
        "PRIMARY KEY (session_id, fact_key))"
    )
    return connection


def add_message(
    connection: sqlite3.Connection,
    session_id: str,
    sequence: int,
    role: str,
    content: str,
) -> None:
    if role not in {"user", "assistant"}:
        raise ValueError("Only user and assistant messages are allowed.")
    connection.execute(
        "INSERT INTO messages VALUES (?, ?, ?, ?)",
        (session_id, sequence, role, content),
    )


def remember_fact(
    connection: sqlite3.Connection,
    session_id: str,
    key: str,
    value: str,
) -> None:
    connection.execute(
        "INSERT INTO facts VALUES (?, ?, ?) "
        "ON CONFLICT(session_id, fact_key) DO UPDATE SET fact_value = excluded.fact_value",
        (session_id, key, value),
    )


def build_context(connection: sqlite3.Connection, session_id: str) -> str:
    facts = connection.execute(
        "SELECT fact_key, fact_value FROM facts WHERE session_id = ? ORDER BY fact_key",
        (session_id,),
    ).fetchall()
    messages = connection.execute(
        "SELECT role, content FROM messages WHERE session_id = ? "
        "ORDER BY sequence DESC LIMIT ?",
        (session_id, MAX_HISTORY),
    ).fetchall()
    lines = [f"Known user-approved facts: {key}={value}" for key, value in facts]
    lines.extend(f"{role}: {content}" for role, content in reversed(messages))
    return "\n".join(lines)[-MAX_CONTEXT_CHARS:]


def demo() -> dict[str, object]:
    with create_store() as connection:
        remember_fact(connection, "demo-session", "preferred_language", "English")
        for index, content in enumerate(
            ["I am planning a trip.", "I prefer trains.", "Find a quiet hotel.", "Keep it under budget."],
            start=1,
        ):
            add_message(connection, "demo-session", index, "user", content)
        return {
            "session": "demo-session",
            "max_history_messages": MAX_HISTORY,
            "max_context_chars": MAX_CONTEXT_CHARS,
            "context": build_context(connection, "demo-session"),
        }


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo to build a bounded sample context.")
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
