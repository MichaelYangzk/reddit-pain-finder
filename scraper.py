#!/usr/bin/env python3
"""
Reddit Pain Finder - Scrape Reddit .json for user pain points & startup ideas.

Usage:
    python3 scraper.py <subreddit_name_or_url> [--posts N] [--comments N] [--min-score N]

Examples:
    python3 scraper.py smallbusiness
    python3 scraper.py https://www.reddit.com/r/SaaS/
    python3 scraper.py https://www.reddit.com/r/webdev/comments/abc123/some_post/
    python3 scraper.py SaaS --posts 30 --comments 200 --min-score 5
"""

import json
import sys
import time
import re
import argparse
import urllib.request
import urllib.error

HEADERS = {
    "User-Agent": "RedditPainFinder/1.0 (research tool; contact: research@mkyang.ai)"
}

def fetch_json(url):
    """Fetch JSON from a Reddit URL with rate limiting."""
    if not url.endswith(".json"):
        url = url.rstrip("/") + "/.json"

    # Add raw_json=1 to get unescaped HTML entities
    separator = "&" if "?" in url else "?"
    url += f"{separator}raw_json=1"

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(json.dumps({"error": "Rate limited by Reddit. Wait 60s and retry."}))
            sys.exit(1)
        raise


def parse_subreddit_input(raw):
    """Normalize input to a subreddit name or full post URL."""
    raw = raw.strip().rstrip("/")

    # Full post URL: https://www.reddit.com/r/SaaS/comments/xxx/...
    post_match = re.match(r"https?://(?:www\.)?reddit\.com(/r/\w+/comments/\w+[^\s]*)", raw)
    if post_match:
        return {"type": "post", "url": f"https://www.reddit.com{post_match.group(1)}"}

    # Subreddit URL: https://www.reddit.com/r/SaaS
    sub_match = re.match(r"https?://(?:www\.)?reddit\.com/r/(\w+)", raw)
    if sub_match:
        return {"type": "subreddit", "name": sub_match.group(1)}

    # r/SaaS or just SaaS
    name = re.sub(r"^r/", "", raw)
    if re.match(r"^\w+$", name):
        return {"type": "subreddit", "name": name}

    return None


def extract_comments(comment_data, depth=0, min_score=1):
    """Recursively extract comments from Reddit JSON comment tree."""
    comments = []

    if isinstance(comment_data, dict):
        items = comment_data.get("data", {}).get("children", [])
    elif isinstance(comment_data, list):
        items = comment_data
    else:
        return comments

    for item in items:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind", "")
        data = item.get("data", {})

        if kind == "t1":  # Comment
            body = data.get("body", "").strip()
            score = data.get("score", 0)
            author = data.get("author", "[deleted]")

            # Skip deleted/removed/bot comments
            if body in ("[deleted]", "[removed]", ""):
                continue
            if author in ("[deleted]", "AutoModerator"):
                continue
            if score < min_score:
                continue

            comments.append({
                "author": author,
                "score": score,
                "body": body[:2000],  # Cap length
                "depth": depth,
            })

            # Recurse into replies
            replies = data.get("replies", "")
            if isinstance(replies, dict):
                comments.extend(extract_comments(replies, depth + 1, min_score))

        elif kind == "more":
            # "Load more comments" — skip for now (would need extra requests)
            pass

    return comments


def scrape_post(url, min_score=1):
    """Scrape a single Reddit post + all comments."""
    data = fetch_json(url)

    if not isinstance(data, list) or len(data) < 2:
        return None

    post_data = data[0]["data"]["children"][0]["data"]
    comments_data = data[1]

    comments = extract_comments(comments_data, min_score=min_score)
    comments.sort(key=lambda c: c["score"], reverse=True)

    return {
        "title": post_data.get("title", ""),
        "selftext": post_data.get("selftext", "")[:3000],
        "score": post_data.get("score", 0),
        "num_comments": post_data.get("num_comments", 0),
        "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
        "comments": comments,
    }


def scrape_subreddit(name, max_posts=25, max_comments=150, min_score=2):
    """Scrape hot posts from a subreddit and collect top comments."""
    url = f"https://www.reddit.com/r/{name}/hot.json?limit={max_posts}"
    data = fetch_json(url)

    if not isinstance(data, dict):
        return None

    posts = data.get("data", {}).get("children", [])
    results = {
        "subreddit": name,
        "posts_scanned": 0,
        "total_comments_collected": 0,
        "posts": [],
    }

    all_comments = []

    for post_item in posts:
        post = post_item.get("data", {})

        # Skip stickied/pinned posts
        if post.get("stickied", False):
            continue

        permalink = post.get("permalink", "")
        if not permalink:
            continue

        post_url = f"https://www.reddit.com{permalink}"

        try:
            post_result = scrape_post(post_url, min_score=min_score)
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to fetch {post_url}: {e}\n")
            continue

        if post_result:
            results["posts"].append(post_result)
            all_comments.extend(post_result["comments"])
            results["posts_scanned"] += 1

        # Rate limit: Reddit allows ~1 req/sec for unauthenticated
        time.sleep(1.2)

        # Stop if we have enough comments
        if len(all_comments) >= max_comments:
            break

    # Sort all comments by score, take top N
    all_comments.sort(key=lambda c: c["score"], reverse=True)
    results["top_comments"] = all_comments[:max_comments]
    results["total_comments_collected"] = len(all_comments)

    return results


def main():
    parser = argparse.ArgumentParser(description="Reddit Pain Finder - scrape Reddit for user pain points")
    parser.add_argument("target", help="Subreddit name, r/name, or full Reddit URL")
    parser.add_argument("--posts", type=int, default=25, help="Max posts to scan (default: 25)")
    parser.add_argument("--comments", type=int, default=150, help="Max top comments to return (default: 150)")
    parser.add_argument("--min-score", type=int, default=2, help="Min comment score to include (default: 2)")

    args = parser.parse_args()

    parsed = parse_subreddit_input(args.target)
    if not parsed:
        print(json.dumps({"error": f"Cannot parse input: {args.target}"}))
        sys.exit(1)

    sys.stderr.write(f"[INFO] Scraping: {parsed}\n")

    if parsed["type"] == "post":
        result = scrape_post(parsed["url"], min_score=args.min_score)
    else:
        result = scrape_subreddit(
            parsed["name"],
            max_posts=args.posts,
            max_comments=args.comments,
            min_score=args.min_score,
        )

    if result is None:
        print(json.dumps({"error": "Failed to fetch data from Reddit"}))
        sys.exit(1)

    # Output JSON to stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
