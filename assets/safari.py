"""The wild Pokemon on this profile. A README cannot run code, so each sprite links to the safari on
my portfolio, which spawns that exact one to catch. Rewrites the safari block in README.md and
assets/hero.svg. Cards hold their GIF, so each is built once and reused: rotating them must not grow git forever."""
import base64, html, json, os, random, re, urllib.error, urllib.request

from gen_stats import HERE, fonts

README = os.path.join(HERE, "..", "README.md")
PORTFOLIO = "https://fakubwoy.github.io/portfolio/"
WILD_COUNT = 6
GEN5_MAX = 649
SHINY_ODDS = 1 / 40
RARE_ODDS = 0.045
LEGEND = [144,145,146,150,243,244,245,249,250,377,378,379,380,381,382,383,384,
          480,481,482,483,484,485,486,487,488,638,639,640,641,642,643,644,645,646]
MYTH = [151,251,385,386,489,490,491,492,493,494,647,648,649]
RARE = set(LEGEND + MYTH)
CARDS = os.path.join(HERE, "cards")
TYPES = {"normal": "#A8A77A", "fire": "#EE8130", "water": "#6390F0", "electric": "#F7D02C", "grass": "#7AC74C", "ice": "#96D9D6",
         "fighting": "#C22E28", "poison": "#A33EA1", "ground": "#E2BF65", "flying": "#A98FF3", "psychic": "#F95587", "bug": "#A6B91A",
         "rock": "#B6A136", "ghost": "#735797", "dragon": "#6F35FC", "dark": "#705746", "steel": "#B7B7CE", "fairy": "#D685AD"}
GOLD = "#F5C542"
SPRITES = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/"


def spawn(rng):
    rare = rng.random() < RARE_ODDS
    if rare:
        i = rng.choice(LEGEND if rng.random() < 0.6 else MYTH)
    else:
        i = rng.choice([n for n in range(1, GEN5_MAX + 1) if n not in RARE])
    return {"id": i, "shiny": rng.random() < SHINY_ODDS, "rare": rare}


def encounter(rng, count=WILD_COUNT):
    """Distinct wild Pokemon."""
    wild = {}
    while len(wild) < count:
        mon = spawn(rng)
        wild[mon["id"]] = mon
    return list(wild.values())


def card_name(m):
    return f'{m["id"]}{"s" if m["shiny"] else ""}.svg'


def fit(w, h):
    """Bigger sprites shrink to the box, tiny ones stop at 2x so the pixels stay crisp."""
    return min(2, 104 / max(w, h))


def card(m, gif):
    w, h = int.from_bytes(gif[6:8], "little"), int.from_bytes(gif[8:10], "little")
    scale = fit(w, h)
    w, h = w * scale, h * scale
    color = TYPES[m["type"]]
    tag = "SHINY" if m["shiny"] else "RARE" if m["rare"] else m["type"].upper()
    frame, tag_color = (GOLD, GOLD) if m["shiny"] or m["rare"] else ("#26262C", color)
    data = base64.b64encode(gif).decode()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="196" viewBox="0 0 160 196" role="img" aria-label="Catch {html.escape(m["name"])}">
