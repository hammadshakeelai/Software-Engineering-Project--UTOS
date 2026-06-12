"""Render a clean UML package diagram of the UTOS layered architecture."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images", "generated")
os.makedirs(OUT, exist_ok=True)

TEAL = "#0F6E66"
DARK = "#1A1A2E"
TAB = "#0F6E66"
BODY = "#FFFFFF"
EDGE = "#0F6E66"

# package: (id, x, y, w, h, title, stereotype, contents)
PKGS = [
    ("ui", 1.6, 8.4, 5.6, 1.5, "Presentation", "«user interface»",
     "index.html · api.js · state.js\nrender.js · main.js  (vanilla ES modules)"),
    ("api", 2.6, 6.7, 3.6, 1.2, "Web API", "«controller»",
     "server.py\nThreadingHTTPServer · JSON REST routing"),
    ("svc", 0.5, 4.9, 3.4, 1.3, "Application Services", "«service»",
     "bootstrap_service\ntimetable_service"),
    ("alg", 4.7, 4.9, 3.4, 1.3, "Solver", "«algorithm»",
     "timetable_solver\nsolve(problem) → result"),
    ("repo", 0.5, 3.0, 3.4, 1.3, "Repositories", "«data access»",
     "master_data · timetable_repository\nsystem (notifications, audit)"),
    ("dom", 4.7, 3.0, 3.4, 1.3, "Domain Model", "«entities»",
     "Person · Course · Timetable\nClassSession · Room · Policy …"),
    ("db", 2.6, 1.2, 3.4, 1.3, "Persistence", "«infrastructure»",
     "database.py · schema.sql\nseed.py · migrate.py  (SQLite)"),
]
# dependency arrows: (from, to)
DEPS = [
    ("ui", "api"), ("api", "svc"), ("api", "alg"),
    ("svc", "repo"), ("svc", "alg"), ("svc", "dom"),
    ("alg", "dom"), ("repo", "dom"), ("repo", "db"),
]


def center(p):
    _, x, y, w, h, *_ = p
    return (x + w / 2, y + h / 2)


def box(p):
    return {p[0]: p for p in PKGS}[p]


def draw():
    fig, ax = plt.subplots(figsize=(9.2, 6.6), dpi=170)
    ax.set_xlim(0, 8.7); ax.set_ylim(0.6, 10.2); ax.axis("off")
    idx = {p[0]: p for p in PKGS}

    # arrows first (behind boxes)
    for a, b in DEPS:
        pa, pb = idx[a], idx[b]
        xa, ya = center(pa); xb, yb = center(pb)
        arr = FancyArrowPatch((xa, ya), (xb, yb),
                              arrowstyle="-|>", mutation_scale=14,
                              linestyle=(0, (5, 3)), color="#7A8A88", lw=1.3,
                              shrinkA=38, shrinkB=38, zorder=1)
        ax.add_patch(arr)

    for pid, x, y, w, h, title, stereo, contents in PKGS:
        # folder tab
        tabw = max(2.0, 0.06 * len(title) + 1.4)
        ax.add_patch(Rectangle((x, y + h), tabw, 0.34, facecolor=TAB,
                                edgecolor=EDGE, lw=1.4, zorder=3))
        ax.text(x + 0.18, y + h + 0.17, title, color="white", fontsize=10.5,
                fontweight="bold", va="center", ha="left", zorder=4)
        # body
        ax.add_patch(Rectangle((x, y), w, h, facecolor=BODY, edgecolor=EDGE,
                               lw=1.4, zorder=3))
        ax.text(x + w / 2, y + h - 0.26, stereo, color=TEAL, fontsize=8.5,
                style="italic", ha="center", va="center", zorder=4)
        ax.text(x + w / 2, y + h / 2 - 0.18, contents, color=DARK, fontsize=8.2,
                ha="center", va="center", zorder=4, linespacing=1.4)

    # legend (bottom-left, clear of all packages)
    ax.add_patch(FancyArrowPatch((0.5, 1.55), (1.2, 1.55), arrowstyle="-|>",
                 mutation_scale=12, linestyle=(0, (5, 3)), color="#7A8A88", lw=1.3))
    ax.text(1.35, 1.55, "dependency  «import / call»", fontsize=8.5,
            color="#555F6B", va="center")
    ax.set_title("UTOS — Package Diagram (Layered Architecture)",
                 fontsize=13, fontweight="bold", color=DARK, pad=8)
    fig.tight_layout()
    path = os.path.join(OUT, "package_diagram.png")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    print("saved", path)


if __name__ == "__main__":
    draw()
