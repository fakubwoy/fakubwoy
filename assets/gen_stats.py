"""Builds assets/stats.svg from GitHub's GraphQL API. Runs daily in Actions with the built-in GITHUB_TOKEN.
Contribution totals include private work because the profile shows private contributions publicly."""
import json, os, urllib.request

USER = "fakubwoy"
Q = """query($u:String!){ user(login:$u){
  contributionsCollection{ contributionCalendar{ totalContributions }
    totalCommitContributions restrictedContributionsCount totalPullRequestContributions totalPullRequestReviewContributions }
  pullRequests(states:MERGED){ totalCount }
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){ totalCount nodes{ stargazerCount } }
}}"""


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "User-Agent": USER})
    return json.load(urllib.request.urlopen(req))["data"]["user"]


def render(u):
    c = u["contributionsCollection"]
    rows = [
        ("Contributions, last 12 months (incl. private)", c["contributionCalendar"]["totalContributions"]),
        ("Merged PRs in public repos", u["pullRequests"]["totalCount"]),
        ("Public repos", u["repositories"]["totalCount"]),
        ("Stars on my public repos", sum(n["stargazerCount"] for n in u["repositories"]["nodes"])),
    ]
    h = 46 + 28 * len(rows)
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="{h}" viewBox="0 0 420 {h}">',
             '<style>.t{font:600 17px Segoe UI,Ubuntu,sans-serif;fill:#58a6ff}.l{font:400 14px Segoe UI,Ubuntu,sans-serif;fill:#c9d1d9}.v{font:700 14px Segoe UI,Ubuntu,sans-serif;fill:#e6edf3}</style>',
             f'<rect width="420" height="{h}" rx="6" fill="#0d1117"/>',
             '<text x="22" y="32" class="t">Farhaan\'s GitHub activity</text>']
    for i, (label, val) in enumerate(rows):
        y = 66 + 28 * i
        lines.append(f'<text x="22" y="{y}" class="l">{label}</text><text x="398" y="{y}" class="v" text-anchor="end">{val:,}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


if __name__ == "__main__":
    svg = render(fetch())
    assert svg.startswith("<svg") and "Contributions" in svg
    open(os.path.join(os.path.dirname(__file__), "stats.svg"), "w").write(svg + "\n")
    print(svg.count("<text"), "text nodes written")