<style>{fonts()}.n{{font:600 15px Geist,sans-serif;fill:#EDEDEA}}.k{{font:400 11px 'Geist Mono',monospace;letter-spacing:.5px}}</style>
<rect x="1" y="1" width="158" height="194" fill="#0E0E10" stroke="{frame}" stroke-width="2"/>
<rect x="2" y="2" width="156" height="3" fill="{color}"/>
<text x="13" y="25" class="k" fill="#80808A">#{m["id"]:03d}</text>
<text x="147" y="25" class="k" fill="{tag_color}" text-anchor="end">{tag}</text>
<ellipse cx="80" cy="145" rx="52" ry="9" fill="{color}" opacity=".2"/>
<image href="data:image/gif;base64,{data}" x="{80 - w / 2:g}" y="{148 - h:g}" width="{w:g}" height="{h:g}" style="image-rendering:pixelated"/>
<text x="80" y="177" class="n" text-anchor="middle">{html.escape(m["name"])}</text>
</svg>
'''


def sprite(m):
    """A few Pokemon have no shiny sprite: fall back to the normal one, like the portfolio does."""
    urls = [SPRITES + f'shiny/{m["id"]}.gif'] if m["shiny"] else []
    for url in urls + [SPRITES + f'{m["id"]}.gif']:
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "fakubwoy"}), timeout=30).read()
        except urllib.error.HTTPError:
            if not url.count("/shiny/"):
                raise


def block(wild):
    out = []
    for m in wild:
        name = html.escape(m["name"])
        url = f'{PORTFOLIO}?wild={m["id"]}' + ("&shiny=1" if m["shiny"] else "")
        out.append(f'<a href="{url}"><img src="assets/cards/{card_name(m)}" width="15%" alt="Catch {name}" title="Catch {name}"></a>')
    return '<p align="center">\n' + "\n".join(out) + "\n</p>"


def hero():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="200" viewBox="0 0 1000 200" role="img" aria-label="Farhaan Khan, software engineer, with a Great Ball">
<style>{fonts()}
.n{{font:600 68px Geist,sans-serif;letter-spacing:-2.5px;fill:#EDEDEA}}.r{{font:400 17px 'Geist Mono',monospace;fill:#9A9AA2}}.a{{font:400 14px 'Geist Mono',monospace;fill:#6A93FF}}
.ball{{transform-origin:830px 170px;animation:shake 4.2s ease-in-out infinite}}
@keyframes shake{{0%,62%,100%{{transform:rotate(0)}}68%{{transform:rotate(-13deg)}}76%{{transform:rotate(11deg)}}84%{{transform:rotate(-7deg)}}92%{{transform:rotate(4deg)}}}}
@media (prefers-reduced-motion:reduce){{.ball{{animation:none}}}}
</style>
<rect width="1000" height="200" fill="#0E0E10"/>
<text x="40" y="62" class="a">HYDERABAD, INDIA / VIT '26 / IEEE ACCESS AUTHOR</text>
<text x="36" y="132" class="n">Farhaan Khan</text>
<text x="40" y="168" class="r">Building production AI agents and med-tech.</text>
<g class="ball"><circle cx="830" cy="100" r="74" fill="#E6E6E2"/><path d="M756 100a74 74 0 0 1 148 0z" fill="#2B5DE6"/>
<path d="M782 44l22 22h-16l-20-14zM878 44l-22 22h16l20-14z" fill="#E0301E"/>
<rect x="756" y="93" width="148" height="14" fill="#0E0E11"/><circle cx="830" cy="100" r="24" fill="#0E0E11"/><circle cx="830" cy="100" r="14" fill="#F4F4F1"/></g>
<rect y="196" width="1000" height="4" fill="#1E46C8"/>
</svg>
'''


def details(i):
    req = urllib.request.Request(f"https://pokeapi.co/api/v2/pokemon/{i}", headers={"User-Agent": "fakubwoy"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    return d["name"].replace("-", " ").title(), d["types"][0]["type"]["name"]


if __name__ == "__main__":
    wild = encounter(random.SystemRandom())
    os.makedirs(CARDS, exist_ok=True)
    for m in wild:
        m["name"], m["type"] = details(m["id"])
        path = os.path.join(CARDS, card_name(m))
        if not os.path.exists(path):
            open(path, "w").write(card(m, sprite(m)))
    open(os.path.join(HERE, "hero.svg"), "w").write(hero())
    text = open(README).read()
    new, n = re.subn(r"(<!-- safari:start -->\n).*?(<!-- safari:end -->)", lambda m: m[1] + block(wild) + "\n" + m[2], text, flags=re.S)
    assert n == 1, "safari markers missing from README"
    open(README, "w").write(new)
    print("wild:", ", ".join(m["name"] for m in wild))
