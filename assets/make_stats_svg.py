#!/usr/bin/env python3
"""
Builds the profile stats card from live GitHub data.

Why this exists: the public github-readme-stats / trophy / activity-graph
instances share one pool of API tokens and are rate-limited most of the time,
which is why they render as broken images. This talks to the API directly with
a token that has its own 5000 req/hr budget, so it cannot be starved by anyone
else's traffic.

    GITHUB_TOKEN=xxx python3 make_stats_svg.py            # live
    python3 make_stats_svg.py --cached stats-cache.json   # offline / preview

Writes assets/stats-dark.svg and assets/stats-light.svg. Stdlib only, so the
workflow needs no pip install.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

LOGIN = os.environ.get("GH_LOGIN", "gksriharsha")
API = "https://api.github.com"

# ------------------------------------------------------------------ palettes

THEMES = {
    "dark": {
        "text": "#c9d1d9", "dim": "#8b949e", "accent": "#58a6ff",
        "rule": "#21262d", "track": "#21262d", "title": "#58a6ff",
        "num": "#e6edf3",
    },
    "light": {
        "text": "#24292f", "dim": "#6e7781", "accent": "#0969da",
        "rule": "#e6eaef", "track": "#eaeef2", "title": "#0969da",
        "num": "#1f2328",
    },
}

# linguist colours for the languages that actually show up, plus a fallback ramp
LANG_COLOR = {
    "Python": "#3572A5", "HTML": "#e34c26", "Java": "#b07219",
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "CSS": "#563d7c",
    "SCSS": "#c6538c", "Groovy": "#4298b8", "Shell": "#89e051",
    "Dockerfile": "#384d54", "Jupyter Notebook": "#DA5B0B", "C": "#555555",
    "C++": "#f34b7d", "Go": "#00ADD8", "Rust": "#dea584", "Ruby": "#701516",
    "Makefile": "#427819", "Batchfile": "#C1F12E", "PowerShell": "#012456",
}
FALLBACK = ["#58a6ff", "#3fb950", "#d29922", "#db61a2", "#a371f7", "#f85149"]

W, H = 880, 246
FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")
MID = 470          # vertical divider
PAD = 44


# ------------------------------------------------------------------ fetching

def _req(url, token, data=None):
    hdrs = {"Accept": "application/vnd.github+json",
            "User-Agent": "profile-stats-card"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    if body:
        hdrs["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=hdrs)
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


GQL = """
query($login:String!) {
  user(login:$login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    contributionsCollection { totalCommitContributions }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false) {
      totalCount
      nodes {
        stargazerCount
        languages(first:12, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}"""


def lifetime_contributions(token, created_year):
    """contributionsCollection only covers a one-year window, so ask for every
    year since signup in a single aliased query and sum them."""
    now = datetime.now(timezone.utc).year
    parts = []
    for y in range(created_year, now + 1):
        parts.append(
            f'y{y}: contributionsCollection('
            f'from:"{y}-01-01T00:00:00Z", to:"{y}-12-31T23:59:59Z") '
            f'{{ contributionCalendar {{ totalContributions }} }}')
    q = "query($login:String!){ user(login:$login){ " + " ".join(parts) + " } }"
    out = _req(f"{API}/graphql", token, {"query": q, "variables": {"login": LOGIN}})
    if "errors" in out:
        raise RuntimeError(out["errors"])
    u = out["data"]["user"]
    return sum(v["contributionCalendar"]["totalContributions"]
               for v in u.values() if isinstance(v, dict))


def fetch(token):
    """GraphQL first (exact numbers); REST as a safety net."""
    try:
        out = _req(f"{API}/graphql", token,
                   {"query": GQL, "variables": {"login": LOGIN}})
        if "errors" in out:
            raise RuntimeError(out["errors"])
        u = out["data"]["user"]
        repos = u["repositories"]["nodes"]
        langs = {}
        for r in repos:
            for e in r["languages"]["edges"]:
                n = e["node"]["name"]
                langs[n] = langs.get(n, 0) + e["size"]
                LANG_COLOR.setdefault(n, e["node"]["color"] or "#8b949e")
        created = u["createdAt"]
        try:
            total = lifetime_contributions(token, int(created[:4]))
        except Exception as exc:                              # noqa: BLE001
            print(f"lifetime query failed ({exc})", file=sys.stderr)
            total = None
        return {
            "contributions": total,
            "commits": u["contributionsCollection"]["totalCommitContributions"],
            "repos": u["repositories"]["totalCount"],
            "stars": sum(r["stargazerCount"] for r in repos),
            "followers": u["followers"]["totalCount"],
            "prs": u["pullRequests"]["totalCount"],
            "since": created[:7],
            "languages": langs,
        }
    except Exception as exc:                                  # noqa: BLE001
        print(f"graphql failed ({exc}); falling back to REST", file=sys.stderr)

    user = _req(f"{API}/users/{LOGIN}", token)
    repos = _req(f"{API}/users/{LOGIN}/repos?per_page=100&type=owner", token)
    repos = [r for r in repos if not r["fork"]]
    langs = {}
    for r in repos:
        try:
            for n, sz in _req(r["languages_url"], token).items():
                langs[n] = langs.get(n, 0) + sz
        except urllib.error.HTTPError:
            pass
    return {
        "contributions": None,
        "commits": None,
        "repos": len(repos),
        "stars": sum(r["stargazers_count"] for r in repos),
        "followers": user["followers"],
        "prs": None,
        "since": user["created_at"][:7],
        "languages": langs,
    }


# ------------------------------------------------------------------ drawing

def human(n):
    if n is None:
        return "--"
    if n >= 1000:
        return f"{n:,}"
    return str(n)


def month(iso):
    try:
        return datetime.strptime(iso, "%Y-%m").strftime("%b %Y")
    except ValueError:
        return iso


def build(d, theme):
    c = THEMES[theme]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" aria-labelledby="st sd" '
         f'font-family="{FONT}">',
         '<title id="st">GitHub statistics</title>',
         f'<desc id="sd">Contribution counts and language breakdown for '
         f'{LOGIN}, regenerated daily from the GitHub API.</desc>']
    add = p.append

    # ---------- left: the numbers
    add(f'<text x="{PAD}" y="36" font-size="13" font-weight="600" '
        f'fill="{c["title"]}" letter-spacing="0.08em">BY THE NUMBERS</text>')

    # A metric we could not resolve is dropped rather than rendered as a dash,
    # so the seeded first commit still looks deliberate.
    cells = [(human(v), label) for v, label in (
        (d["contributions"], "total contributions"),
        (d["repos"],         "public repositories"),
        (d["commits"],       "commits, past year"),
        (d["stars"],         "stars earned"),
        (d["prs"],           "pull requests opened"),
        (d["followers"],     "followers"),
    ) if v is not None]
    col_x = [PAD, PAD + 196]
    row_y = [92, 150, 208]
    for i, (val, label) in enumerate(cells):
        x = col_x[i % 2]
        y = row_y[i // 2]
        delay = 0.06 * i
        add(f'<g opacity="1">'
            f'<animate attributeName="opacity" values="0;0;1" '
            f'keyTimes="0;{delay / 1.6:.3f};1" dur="1.6s" repeatCount="1" fill="freeze"/>'
            f'<text x="{x}" y="{y}" font-size="27" font-weight="700" '
            f'fill="{c["num"]}">{val}</text>'
            f'<text x="{x}" y="{y + 19}" font-size="11.5" fill="{c["dim"]}">'
            f'{label}</text></g>')

    add(f'<line x1="{MID}" y1="24" x2="{MID}" y2="{H - 24}" '
        f'stroke="{c["rule"]}" stroke-width="1"/>')

    # ---------- right: language breakdown
    rx = MID + 40
    rw = W - PAD - rx
    add(f'<text x="{rx}" y="36" font-size="13" font-weight="600" '
        f'fill="{c["title"]}" letter-spacing="0.08em">LANGUAGE BREAKDOWN</text>')

    langs = sorted(d["languages"].items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in langs) or 1
    top = langs[:6]
    shown = sum(v for _, v in top)
    if len(langs) > 6:
        top.append(("Other", total - shown))
        LANG_COLOR.setdefault("Other", c["dim"])

    add(f'<rect x="{rx}" y="58" width="{rw}" height="13" rx="6.5" '
        f'fill="{c["track"]}"/>')
    add(f'<defs><clipPath id="barclip"><rect x="{rx}" y="58" width="{rw}" '
        f'height="13" rx="6.5"/></clipPath></defs>')
    add('<g clip-path="url(#barclip)">')
    off = 0.0
    for i, (name, size) in enumerate(top):
        seg = rw * size / total
        col = LANG_COLOR.get(name, FALLBACK[i % len(FALLBACK)])
        add(f'  <rect x="{rx + off:.1f}" y="58" width="{seg:.1f}" height="13" '
            f'fill="{col}"><animate attributeName="width" values="0;{seg:.1f}" '
            f'dur="0.9s" begin="{0.05 * i:.2f}s" repeatCount="1" fill="freeze"/>'
            f'</rect>')
        off += seg
    add('</g>')

    # legend, two columns snapped to the bar's own width
    col_w = rw / 2
    for i, (name, size) in enumerate(top):
        cx = rx + (i % 2) * col_w
        cy = 104 + (i // 2) * 26
        col = LANG_COLOR.get(name, FALLBACK[i % len(FALLBACK)])
        pct = 100.0 * size / total
        add(f'<circle cx="{cx + 5:.1f}" cy="{cy - 4}" r="5" fill="{col}"/>')
        add(f'<text x="{cx + 18:.1f}" y="{cy}" font-size="12.5" '
            f'fill="{c["text"]}">{name}</text>')
        add(f'<text x="{cx + col_w - 10:.1f}" y="{cy}" font-size="12.5" '
            f'fill="{c["dim"]}" text-anchor="end">{pct:.1f}%</text>')

    add(f'<text x="{rx}" y="{H - 22}" font-size="11" fill="{c["dim"]}">'
        f'on GitHub since {month(d["since"])} '
        f'&#183; refreshed {datetime.now(timezone.utc):%d %b %Y}</text>')

    add('</svg>')
    return "\n".join(p)


# ------------------------------------------------------------------ entry

if __name__ == "__main__":
    if "--cached" in sys.argv:
        data = json.load(open(sys.argv[sys.argv.index("--cached") + 1]))
    else:
        data = fetch(os.environ.get("GITHUB_TOKEN"))

    here = os.path.dirname(os.path.abspath(__file__))
    for theme in THEMES:
        path = os.path.join(here, f"stats-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(data, theme))
        print("wrote", path)
