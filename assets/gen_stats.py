"""Builds assets/stats.svg (the Trainer Card) from GitHub's GraphQL API. Runs daily in Actions with the built-in GITHUB_TOKEN.
Contribution totals include private work because the profile shows private contributions publicly."""
import base64, datetime, json, os, urllib.request

USER = "fakubwoy"
HERE = os.path.dirname(os.path.abspath(__file__))
GRASS = ["#1E1E24", "#172E73", "#1E46C8", "#4470F0", "#9DB7FF"]
Q = """query($u:String!){ user(login:$u){ databaseId
  contributionsCollection{ contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } }
  pullRequests(states:MERGED){ totalCount }
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){ totalCount nodes{ stargazerCount } }
}}"""


def fonts():
    """Inlined because an SVG used as an image cannot load anything external."""
    faces = []
    for fam, weight, name in (("Geist", 600, "geist"), ("Geist Mono", 400, "geistmono")):
        data = base64.b64encode(open(os.path.join(HERE, "fonts", name + ".woff2"), "rb").read()).decode()
        faces.append(f"@font-face{{font-family:'{fam}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}")
    return "".join(faces)


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "User-Agent": USER})
    return json.load(urllib.request.urlopen(req))["data"]["user"]


def streak(counts):
    """Consecutive active days, oldest first. Today still at zero does not break it."""
    if counts and counts[-1] == 0:
        counts = counts[:-1]
    n = 0
    for c in reversed(counts):
        if c == 0:
            break
        n += 1
    return n


def level(c):
    return sum(c >= t for t in (1, 4, 10, 20))


def render(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]
    rows = [
        ("Contributions, 12 months", cal["totalContributions"]),
        ("Current streak, days", streak(days)),
        ("Merged PRs, public", u["pullRequests"]["totalCount"]),
        ("Public repos", u["repositories"]["totalCount"]),
        ("Stars earned", sum(n["stargazerCount"] for n in u["repositories"]["nodes"])),
    ]
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="236" viewBox="0 0 1000 236" role="img" aria-label="Trainer card: GitHub activity for the last 12 months">',
             f"<style>{fonts()}.t{{font:600 22px Geist,sans-serif;fill:#EDEDEA}}.k{{font:400 13px 'Geist Mono',monospace;fill:#9A9AA2}}.v{{font:600 15px Geist,sans-serif;fill:#EDEDEA}}.a{{font:400 13px 'Geist Mono',monospace;fill:#6A93FF}}</style>",
             '<rect width="1000" height="236" fill="#0E0E10"/>',
             '<rect width="1000" height="4" fill="#1E46C8"/>',
             '<text x="32" y="48" class="t">Farhaan Khan</text>',
             f'<text x="968" y="48" class="a" text-anchor="end">IDNo. {u["databaseId"]}</text>']
    for i, (label, val) in enumerate(rows):
        y = 88 + 28 * i
        lines.append(f'<text x="32" y="{y}" class="k">{label}</text><text x="320" y="{y}" class="v" text-anchor="end">{val:,}</text>')
    size, gap, x0, y0 = 10, 2, 354, 76
    for wx, week in enumerate(cal["weeks"][-51:]):
        for day in week["contributionDays"]:
            dy = datetime.date.fromisoformat(day["date"]).isoweekday() % 7   # GitHub's weeks start on Sunday
            lines.append(f'<rect x="{x0 + wx * (size + gap)}" y="{y0 + dy * (size + gap)}" width="{size}" height="{size}" fill="{GRASS[level(day["contributionCount"])]}"/>')
    lines.append('<text x="354" y="186" class="k">Last 12 months: every square is a day, brighter grass means more contributions</text>')
    lines.append('</svg>')
    return "\n".join(lines)


if __name__ == "__main__":
    svg = render(fetch())
    assert svg.startswith("<svg") and "Contributions" in svg
    open(os.path.join(HERE, "stats.svg"), "w").write(svg + "\n")
    print(svg.count("<text"), "text nodes written")
