import json
import sqlite3
from pathlib import Path

import reference

DATA = Path(__file__).parent / "deals.ndjson"


def rows():
    return reference.load(DATA)


def test_row_and_deal_counts():
    r = rows()
    assert len(r) == 12
    assert len({x["deal_id"] for x in r}) == 4


def test_latest_stage_and_tie_break():
    # D-1004 has two versions with the same last_modified; the later row wins.
    assert reference.latest_stage(rows()) == {
        "D-1001": "Closed Won",
        "D-1002": "Quotation",
        "D-1003": "Closed Won",
        "D-1004": "Closed Lost",
    }


def test_deal_values_use_latest_version_only():
    # D-1001: 1200*2 + 5400 = 7800 (not the sum of all three versions).
    assert reference.deal_values(rows()) == {
        "D-1001": 7800,
        "D-1002": 1200 + 800 * 3 + 5400,
        "D-1003": 750 * 10 * 2,   # the duplicated line is a real second line here
        "D-1004": 1200 * 4 * 2,
    }


def test_right_vs_wrong_closed_won_count():
    r = rows()
    wrong = sum(1 for x in r if x["stage"] == "Closed Won")
    right = sum(1 for s in reference.latest_stage(r).values() if s == "Closed Won")
    assert (wrong, right) == (4, 2)


def test_sql_window_query_matches_reference():
    # Same ROW_NUMBER query as queries.sql Q3, run on sqlite (json_extract instead
    # of ->>) so it can be checked without a Postgres server.
    con = sqlite3.connect(":memory:")
    con.execute("create table raw_deals (id integer primary key, payload text)")
    for line in DATA.read_text().splitlines():
        con.execute("insert into raw_deals (payload) values (?)", (line,))
    got = dict(con.execute("""
        select deal_id, stage from (
          select json_extract(payload,'$.deal_id') deal_id,
                 json_extract(payload,'$.stage') stage,
                 row_number() over (
                   partition by json_extract(payload,'$.deal_id')
                   order by json_extract(payload,'$.last_modified') desc, id desc) rn
          from raw_deals) where rn = 1""").fetchall())
    assert got == reference.latest_stage(rows())
