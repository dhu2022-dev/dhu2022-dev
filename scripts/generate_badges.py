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
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com/",
        "User-Agent": "Mozilla/5.0 (GitHub Actions badge updater)",
    }

    resp = requests.post(
        url,
        json={"query": query, "variables": {"username": username}},
        headers=headers,
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    matched = (data.get("data") or {}).get("matchedUser")
    if not matched:
        raise RuntimeError(f"LeetCode user not found or blocked: {username}. Response: {data}")

    stats = matched["submitStats"]["acSubmissionNum"]
    total = next((item["count"] for item in stats if item["difficulty"] == "All"), None)
    if total is None:
        raise RuntimeError(f"Could not parse LeetCode stats for {username}. Got: {stats}")
    return int(total)


def get_codeforces_solved(handle: str) -> int:
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("status") != "OK":
        raise RuntimeError(f"Codeforces API error for {handle}: {payload}")
    submissions = payload["result"]

    solved = set()
    for sub in submissions:
        if sub.get("verdict") == "OK":
            p = sub["problem"]
            solved.add(f'{p.get("contestId", 0)}-{p.get("index", "")}')
    return len(solved)


def make_badge(label: str, value: int, color: str) -> str:
    left_text = label
    right_text = str(value)

    left_width = max(40, 7 * len(left_text) + 20)
    right_width = max(40, 7 * len(right_text) + 20)
    total_width = left_width + right_width

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
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


def main():
    lc_user = os.getenv("LEETCODE_USERNAME", "user6448Ai")
    cf_handle = os.getenv("CODEFORCES_HANDLE", "Woogles")

    print(f"Fetching stats for LeetCode={lc_user}, Codeforces={cf_handle}")

    lc_count = get_leetcode_solved(lc_user)
    cf_count = get_codeforces_solved(cf_handle)

    badges_dir = Path("badges")
    badges_dir.mkdir(exist_ok=True)

    (badges_dir / "leetcode_solved.svg").write_text(make_badge("LeetCode", lc_count, "#ffa116"), encoding="utf-8")
    (badges_dir / "codeforces_solved.svg").write_text(make_badge("Codeforces", cf_count, "#1f8acb"), encoding="utf-8")

    print("Wrote badges/*.svg successfully.")


if __name__ == "__main__":
    main()
