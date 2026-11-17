import pytest

from sql_guard import GuardError, check_select


def test_allowed_select_is_capped():
    out = check_select("SELECT stage, count(*) FROM raw_deals GROUP BY stage;", max_rows=50)
    assert out.endswith("LIMIT 50")
    assert "GROUP BY stage" in out


@pytest.mark.parametrize("bad", [
    "DELETE FROM raw_deals",
    "SELECT 1; DROP TABLE raw_deals",
    "SELECT 1; SELECT 2",
    "WITH x AS (DELETE FROM raw_deals RETURNING *) SELECT * FROM x",
    "SELECT * INTO copy_of_deals FROM raw_deals",
    "SELECT 1 -- hidden",
    "UPDATE raw_deals SET payload = '{}'",
    "",
])
def test_refuses_writes_and_tricks(bad):
    with pytest.raises(GuardError):
        check_select(bad)


def test_keywords_inside_string_literals_are_fine():
    # A value like 'drop;' in a filter is data, not a statement.
    out = check_select("SELECT * FROM raw_deals WHERE payload->>'stage' = 'drop; delete'")
    assert out.startswith("SELECT * FROM (")
