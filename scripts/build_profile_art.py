"""Build the local SVG artwork for the profile README.

Only Python's standard library is used. The artwork deliberately uses solid
fills; the movement comes from SVG SMIL animation rather than gradients or JS.
"""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BG = "#080b10"
PANEL = "#0e141d"
LINE = "#263241"
WHITE = "#f3f5f7"
MUTED = "#aab6c4"
CYAN = "#3dd6d0"
RED = "#ee5757"
ORANGE = "#f2a24c"
BLUE = "#4b83e8"
GREEN = "#55b87a"
YELLOW = "#f0d35a"


def svg(width: int, height: int, title: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="svg-title">'
        f'<title id="svg-title">{escape(title)}</title>'
        f'<rect width="{width}" height="{height}" rx="18" fill="{BG}"/>'
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="17" fill="none" stroke="{LINE}"/>'
        f"{body}</svg>"
    )


def text(x: int, y: int, value: str, size: int = 16, color: str = WHITE,
         weight: int = 400, family: str = "Arial, sans-serif") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}">{escape(value)}</text>'
    )


def polygon(points: list[tuple[float, float]], fill: str, stroke: str = BG,
            width: int = 2) -> str:
    points_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{points_text}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def face_cells(corners: list[tuple[float, float]], colors: list[str],
               rows: tuple[int, ...] = (0, 1, 2)) -> str:
    output = []
    a, b, c, d = corners
    for row in range(3):
        if row not in rows:
            continue
        for col in range(3):
            # Leave a real dark seam between stickers instead of relying only
            # on a stroke. This makes the cubies read cleanly at README size.
            gap = 0.055
            u0 = (col + gap) / 3
            u1 = (col + 1 - gap) / 3
            v0 = (row + gap) / 3
            v1 = (row + 1 - gap) / 3
            p00 = lerp(lerp(a, b, u0), lerp(d, c, u0), v0)
            p10 = lerp(lerp(a, b, u1), lerp(d, c, u1), v0)
            p11 = lerp(lerp(a, b, u1), lerp(d, c, u1), v1)
            p01 = lerp(lerp(a, b, u0), lerp(d, c, u0), v1)
            output.append(polygon([p00, p10, p11, p01], colors[row * 3 + col]))
    return "".join(output)


def cube_hero() -> None:
    front = [ORANGE, RED, RED, RED, RED, WHITE, RED, RED, RED]
    top = [YELLOW, YELLOW, WHITE, YELLOW, YELLOW, YELLOW, WHITE, YELLOW, YELLOW]
    right = [BLUE, BLUE, GREEN, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE]

    body = text(38, 42, "MITHILESH / 07", 12, CYAN, 700, "monospace")
    body += text(38, 105, "Mithilesh", 54, WHITE, 700)
    body += text(40, 139, "ADHINARAYANAN", 19, MUTED, 400, "monospace")
    body += text(40, 191, "state  →  move  →  result", 22, CYAN, 700, "monospace")
    body += text(40, 226, "reinforcement learning · quant finance · applied ML", 14, MUTED)
    body += text(40, 272, "π(a | s)     P(s' | s, a)     Σ error(t)", 17, WHITE, 400, "monospace")
    body += text(40, 303, "R U R′ U′", 15, YELLOW, 700, "monospace")
    body += text(151, 303, "a four-move turn, rendered as a moving cube", 12, MUTED)
    body += f'<path d="M40 336H1016" stroke="{LINE}"/>'
    body += text(40, 366, "SASTRA UNIVERSITY  /  CSE · AI & DS  /  2024–2028", 11, MUTED, 400, "monospace")
    body += text(830, 366, "HOSUR, INDIA", 11, CYAN, 400, "monospace")

    # The three visible faces are divided into nine stickers. The group tilts
    # and its top layer shifts, creating a cube-turn without JavaScript.
    cube = []
    front_corners = [(650, 129), (830, 129), (830, 309), (650, 309)]
    top_corners = [(650, 129), (760, 74), (940, 74), (830, 129)]
    right_corners = [(830, 129), (940, 74), (940, 254), (830, 309)]
    cube.append('<g id="rubiks-cube">')
    cube.append('<animateTransform attributeName="transform" type="rotate" values="0 795 190;-2 795 190;2 795 190;0 795 190" dur="5.8s" repeatCount="indefinite"/>')
    # The lower two rows remain fixed while the top layer separates, turns,
    # and returns. It reads as a U-layer move rather than a floating icon.
    cube.append(face_cells(front_corners, front, rows=(1, 2)))
    cube.append(face_cells(right_corners, right, rows=(1, 2)))
    cube.append('<g id="turning-top">')
    cube.append('<animateTransform attributeName="transform" type="translate" values="0 0;8 -4;20 -7;8 -3;0 0" dur="4.8s" repeatCount="indefinite"/>')
    cube.append('<animateTransform attributeName="transform" type="rotate" values="0 795 129;-4 795 129;-7 795 129;-2 795 129;0 795 129" dur="4.8s" repeatCount="indefinite" additive="sum"/>')
    cube.append(face_cells(front_corners, front, rows=(0,)))
    cube.append(face_cells(right_corners, right, rows=(0,)))
    cube.append(face_cells(top_corners, top))
    cube.append("</g></g>")
    body += "".join(cube)

    # Orbit line and a moving point make the mathematical notation feel alive.
    body += f'<path d="M530 334 C650 390 810 360 900 290" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="3 8"><animate attributeName="stroke-dashoffset" from="0" to="-44" dur="2.5s" repeatCount="indefinite"/></path>'
    body += f'<circle r="4" fill="{YELLOW}"><animateMotion dur="4.5s" repeatCount="indefinite" path="M530 334 C650 390 810 360 900 290"/></circle>'
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "cube-hero.svg").write_text(
        svg(1080, 400, "Mithilesh Adhinarayanan — Rubik's cube and mathematics", body),
        encoding="utf-8",
    )


