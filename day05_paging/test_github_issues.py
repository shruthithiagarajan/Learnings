import json

import pytest

import github_issues as gi


def page(items, link=None, status=200, headers=None):
    h = dict(headers or {})
    if link:
        h["Link"] = link
    return status, h, json.dumps(items)


def scripted(responses):
    """A fake fetch that returns the scripted responses in order."""
    calls = []

    def fetch(url):
        calls.append(url)
        return responses[len(calls) - 1]

    fetch.calls = calls
    return fetch


def test_next_url_reads_link_header():
    h = '<https://x/p2>; rel="next", <https://x/p9>; rel="last"'
    assert gi.next_url(h) == "https://x/p2"
    assert gi.next_url('<https://x/p1>; rel="prev"') is None   # last page
    assert gi.next_url(None) is None


def test_follows_pages_until_no_next_link():
    # Proves paging stops when there is no rel="next".
    fetch = scripted([
        page([{"n": 1}, {"n": 2}], link='<https://api/p2>; rel="next"'),
        page([{"n": 3}], link='<https://api/p3>; rel="next"'),
        page([{"n": 4}]),
    ])
    issues, pages = gi.fetch_issues_since("o/r", "2026-09-01T00:00:00Z", fetch=fetch)
    assert [i["n"] for i in issues] == [1, 2, 3, 4]
    assert pages == 3
    assert fetch.calls[0].endswith("since=2026-09-01T00:00:00Z")
    assert fetch.calls[1:] == ["https://api/p2", "https://api/p3"]


def test_retries_429_with_growing_wait_then_succeeds():
    waits = []
    fetch = scripted([(429, {}, "{}"), (503, {}, "{}"), page([{"n": 1}])])
    headers, body = gi.get_with_retry("u", fetch=fetch, base_wait=1, sleep=waits.append)
    assert json.loads(body) == [{"n": 1}]
    assert waits == [1, 2]          # doubles each time


def test_retry_after_header_is_respected():
    waits = []
    fetch = scripted([(429, {"Retry-After": "7"}, "{}"), page([])])
    gi.get_with_retry("u", fetch=fetch, sleep=waits.append)
    assert waits == [7.0]


def test_401_is_not_retried_and_gives_up_after_max_tries():
    fetch = scripted([(401, {}, "{}")])
    with pytest.raises(gi.FetchError):
        gi.get_with_retry("u", fetch=fetch, sleep=lambda s: None)
    assert len(fetch.calls) == 1

    fetch = scripted([(500, {}, "{}")] * 3)
    with pytest.raises(gi.FetchError):
        gi.get_with_retry("u", fetch=fetch, max_tries=3, sleep=lambda s: None)
    assert len(fetch.calls) == 3
