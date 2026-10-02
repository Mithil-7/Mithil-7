"""Fetch GitHub's contribution calendar and draw a solid-colour 3D SVG.

The GitHub Action passes its built-in GITHUB_TOKEN. For local runs use a token
with public read access, or pass --fixture with a previously saved JSON file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "contributions.json"
SVG_PATH = ROOT / "assets" / "contributions-3d.svg"
GRAPHQL_URL = "https://api.github.com/graphql"
LEVELS = {
    "NONE": ("#111923", "#182430", "#0b1016"),
    "FIRST_QUARTILE": ("#17453b", "#236552", "#102f2a"),
    "SECOND_QUARTILE": ("#227c64", "#31997a", "#175443"),
    "THIRD_QUARTILE": ("#4caf87", "#65c99d", "#2b805f"),
    "FOURTH_QUARTILE": ("#91e9bd", "#b2f4d3", "#5ab88a"),
}


QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
          }
        }
      }
    }
  }
}
"""


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_calendar(login: str, token: str) -> dict:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=365)
    payload = json.dumps({
        "query": QUERY,
        "variables": {"login": login, "from": iso_utc(start), "to": iso_utc(end)},
    }).encode("utf-8")
    request = Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "mithil-rubiks-profile",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"GitHub GraphQL request failed: {error}") from error
    if result.get("errors"):
        messages = "; ".join(item.get("message", "unknown GraphQL error") for item in result["errors"])
        raise RuntimeError(messages)
    user = result.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {login}")
    calendar = user["contributionsCollection"]["contributionCalendar"]
    return {
        "login": login,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "total": calendar["totalContributions"],
        "weeks": calendar["weeks"],
    }


def point(x: float, y: float, z: float = 0) -> tuple[float, float]:
    return x, y - z


def points(values: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in values)


def prism(x: float, y: float, height: float, palette: tuple[str, str, str], label: str,
          delay: float) -> str:
    # The footprint uses two axes: week (right) and weekday (up-right/down).
    p00 = (x, y)
    p10 = (x + 12, y)
    p11 = (x + 18, y + 6)
    p01 = (x + 6, y + 6)
    top = [point(*p00, height), point(*p10, height), point(*p11, height), point(*p01, height)]
    front = [p01, p11, p11, p01]
    side = [p10, p11, p11, p10]
    # Visible vertical faces are written explicitly to keep the graph SVG simple.
    front = [p01, p11, point(*p11, height), point(*p01, height)]
    side = [p10, p11, point(*p11, height), point(*p10, height)]
    title = escape(label)
    return (
        f'<g aria-label="{title}"><title>{title}</title>'
        f'<polygon points="{points(front)}" fill="{palette[2]}"/>'
        f'<polygon points="{points(side)}" fill="{palette[0]}"/>'
        f'<polygon points="{points(top)}" fill="{palette[1]}" stroke="#081018" stroke-width="1"/>'
        f'<animate attributeName="opacity" values="0;1" dur="0.45s" begin="{delay:.2f}s" fill="freeze"/>'
        "</g>"
    )


def make_svg(data: dict) -> str:
    width, height = 1120, 480
    body = (
        '<style>@media (prefers-reduced-motion: reduce) { .bar-animations { display: none; } }</style>'
        f'<text x="34" y="38" fill="#3dd6d0" font-family="monospace" font-size="12" font-weight="700">'
        f'MITHIL-7 / CONTRIBUTION FIELD</text>'
        f'<text x="34" y="82" fill="#f3f5f7" font-family="Arial, sans-serif" font-size="35" font-weight="700">'
        f'{data["total"]}</text>'
        '<text x="100" y="81" fill="#aab6c4" font-family="Arial, sans-serif" font-size="16">public contributions in the last year</text>'
        '<text x="34" y="108" fill="#aab6c4" font-family="monospace" font-size="11">'
        'x = week · y = weekday · z = contribution count</text>'
    )
    body += '<g class="bar-animations">'
    months: list[tuple[int, str]] = []
    index = 0
    for week_index, week in enumerate(data.get("weeks", [])):
        days = week.get("contributionDays", [])
        for day_index, day in enumerate(days):
            date = day["date"]
            if date[8:10] == "01" or (week_index == 0 and day_index == 0):
                months.append((week_index, date[:7]))
            count = int(day.get("contributionCount", 0))
            level = day.get("contributionLevel", "NONE")
            palette = LEVELS.get(level, LEVELS["NONE"])
            # The empty cells retain a small height so the whole lattice stays visible.
            bar_height = 3 if count == 0 else min(74, 6 + count * 3.4)
            # Isometric-ish lattice: weeks run left-to-right and weekdays
            # step down-right. The full 53-week field stays inside the canvas.
            x = 76 + week_index * 18 + day_index * 6
            y = 322 + day_index * 7
            delay = min(index * 0.003, 1.1)
            body += prism(x, y, bar_height, palette, f"{date}: {count} contributions", delay)
            index += 1
    body += "</g>"
    body += f'<path d="M70 374 L1080 374" stroke="#263241" stroke-width="2"/>'
    for week_index, month in months:
        x = 76 + week_index * 18
        body += f'<text x="{x}" y="406" fill="#aab6c4" font-family="monospace" font-size="11">{escape(month)}</text>'
    body += (
        '<g transform="translate(34 437)" font-family="monospace" font-size="10" fill="#aab6c4">'
        '<rect x="0" y="-10" width="12" height="8" fill="#111923"/><text x="18" y="-2">none</text>'
        '<rect x="94" y="-10" width="12" height="8" fill="#17453b"/><text x="112" y="-2">low</text>'
        '<rect x="175" y="-10" width="12" height="8" fill="#227c64"/><text x="193" y="-2">medium</text>'
        '<rect x="292" y="-10" width="12" height="8" fill="#4caf87"/><text x="310" y="-2">high</text>'
        '<rect x="385" y="-10" width="12" height="8" fill="#91e9bd"/><text x="403" y="-2">more</text>'
        '</g>'
        f'<text x="730" y="437" fill="#aab6c4" font-family="monospace" font-size="10">updated {escape(data["generated_at"][:10])}</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">'
        f'<title id="title">{escape(data["login"])} 3D GitHub contribution graph</title>'
        f'<rect width="{width}" height="{height}" rx="18" fill="#080b10"/>'
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="17" fill="none" stroke="#263241"/>'
        f"{body}</svg>"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", default="Mithil-7")
    parser.add_argument("--fixture", type=Path, help="Use saved calendar JSON instead of the GraphQL API")
    args = parser.parse_args()
    try:
        if args.fixture:
            data = json.loads(args.fixture.read_text(encoding="utf-8"))
        else:
            token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
            if not token:
                raise RuntimeError("Set GITHUB_TOKEN, or use --fixture for an offline build.")
            data = fetch_calendar(args.login, token)
        data["login"] = args.login
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
        DATA_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        SVG_PATH.write_text(make_svg(data), encoding="utf-8")
        print(f"Wrote {SVG_PATH} with {data['total']} contributions.")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"update_contributions.py: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
