"""Fetch all pages of GitHub issues changed since a date.

Follows the Link header for the next page and retries with a growing wait on
429 and 5xx. The HTTP call is injected (`fetch`) so tests never touch the network.
The token is read from the GITHUB_TOKEN environment variable, never from code.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

NEXT_RE = re.compile(r'<([^>]+)>;\s*rel="next"')


class FetchError(Exception):
    pass


def next_url(link_header):
    """Return the rel="next" URL from a Link header, or None on the last page."""
    if not link_header:
        return None
    m = NEXT_RE.search(link_header)
    return m.group(1) if m else None


def http_fetch(url):
    """Real fetch: returns (status, headers dict, body text)."""
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8")


def get_with_retry(url, fetch=http_fetch, max_tries=5, base_wait=1.0, sleep=time.sleep):
    """GET one page. Retry 429 and 5xx, waiting base, 2*base, 4*base ... seconds."""
    for attempt in range(max_tries):
        status, headers, body = fetch(url)
        if status == 200:
            return headers, body
        if status in (429, 500, 502, 503, 504):
            retry_after = {k.lower(): v for k, v in headers.items()}.get("retry-after")
            wait = float(retry_after) if retry_after else base_wait * (2 ** attempt)
            sleep(wait)
            continue
        raise FetchError(f"{status} for {url}")  # 401, 403, 404: retrying will not help
    raise FetchError(f"gave up after {max_tries} tries for {url}")


def fetch_issues_since(repo, since, per_page=100, fetch=http_fetch, sleep=time.sleep):
    """Return (issues, pages_fetched) for issues updated since `since` (ISO 8601)."""
    url = (f"https://api.github.com/repos/{repo}/issues"
           f"?state=all&per_page={per_page}&since={since}")
    issues, pages = [], 0
    while url:
        headers, body = get_with_retry(url, fetch=fetch, sleep=sleep)
        issues.extend(json.loads(body))
        pages += 1
        url = next_url({k.lower(): v for k, v in headers.items()}.get("link"))
    return issues, pages
