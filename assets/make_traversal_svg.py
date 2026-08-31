#!/usr/bin/env python3
"""
Generates an animated SVG of a Gremlin traversal walking a family tree.

Emits two theme variants (light / dark) so the README can serve the right one
via <picture>. Animation is pure SMIL -- no JS, no build step, works when
GitHub serves the file through its image proxy.

    python3 make_traversal_svg.py            # writes into ./assets

Timeline is a single 12s loop. Every animation shares dur="12s" and
repeatCount="indefinite", with keyTimes carving out its own slice, so the
whole scene stays in sync forever without a master clock.
"""

import os
import re

# ---------------------------------------------------------------- palettes

THEMES = {
    "dark": {
        "text":       "#c9d1d9",
        "kw":         "#ff7b72",
        "method":     "#d2a8ff",
        "string":     "#a5d6ff",
        "number":     "#79c0ff",
        "comment":    "#8b949e",
        "punct":      "#8b949e",
        "rule":       "#21262d",
        "edge":       "#30363d",
        "edge_lit":   "#58a6ff",
        "node":       "#161b22",
        "node_ring":  "#30363d",
        "node_lit":   "#1f6feb",
        "node_lit_r": "#58a6ff",
        "start":      "#db61a2",
        "result":     "#3fb950",
        "pulse":      "#58a6ff",
        "caption":    "#8b949e",
        "accent":     "#58a6ff",
    },
    "light": {
        "text":       "#24292f",
        "kw":         "#cf222e",
        "method":     "#8250df",
        "string":     "#0a3069",
        "number":     "#0550ae",
        "comment":    "#6e7781",
        "punct":      "#6e7781",
        "rule":       "#e6eaef",
        "edge":       "#d0d7de",
        "edge_lit":   "#1f6feb",
        "node":       "#ffffff",
        "node_ring":  "#d0d7de",
        "node_lit":   "#1f6feb",
        "node_lit_r": "#1f6feb",
        "start":      "#bf3989",
        "result":     "#1a7f37",
        "pulse":      "#1f6feb",
        "caption":    "#6e7781",
        "accent":     "#0969da",
    },
}

W, H = 880, 436
DUR = "12s"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
FS = 14.0
CW = FS * 0.601          # monospace advance width
X0 = 44                  # left gutter

# ---------------------------------------------------------------- the query

QUERY = [
    "g.V().has('person','name','Krishna')",
    "  .repeat(out('child_of')).times(2)",
    "  .repeat(in('child_of')).times(2)",
]
COMMENTS = ["", "// up two generations", "// and back down"]
COMMENT_COL = 40

# ---------------------------------------------------------------- the graph
#   gp                    (440,170)
#   l1   250 / 440 / 630  (y=262)
#   l2   185 315 375 505 565 695  (y=354)
#   start = 375  ("you")

GP = (440, 170)
L1 = [(250, 262), (440, 262), (630, 262)]
L2 = [(185, 354), (315, 354), (375, 354), (505, 354), (565, 354), (695, 354)]
START = 2                       # index into L2
PARENT_OF_START = 1             # index into L1
CHILDREN = {0: [0, 1], 1: [2, 3], 2: [4, 5]}   # l1 index -> l2 indices


def curve(a, b):
    """Vertical-ish cubic bezier from a to b."""
    (x1, y1), (x2, y2) = a, b
    my = (y1 + y2) / 2
    return f"M{x1},{y1} C{x1},{my} {x2},{my} {x2},{y2}"


