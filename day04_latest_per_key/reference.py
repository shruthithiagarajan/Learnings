"""Pure-Python reference answers for the Day 4 deals, to check the SQL against."""
import json


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def latest_version_rows(rows):
    """Per deal, the rows that share the newest last_modified (one version)."""
    newest = {}
    for r in rows:
        d = r["deal_id"]
        if d not in newest or r["last_modified"] > newest[d]:
            newest[d] = r["last_modified"]
    return [r for r in rows if r["last_modified"] == newest[r["deal_id"]]]


def latest_stage(rows):
    """Newest last_modified wins; on a tie the row that appears later wins."""
    best = {}
    for r in rows:
        d = r["deal_id"]
        if d not in best or r["last_modified"] >= best[d]["last_modified"]:
            best[d] = r
    return {d: r["stage"] for d, r in best.items()}


def deal_values(rows):
    out = {}
    for r in latest_version_rows(rows):
        out[r["deal_id"]] = out.get(r["deal_id"], 0) + r["price"] * r["qty"]
    return out
