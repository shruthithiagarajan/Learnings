"""A guard for the run_sql tool: one read-only SELECT, with a row cap.

This is the first of two layers. The second is a database user that only has
SELECT rights; the guard is not enough on its own because text checks can miss
things.
"""
import re

FORBIDDEN = {
    "insert", "update", "delete", "drop", "alter", "create", "truncate", "grant",
    "revoke", "copy", "call", "do", "merge", "vacuum", "set", "reset", "execute",
    "into", "lock", "pg_sleep", "pg_read_file", "dblink",
}
STRING_RE = re.compile(r"'(?:[^']|'')*'")     # single-quoted literals ('' is an escaped quote)
WORD_RE = re.compile(r"[a-z_][a-z0-9_]*")


class GuardError(ValueError):
    pass


def check_select(query, max_rows=100):
    """Return a safe query string, or raise GuardError."""
    q = (query or "").strip()
    if not q:
        raise GuardError("empty query")
    if q.endswith(";"):
        q = q[:-1].rstrip()

    code = STRING_RE.sub("''", q)               # ignore text inside string literals
    if "--" in code or "/*" in code:
        raise GuardError("comments are not allowed")
    if ";" in code:
        raise GuardError("only one statement is allowed")

    lowered = code.lower()
    if not re.match(r"\s*(select|with)\b", lowered):
        raise GuardError("only SELECT queries are allowed")
    bad = FORBIDDEN & set(WORD_RE.findall(lowered))
    if bad:
        raise GuardError(f"not allowed: {', '.join(sorted(bad))}")
    if re.search(r"\bfor\s+(update|share|no\s+key\s+update)\b", lowered):
        raise GuardError("row locking is not allowed")

    # Cap the rows no matter what LIMIT the model wrote.
    return f"SELECT * FROM ({q}) AS guarded LIMIT {int(max_rows)}"