# ---------------------------------------------------------------- timeline
#            (fractions of the 12s loop)
T_LINE = [(0.020, 0.085), (0.085, 0.160), (0.160, 0.240)]
T_START_ON = 0.270
T_UP1 = (0.300, 0.362)          # you -> parent
T_UP2 = (0.378, 0.440)          # parent -> grandparent
T_DOWN1 = (0.470, 0.540)        # grandparent -> aunts/uncles
T_DOWN2 = (0.560, 0.632)        # them -> their children
T_RESULT = 0.664
T_HOLD_END = 0.900
T_RESET = 0.960


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tokenize(line, c):
    """Crude Gremlin tokenizer -> list of (text, color, char_offset)."""
    out = []
    pat = re.compile(r"'[^']*'|//.*$|\b\d+\b|[A-Za-z_][A-Za-z_0-9]*|\s+|.")
    for m in pat.finditer(line):
        t = m.group(0)
        if t.strip() == "":
            continue                      # positions are absolute; gaps are free
        if t.startswith("'"):
            col = c["string"]
        elif t.startswith("//"):
            col = c["comment"]
        elif t.isdigit():
            col = c["number"]
        elif t[:1].isalpha() or t[:1] == "_":
            col = c["method"] if line[m.end():m.end() + 1] == "(" else c["kw"]
        else:
            col = c["punct"]
        out.append((t, col, m.start()))
    return out


def spans(line, c, x0, size=FS):
    """Every token pinned to an exact x and width, so the layout is identical
    in every renderer regardless of which monospace font is available."""
    cw = size * 0.601
    return "".join(
        f'<tspan x="{x0 + off * cw:.1f}" textLength="{len(txt) * cw:.1f}" '
        f'lengthAdjust="spacing" fill="{col}">{esc(txt)}</tspan>'
        for txt, col, off in tokenize(line, c))


def anim(attr, keytimes, values, extra=""):
    kt = ";".join(f"{v:g}" for v in keytimes)
    vv = ";".join(values)
    return (f'<animate attributeName="{attr}" dur="{DUR}" repeatCount="indefinite" '
            f'calcMode="linear" keyTimes="{kt}" values="{vv}" {extra}/>')


def two_state(attr, dim, lit, on, off=T_RESET, ramp=0.012):
    """Dim -> lit at `on`, back to dim at `off`."""
    return anim(attr,
                [0, on - ramp, on, off, min(off + ramp * 3, 1.0), 1],
                [dim, dim, lit, lit, dim, dim])


def pulse(edge_id, t0, t1, c, reverse=False):
    """A comet travelling one edge. Base r="0" so that a renderer which ignores
    SMIL draws nothing at all, rather than parking a dot at the origin."""
    kp = "1;1;0;0" if reverse else "0;0;1;1"
    fade = 0.010
    kt = [0, t0 - fade, t0, t1, t1 + fade, 1]
    body = ""
    for radius, alpha, extra in ((9, "0.45", ' filter="url(#glow)"'), (3.6, "1", "")):
        body += f"""
    <circle r="0" fill="{c['pulse']}" opacity="0"{extra}>
      {anim("r", kt, ["0", "0", str(radius), str(radius), "0", "0"])}
      {anim("opacity", kt, ["0", "0", alpha, alpha, "0", "0"])}
      <animateMotion dur="{DUR}" repeatCount="indefinite" calcMode="linear"
        keyTimes="0;{t0:g};{t1:g};1" keyPoints="{kp}">
        <mpath xlink:href="#{edge_id}" href="#{edge_id}"/>
      </animateMotion>
    </circle>"""
    return f"  <g>{body}\n  </g>"


