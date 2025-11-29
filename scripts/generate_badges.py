import os
import requests
from pathlib import Path


def get_leetcode_solved(username: str) -> int:
    url = "https://leetcode.com/graphql"
    query = """
    query userProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    variables = {"username": username}
    resp = requests.post(url, json={"query": query, "variables": variables}, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
    total = next(item["count"] for item in stats if item["difficulty"] == "All")
    return total


def get_codeforces_solved(handle: str) -> int:
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    submissions = resp.json()["result"]

    solved = set()
    for sub in submissions:
        if sub.get("verdict") == "OK":
            problem = sub["problem"]
            key = f'{problem.get("contestId", 0)}-{problem.get("index", "")}'
            solved.add(key)
    return len(solved)


def make_badge(label: str, value: int, color: str = "#007ec6") -> str:
    """
    Very simple SVG badge (Shields-style layout but hand-rolled).
    """
    left_text = label
    right_text = str(value)

    # rough width calculations (8px per character as a simple heuristic)
    left_width = max(40, 7 * len(left_text) + 20)
    right_width = max(40, 7 * len(right_text) + 20)
    total_width = left_width + right_width

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="smooth" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="round">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#round)">
    <rect width="{left_width}" height="20" fill="#555"/>
    <rect x="{left_width}" width="{right_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#smooth)"/>
  </g>
  <g fill="#fff" text-anchor="middle"
     font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{left_width / 2}" y="14">{left_text}</text>
    <text x="{left_width + right_width / 2}" y="14">{right_text}</text>
  </g>
</svg>
"""
    return svg


def main():
    lc_user = "user6448Ai"
    cf_handle = "Woogles"

    print(f"Fetching stats for LeetCode: {lc_user}, Codeforces: {cf_handle}")

    lc_count = get_leetcode_solved(lc_user)
    cf_count = get_codeforces_solved(cf_handle)

    print(f"LeetCode solved: {lc_count}")
    print(f"Codeforces solved: {cf_count}")

    badges_dir = Path("badges")
    badges_dir.mkdir(exist_ok=True)

    lc_svg = make_badge("LeetCode", lc_count, "#ffa116")
    cf_svg = make_badge("Codeforces", cf_count, "#1f8acb")

    (badges_dir / "leetcode_solved.svg").write_text(lc_svg, encoding="utf-8")
    (badges_dir / "codeforces_solved.svg").write_text(cf_svg, encoding="utf-8")


if __name__ == "__main__":
    main()