def project_card(filename: str, index: str, title: str, line1: str, line2: str,
                 stack: str, accent: str) -> None:
    body = text(24, 34, index, 11, accent, 700, "monospace")
    body += text(24, 73, title, 24, WHITE, 700)
    body += text(24, 111, line1, 14, MUTED)
    body += text(24, 133, line2, 14, MUTED)
    body += f'<path d="M24 158H426" stroke="{LINE}"/>'
    body += text(24, 188, stack, 11, WHITE, 400, "monospace")
    body += f'<rect x="24" y="218" width="62" height="4" rx="2" fill="{accent}"/>'
    body += f'<circle cx="412" cy="220" r="4" fill="{accent}"><animate attributeName="r" values="3;6;3" dur="2.4s" repeatCount="indefinite"/></circle>'
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / filename).write_text(svg(450, 250, title, body), encoding="utf-8")


def cards() -> None:
    project_card("project-traffic.svg", "01 / CONTROL", "Adaptive Traffic",
                 "Multi-agent signal control with a", "safety layer around learned policies.",
                 "DQN · OpenCV · FastAPI · MQTT", RED)
    project_card("project-crafthaat.svg", "02 / ACCESS", "CraftHaat",
                 "A voice note and a photo become", "an offline-first artisan listing.",
                 "Flutter · FastAPI · Whisper · Ollama", ORANGE)
    project_card("project-openenv.svg", "03 / DATA", "Exchange Rate OpenEnv",
                 "An agent chooses how to handle", "missing, spiking, or stale ticks.",
                 "Python · OpenEnv · Docker", CYAN)
    project_card("project-deep-learning.svg", "04 / FOUNDATIONS", "Deep Learning",
                 "Models and notebooks built while", "working through the fundamentals.",
                 "Python · Jupyter · NPTEL", BLUE)
    project_card("project-efsat.svg", "05 / SATELLITE", "EFSAT",
                 "An Efficient Satellite Analyser", "built as a 2026 SIH project.",
                 "Python · satellite analysis · SIH 2026", GREEN)
    project_card("project-gsoc.svg", "06 / OPEN SOURCE", "PyMC / GSoC Prep",
                 "Open-source preparation for a", "PyMC-focused GSoC 2026 path.",
                 "PyMC · Bayesian modelling · GSoC 2026", YELLOW)