def build(theme):
    c = THEMES[theme]
    p = []
    add = p.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-labelledby="t d" font-family="{FONT}">')
    add('<title id="t">A Gremlin traversal walking a family tree</title>')
    add('<desc id="d">An animated diagram: a Gremlin query types out, then a pulse '
        'travels up two generations and back down, lighting up the first cousins it finds.</desc>')

    # ---- defs
    add('<defs>')
    add('<filter id="glow" x="-120%" y="-120%" width="340%" height="340%">'
        '<feGaussianBlur stdDeviation="4"/></filter>')
    for i, line in enumerate(QUERY):
        full = line
        if COMMENTS[i]:
            full = line.ljust(COMMENT_COL) + COMMENTS[i]
        w = len(full) * CW + 4
        t0, t1 = T_LINE[i]
        # base width is the FULL line: if SMIL never runs (static rasterisers,
        # some mobile clients) the viewer sees the finished frame, not a blank.
        add(f'<clipPath id="type{i}"><rect x="{X0 - 2}" y="{22 + i * 24}" height="22" width="{w:g}">'
            + anim("width", [0, t0, t1, T_RESET, min(T_RESET + 0.02, 1.0), 1],
                   ["0", "0", f"{w:g}", f"{w:g}", "0", "0"])
            + '</rect></clipPath>')
    add('</defs>')

    # ---- query block
    add('<g>')
    for i, line in enumerate(QUERY):
        y = 38 + i * 24
        full = line.ljust(COMMENT_COL) + COMMENTS[i] if COMMENTS[i] else line
        add(f'  <text y="{y}" font-size="{FS}" clip-path="url(#type{i})">'
            f'{spans(full, c, X0)}</text>')
        # travelling caret
        t0, t1 = T_LINE[i]
        x_end = X0 + len(full) * CW
        add(f'  <rect y="{y - 11}" width="0" height="15" fill="{c["accent"]}" opacity="0" x="{X0}">'
            + anim("x", [0, t0, t1, 1], [f"{X0}", f"{X0}", f"{x_end:g}", f"{x_end:g}"])
            + anim("width", [0, t0 - 0.006, t0, t1, t1 + 0.006, 1], ["0", "0", "8", "8", "0", "0"])
            + anim("opacity", [0, t0 - 0.006, t0, t1, t1 + 0.006, 1],
                   ["0", "0", "0.9", "0.9", "0", "0"])
            + '</rect>')
    # blinking caret parked at the end while results are shown
    tail = QUERY[2].ljust(COMMENT_COL) + COMMENTS[2]
    add(f'  <rect x="{X0 + len(tail) * CW:g}" y="{38 + 2 * 24 - 11}" width="0" height="15" '
        f'fill="{c["accent"]}" opacity="0">'
        + anim("width", [0, T_LINE[2][1], 0.50, min(T_RESET, 1.0), 1], ["0", "8", "8", "0", "0"])
        + anim("opacity",
               [0, T_LINE[2][1], 0.30, 0.34, 0.38, 0.42, 0.46, 0.50, T_RESET, 1],
               ["0", "0.9", "0.9", "0", "0.9", "0", "0.9", "0", "0", "0"])
        + '</rect>')
    add('</g>')

    add(f'<line x1="{X0}" y1="122" x2="{W - X0}" y2="122" stroke="{c["rule"]}" stroke-width="1"/>')

    # ---- edges
    edges = []
    for i, n in enumerate(L1):
        edges.append((f"e-gp-{i}", curve(GP, n)))
    for li, kids in CHILDREN.items():
        for k in kids:
            edges.append((f"e-l1-{li}-{k}", curve(L1[li], L2[k])))

    add('<g fill="none" stroke-width="1.8" stroke-linecap="round">')
    for eid, d in edges:
        add(f'  <path id="{eid}" d="{d}" stroke="{c["edge"]}"/>')
    add('</g>')

    # edges brighten as the traversal crosses them
    add('<g fill="none" stroke-width="2.2" stroke-linecap="round">')
    lit_windows = {
        f"e-l1-{PARENT_OF_START}-{START}": T_UP1[1],
        f"e-gp-{PARENT_OF_START}": T_UP2[1],
    }
    for i in range(3):
        lit_windows.setdefault(f"e-gp-{i}", T_DOWN1[1])
    for li, kids in CHILDREN.items():
        for k in kids:
            lit_windows.setdefault(f"e-l1-{li}-{k}", T_DOWN2[1])
    for eid, d in edges:
        on = lit_windows[eid]
        add(f'  <path d="{d}" stroke="{c["edge_lit"]}" opacity="0.85">'
            + anim("opacity", [0, on - 0.02, on, T_HOLD_END, T_RESET, 1],
                   ["0", "0", "0.85", "0.85", "0", "0"]) + '</path>')
    add('</g>')

    # ---- pulses
    add(pulse(f"e-l1-{PARENT_OF_START}-{START}", *T_UP1, c, reverse=True))
    add(pulse(f"e-gp-{PARENT_OF_START}", *T_UP2, c, reverse=True))
    for i in range(3):
        add(pulse(f"e-gp-{i}", *T_DOWN1, c))
    for li, kids in CHILDREN.items():
        for k in kids:
            add(pulse(f"e-l1-{li}-{k}", *T_DOWN2, c))

    # ---- nodes
    def node(x, y, on):
        return (f'  <g><circle cx="{x}" cy="{y}" r="13" fill="{c["node_lit"]}" '
                f'stroke="{c["node_lit_r"]}" stroke-width="1.8">'
                + two_state("fill", c["node"], c["node_lit"], on)
                + two_state("stroke", c["node_ring"], c["node_lit_r"], on)
                + '</circle></g>')

    add('<g>')
    add(node(*GP, T_UP2[1]))
    for i, n in enumerate(L1):
        add(node(*n, T_UP1[1] if i == PARENT_OF_START else T_DOWN1[1]))
    for i, n in enumerate(L2):
        if i == START:
            continue
        add(node(*n, T_DOWN2[1]))
    add('</g>')

    # ---- start node: always tinted, ripples once the query fires
    sx, sy = L2[START]
    add(f'<g><circle cx="{sx}" cy="{sy}" r="13" fill="{c["start"]}" stroke="{c["start"]}" '
        f'stroke-width="1.8" opacity="1">'
        + anim("opacity", [0, T_START_ON - 0.01, T_START_ON, T_HOLD_END, T_RESET, 1],
               ["0.45", "0.45", "1", "1", "0.45", "0.45"]) + '</circle>')
    for k in range(2):
        d = T_START_ON + k * 0.030
        add(f'  <circle cx="{sx}" cy="{sy}" r="13" fill="none" stroke="{c["start"]}" stroke-width="2">'
            + anim("r", [0, d, d + 0.075, 1], ["13", "13", "30", "30"])
            + anim("opacity", [0, d, d + 0.075, 1], ["0", "0.8", "0", "0"]) + '</circle>')
    add(f'  <text x="{sx}" y="{sy + 27}" font-size="11" fill="{c["start"]}" text-anchor="middle" '
        f'opacity="1">start'
        + anim("opacity", [0, T_START_ON, T_START_ON + 0.02, T_HOLD_END, T_RESET, 1],
               ["0", "0", "1", "1", "0", "0"]) + '</text>')
    add('</g>')

    # ---- result rings on everything the query returned (siblings + cousins)
    add('<g fill="none">')
    for i, (x, y) in enumerate(L2):
        if i == START:
            continue
        add(f'  <circle cx="{x}" cy="{y}" r="20" stroke="{c["result"]}" stroke-width="2" opacity="1">'
            + anim("r", [0, T_RESULT, T_RESULT + 0.02, T_HOLD_END, T_RESET, 1],
                   ["13", "13", "20", "20", "13", "13"])
            + anim("opacity", [0, T_RESULT, T_RESULT + 0.02, T_HOLD_END, T_RESET, 1],
                   ["0", "0", "1", "1", "0", "0"]) + '</circle>')
    add('</g>')

    # ---- captions
    fade_in = anim("opacity", [0, T_RESULT, T_RESULT + 0.02, T_HOLD_END, T_RESET, 1],
                   ["0", "0", "1", "1", "0", "0"])
    add(f'<text x="{X0}" y="410" font-size="13" fill="{c["result"]}" textLength="94" '
        f'lengthAdjust="spacing" opacity="1">&#8594; 5 vertices{fade_in}</text>')
    add(f'<text x="{X0 + 108}" y="410" font-size="13" fill="{c["caption"]}" opacity="1">'
        f'&#183; siblings + first cousins{fade_in}</text>')
    add(f'<text x="{W - X0}" y="410" font-size="13" fill="{c["caption"]}" text-anchor="end" '
        f'opacity="1">one traversal, zero joins'
        + anim("opacity", [0, T_RESULT + 0.02, T_RESULT + 0.045, T_HOLD_END, T_RESET, 1],
               ["0", "0", "1", "1", "0", "0"]) + '</text>')

    add('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "assets")
    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        path = os.path.join(out, f"traversal-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(theme))
        print("wrote", path)
