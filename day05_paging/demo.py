import urllib.request
from github_issues import fetch_issues_since, http_fetch

issues, pages = fetch_issues_since(
    "psf/requests", "2026-11-10T00:00:00Z", per_page=3, fetch=http_fetch
)
print("issues:", len(issues), "pages fetched:", pages)
for i in issues[:3]:
    print(i["number"], i["state"], i["updated_at"], i["title"][:60])

req = urllib.request.Request("https://github.com")
with urllib.request.urlopen(req) as r:
    print("rate limit headers:")
    for k, v in r.headers.items():
        if k.lower().startswith("x-ratelimit"):
            print(" ", k, v)

