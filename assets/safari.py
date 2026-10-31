"""The wild Pokemon on this profile. A README cannot run code, so each sprite links to the safari on
my portfolio, which spawns that exact one to catch. Rewrites the safari block in README.md and
assets/hero.svg."""
import html, json, os, random, re, urllib.request

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


def block(wild):
    cells = []
    for m in wild:
        name = html.escape(m["name"])
        tag = " (shiny)" if m["shiny"] else " (rare)" if m["rare"] else ""
        url = f'{PORTFOLIO}?wild={m["id"]}' + ("&shiny=1" if m["shiny"] else "")
        src = SPRITES + ("shiny/" if m["shiny"] else "") + f'{m["id"]}.gif'
        cells.append(f'<td align="center" width="16%"><a href="{url}"><img src="{src}" height="72" alt="Catch {name}" title="Catch {name}"></a><br><sub><a href="{url}">{name}{tag}</a></sub></td>')
    return "<table><tr>\n" + "\n".join(cells) + "\n</tr></table>"


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


def name_of(i):
    req = urllib.request.Request(f"https://pokeapi.co/api/v2/pokemon/{i}", headers={"User-Agent": "fakubwoy"})
    return json.load(urllib.request.urlopen(req, timeout=30))["name"].replace("-", " ").title()


if __name__ == "__main__":
    wild = encounter(random.SystemRandom())
    for m in wild:
        m["name"] = name_of(m["id"])
    open(os.path.join(HERE, "hero.svg"), "w").write(hero())
    text = open(README).read()
    new, n = re.subn(r"(<!-- safari:start -->\n).*?(<!-- safari:end -->)", lambda m: m[1] + block(wild) + "\n" + m[2], text, flags=re.S)
    assert n == 1, "safari markers missing from README"
    open(README, "w").write(new)
    print("wild:", ", ".join(m["name"] for m in wild))
