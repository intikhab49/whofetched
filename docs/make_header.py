"""Generate the README header SVG. Self-hosted on purpose.

capsule-render and friends time out through GitHub's camo proxy often enough to leave a broken image,
so the header is generated here and committed. The bars on the right are read from the published
summary, not typed in. Regenerate with:  python docs/make_header.py

Validates as XML before writing - a bare '&' in SVG text is invalid XML and GitHub renders it as
"Invalid image source" with no other warning.
"""
import json
import pathlib
import xml.dom.minidom

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUMMARY = ROOT / "evidence" / "2026-10-09" / "summary.json"

W, H = 1200, 340
BG = "#0A0A14"
AMBER, CORAL, PINK = "#FFB020", "#FF6B4A", "#FF4E88"
LIME, BLUE, DIM = "#A3E635", "#5B9BFF", "#8B8BA7"

APPS = [("Grok", "Grok"), ("Gemini", "Gemini"), ("ChatGPT", "ChatGPT"), ("Claude", "Claude")]


def max_ips():
    """Most distinct IPs that fetched one canary URL, per app, over the AI-driven rounds."""
    probes = json.loads(SUMMARY.read_text(encoding="utf-8"))["probes"]
    ai = [p for p in probes if p["round"] not in ("r1", "r1b")]
    return {label: max([p["distinct_ips"] for p in ai if p["product"] in (name, name + "-web")] or [0])
            for label, name in APPS}


def bars_svg(values, x0, y0, w, h, gap=14, axis=13):
    out, bh = [], (h - gap * (len(values) - 1)) / len(values)
    for i, (name, v) in enumerate(values.items()):
        y = y0 + i * (bh + gap)
        bw = max(w * v / axis, 4)
        hot = name == "Grok"
        out.append(f'<rect x="{x0}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" '
                   f'fill="{"url(#grad)" if hot else DIM}" opacity="{"1" if hot else "0.35"}"/>')
        out.append(f'<text x="{x0 + bw + 10:.1f}" y="{y + bh / 2 + 4:.1f}" '
                   f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="13" '
                   f'fill="{"#FFFFFF" if hot else DIM}" font-weight="{"700" if hot else "400"}">'
                   f'{v}  {name}</text>')
    return "\n    ".join(out)


def svg(values):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img"
     aria-label="whofetched: find out which AI actually fetched your page. Give each AI app a secret link,
     ask it to read it, and see who shows up. In tests on 9 October 2026, Grok fetched one page from up to
     {values['Grok']} different IP addresses; ChatGPT, Claude and Gemini each used one.">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{AMBER}"/>
      <stop offset="55%" stop-color="{CORAL}"/>
      <stop offset="100%" stop-color="{PINK}"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{CORAL}" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="{BG}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M28 0 L0 0 0 28" fill="none" stroke="#FFFFFF" stroke-opacity="0.04" stroke-width="1"/>
    </pattern>
  </defs>

  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <circle cx="{W - 160}" cy="70" r="240" fill="url(#fade)"/>

  <text x="64" y="86" font-family="ui-monospace,SFMono-Regular,Menlo,monospace"
        font-size="13" letter-spacing="3.5" fill="{LIME}">CANARY-URL ATTRIBUTION &#183; AI FETCHERS</text>

  <text x="60" y="164" font-family="Georgia,'Times New Roman',serif"
        font-size="68" font-weight="700" fill="url(#grad)">whofetched</text>

  <text x="64" y="204" font-family="-apple-system,Segoe UI,Helvetica,sans-serif"
        font-size="19" fill="#E8E8F0">Find out which AI actually fetched your page.</text>
  <text x="64" y="232" font-family="-apple-system,Segoe UI,Helvetica,sans-serif"
        font-size="19" fill="{DIM}">Secret link &#8594; ask the AI to read it &#8594; see who shows up.</text>

  <g font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12">
    <rect x="64" y="262" width="172" height="28" rx="14" fill="none" stroke="{AMBER}" stroke-opacity="0.55"/>
    <text x="150" y="281" fill="{AMBER}" text-anchor="middle">CLOUDFLARE WORKER</text>

    <rect x="248" y="262" width="150" height="28" rx="14" fill="none" stroke="{LIME}" stroke-opacity="0.55"/>
    <text x="323" y="281" fill="{LIME}" text-anchor="middle">HMAC CANARIES</text>

    <rect x="410" y="262" width="158" height="28" rx="14" fill="none" stroke="{BLUE}" stroke-opacity="0.55"/>
    <text x="489" y="281" fill="{BLUE}" text-anchor="middle">6 AI APPS TESTED</text>

    <rect x="580" y="262" width="168" height="28" rx="14" fill="none" stroke="{PINK}" stroke-opacity="0.55"/>
    <text x="664" y="281" fill="{PINK}" text-anchor="middle">TIMESTAMPED DATA</text>
  </g>

  <text x="820" y="74" font-family="ui-monospace,SFMono-Regular,Menlo,monospace"
        font-size="11" letter-spacing="2" fill="{DIM}">IPs THAT FETCHED ONE PAGE &#183; 9 OCT 2026</text>
  <g>
    {bars_svg(values, 820, 92, 205, 196)}
  </g>
</svg>
"""


if __name__ == "__main__":
    values = max_ips()
    text = svg(values)
    xml.dom.minidom.parseString(text)  # fails loudly on a bare '&'
    out = pathlib.Path(__file__).parent / "header.svg"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({len(text)} bytes, valid XML) from {values}")
