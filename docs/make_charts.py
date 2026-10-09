"""Charts for the README, drawn from evidence/2026-10-09/summary.json in the Open Jev palette.
Regenerate with:  python docs/make_charts.py
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUMMARY = ROOT / "evidence" / "2026-10-09" / "summary.json"
OUT = pathlib.Path(__file__).parent / "charts"

SURFACE, INK, INK_2, MUTED, BASELINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#c3c2b7"
S1, CRITICAL = "#2a78d6", "#d03b3b"

# (label on the chart, product names in probes.jsonl)
APPS = [
    ("Grok", ["Grok"]),
    ("Gemini", ["Gemini"]),
    ("ChatGPT", ["ChatGPT", "ChatGPT-web"]),
    ("Claude", ["Claude"]),
    ("Perplexity", ["Perplexity"]),
    ("GitHub Copilot", ["Copilot"]),
    ("Codex CLI", ["Codex-CLI"]),
]


def style():
    matplotlib.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "text.color": INK, "axes.labelcolor": INK_2, "xtick.color": MUTED, "ytick.color": INK_2,
        "axes.edgecolor": BASELINE, "axes.linewidth": 1.0,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": BASELINE, "grid.alpha": 0.45, "grid.linewidth": 0.8,
        "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.titlepad": 12, "figure.dpi": 120,
    })


def distinct_ips():
    probes = json.loads(SUMMARY.read_text(encoding="utf-8"))["probes"]
    # Rounds r1 and r1b were opened in the operator's own browser, not by any AI, so they are left out.
    ai = [p for p in probes if p["round"] not in ("r1", "r1b")]
    return [(label, [p["distinct_ips"] for p in ai if p["product"] in names]) for label, names in APPS]


def main():
    style()
    rows = distinct_ips()
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    for y, (label, values) in enumerate(reversed(rows)):
        n = len(values)
        for i, v in enumerate(values):
            dy = (i - (n - 1) / 2) * 0.09 if n > 1 else 0
            if v == 0:
                ax.scatter(v, y + dy, s=70, facecolors="none", edgecolors=MUTED, linewidths=1.6, zorder=3)
            else:
                ax.scatter(v, y + dy, s=70, color=CRITICAL if label == "Grok" else S1, zorder=3)
    labels = [label for label, _ in reversed(rows)]
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlim(-0.6, 13.2)
    ax.set_xticks(range(0, 14))
    ax.set_xlabel("distinct IP addresses that fetched the page for one request")
    ax.grid(axis="y", visible=False)
    ax.set_title("One request, how many machines showed up?")
    grok = dict(rows)["Grok"]
    ax.annotate(f"Grok: {min(grok)}–{max(grok)} IPs per request,\nproxy networks and home ISPs, no bot name",
                xy=(max(grok), len(rows) - 1), xytext=(6.2, len(rows) - 2.35), fontsize=9.5, color=CRITICAL,
                arrowprops=dict(arrowstyle="-", color=CRITICAL, lw=1))
    ax.set_axisbelow(True)
    fig.text(0.0, 1.0, "Each dot is one request to an AI app, 9 Oct 2026. Hollow dot = no request reached the site.",
             ha="left", va="bottom", fontsize=10, color=INK_2, transform=fig.transFigure)
    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    out = OUT / "ips-per-request.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"wrote {out} from {rows}")


if __name__ == "__main__":
    main()