def work_tree() -> None:
    """Draw the README-safe, non-interactive version of the work tree."""
    width, height = 1180, 700
    body = (
        '<style>'
        '.node .box{transition:fill .2s,stroke .2s}'
        '.node:hover .box{fill:#18232e;stroke:#f0d35a;stroke-width:2}'
        '.node:hover .label{fill:#ffffff}'
        '</style>'
        '<text x="34" y="38" fill="#3dd6d0" font-family="monospace" font-size="12" font-weight="700">'
        'MITHILESH / WORK TREE</text>'
        '<text x="34" y="65" fill="#aab6c4" font-family="Arial, sans-serif" font-size="15">'
        'present work branches from research questions into systems, mathematics, and open source</text>'
    )

    def line(x1: int, y1: int, x2: int, y2: int, accent: str = LINE) -> str:
        return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{accent}" stroke-width="2" fill="none"/>'

    def node(x: int, y: int, title: str, detail: str, accent: str) -> str:
        return (
            f'<g class="node"><title>{escape(title)} — {escape(detail)}</title>'
            f'<rect class="box" x="{x}" y="{y}" width="250" height="62" rx="9" fill="#0e141d" stroke="#263241"/>'
            f'<rect x="{x}" y="{y}" width="5" height="62" rx="2" fill="{accent}"/>'
            f'<text class="label" x="{x+18}" y="{y+27}" fill="#f3f5f7" font-family="Arial, sans-serif" font-size="14" font-weight="700">{escape(title)}</text>'
            f'<text x="{x+18}" y="{y+47}" fill="#aab6c4" font-family="monospace" font-size="10">{escape(detail)}</text>'
            '</g>'
        )

    root_x, root_y = 465, 90
    body += node(root_x, root_y, "Mithilesh / 2024 → now", "CSE · AI & DS · SASTRA", CYAN)
    branches = [
        (30, "research", "DNN–RL + APT detection", CYAN),
        (315, "systems", "models meet applications", RED),
        (600, "open source", "learn in public", YELLOW),
        (885, "mathematics", "probability · proof · risk", ORANGE),
    ]
    root_center = root_x + 125
    for x, title, detail, accent in branches:
        branch_center = x + 125
        body += line(root_center, root_y + 62, branch_center, 174, accent)
        body += node(x, 174, title, detail, accent)

    children = [
        (30, 285, "Exchange-rate forecasting", "DNN · PPO · NIFTY 50", CYAN),
        (30, 373, "APT detection", "anomaly · network security", CYAN),
        (315, 285, "Adaptive Traffic", "DQN · MARL · OpenCV", RED),
        (315, 373, "CraftHaat + EFSAT", "voice catalog · satellite", RED),
        (600, 285, "PyMC / GSoC prep", "Bayesian · contribution track", YELLOW),
        (600, 373, "BSTS · ML4Sci · OSM", "research preparation", YELLOW),
        (885, 285, "WorldQuant BRAIN", "alpha · backtesting · risk", ORANGE),
        (885, 373, "IOQM · Yale · CS50W", "math · finance · web", ORANGE),
    ]
    for x, y, title, detail, accent in children:
        body += line(x + 125, 236, x + 125, y, accent)
        body += node(x, y, title, detail, accent)

    body += '<path d="M30 485H1135" stroke="#263241"/>'
    body += '<text x="30" y="516" fill="#f0d35a" font-family="monospace" font-size="11" font-weight="700">SKILL INDEX</text>'
    skill_lines = [
        "AI / ML     RL · PPO · DQN · MARL · PyTorch · TensorFlow · Scikit-Learn",
        "NLP / LLM   Transformers · BERT / GPT · Hugging Face · RAG · LangChain",
        "VISION      OpenCV · YOLO · CNNs · detection · segmentation · video",
        "SYSTEMS     Python · C / C++ · Java · JavaScript · SQL · FastAPI · Django · React",
        "DATA        NumPy · Pandas · Matplotlib · Seaborn · Plotly · EDA · statistics",
        "QUANT       BRAIN · alpha research · forecasting · macro data · risk · portfolio",
        "TOOLS       Git · Linux · Jupyter · Colab · VS Code · Docker · Raspberry Pi",
        "MATH        probability · linear algebra · calculus · Olympiad · problem solving",
    ]
    for index, value in enumerate(skill_lines):
        body += f'<text x="30" y="{546 + index * 16}" fill="#aab6c4" font-family="monospace" font-size="10">{escape(value)}</text>'
    body += '<text x="820" y="674" fill="#3dd6d0" font-family="monospace" font-size="10">open the interactive lab for hover states + cube controls →</text>'
    (ASSETS / "work-tree.svg").write_text(svg(width, height, "Mithilesh work tree and skill index", body), encoding="utf-8")


if __name__ == "__main__":
    cube_hero()
    cards()
    work_tree()
    print("Built cube hero, six project cards, and the work tree.")
