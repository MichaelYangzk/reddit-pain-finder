#!/usr/bin/env python3
"""
Reddit Pain Finder v2.0 - Scrape Reddit for user pain points & startup ideas.

Features:
    - Pain signal classification (frustration, WTP, tool-switch, solution requests)
    - Pain scoring per comment (0-100 composite score)
    - Mirror fallback rotation (redlib mirrors when Reddit rate-limits)
    - RSS fallback when .json fails

Usage:
    python3 scraper.py <subreddit_name_or_url> [--posts N] [--comments N] [--min-score N]
    python3 scraper.py SaaS --posts 30 --comments 200 --score-pain

Examples:
    python3 scraper.py smallbusiness
    python3 scraper.py https://www.reddit.com/r/SaaS/
    python3 scraper.py https://www.reddit.com/r/webdev/comments/abc123/some_post/
    python3 scraper.py SaaS --posts 30 --comments 200 --min-score 5
    python3 scraper.py r/startups --score-pain
"""

import json
import sys
import time
import re
import argparse
import urllib.request
import urllib.error

HEADERS = {
    "User-Agent": "RedditPainFinder/2.0 (research tool; contact: research@mkyang.ai)"
}

# --- Pain Signal Detection Patterns ---
# Based on SubredditSignals 7-Signal System + Reddinbox WTP detection

PAIN_PATTERNS = {
    "frustration": [
        r"(?i)\b(hate|terrible|awful|worst|sucks?|broken|useless|garbage|nightmare|disaster)\b",
        r"(?i)\b(frustrat|annoy|infuriat|maddening|ridiculous|unacceptable)\w*\b",
        r"(?i)(why is it so hard|can'?t believe|sick of|tired of|fed up|give up|losing my mind)",
        r"(?i)(waste of time|waste of money|complete mess|what a joke|driving me crazy)",
    ],
    "solution_request": [
        r"(?i)(is there a tool|any(one|body) know.{0,20}(tool|app|service|solution))",
        r"(?i)(looking for|searching for|need.{0,15}(tool|app|service|solution|way to))",
        r"(?i)(how do (you|I|we)|what('s| is) the best way|recommend.{0,15}(tool|app|service))",
        r"(?i)(does (anyone|anybody).{0,20}(recommend|suggest|know))",
        r"(?i)(wish there was|if only there was|someone should build)",
    ],
    "tool_switch": [
        r"(?i)(switch(ing|ed)? from|migrat(ing|ed)? from|mov(ing|ed)? away from|replac(ing|ed))",
        r"(?i)(alternative(s)? to|instead of|better than|compared to)",
        r"(?i)(left|leaving|ditch(ing|ed)?|abandon(ing|ed)?|cancel(l?ed|l?ing)?).{0,30}(subscription|plan|tool|app|service)",
        r"(?i)(looking to replace|need.{0,10}replacement)",
    ],
    "willingness_to_pay": [
        r"(?i)(willing to pay|would pay|gladly pay|happy to pay|shut up and take my money)",
        r"(?i)(pay \$?\d+|worth \$?\d+|\$\d+.{0,10}(per|a|/)\s*(month|year|mo|yr))",
        r"(?i)(current(ly)? pay(ing)?|spend(ing)?.{0,15}\$?\d+|budget.{0,15}\$?\d+)",
        r"(?i)(take my money|instant buy|day.one (buy|purchase|subscriber))",
        r"(?i)(worth (the|every|it)|money well spent|best.{0,10}(investment|purchase))",
    ],
    "unmet_need": [
        r"(?i)(i wish|if only|it would be great if|would love (to|it|if))",
        r"(?i)(missing feature|doesn'?t (support|have|do)|no way to|can'?t even)",
        r"(?i)(should (have|be able|support)|why (can'?t|doesn'?t|isn'?t))",
        r"(?i)(deal ?breaker|blocker|showstopper|non.?starter)",
    ],
}

# Emotional intensity keywords (weighted)
INTENSITY_WORDS = {
    "extreme": (["hate", "nightmare", "disaster", "worst", "impossible", "furious",
                 "livid", "outraged", "broken", "scam"], 10),
    "high":    (["terrible", "awful", "useless", "frustrated", "angry", "unacceptable",
                 "ridiculous", "pathetic", "garbage", "trash"], 7),
    "medium":  (["annoying", "disappointing", "mediocre", "clunky", "confusing",
                 "slow", "buggy", "unreliable", "awkward", "tedious"], 4),
    "low":     (["wish", "hope", "prefer", "slightly", "minor", "small",
                 "okay", "decent", "fine"], 2),
}

# --- Mirror Fallback Rotation ---
REDDIT_MIRRORS = [
    "https://www.reddit.com",
    "https://old.reddit.com",
]


def fetch_json(url, retry_mirrors=True):
    """Fetch JSON from a Reddit URL with mirror fallback."""
    original_url = url

    if not url.endswith(".json"):
        url = url.rstrip("/") + "/.json"

    separator = "&" if "?" in url else "?"
    url += f"{separator}raw_json=1"

    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429 and retry_mirrors:
            sys.stderr.write(f"[WARN] 429 on {url}, trying mirrors...\n")
            for mirror in REDDIT_MIRRORS[1:]:
                try:
                    mirror_url = original_url.replace("https://www.reddit.com", mirror)
                    time.sleep(2)
                    return fetch_json(mirror_url, retry_mirrors=False)
                except Exception:
                    continue
            sys.stderr.write("[ERROR] All mirrors exhausted.\n")
            print(json.dumps({"error": "Rate limited by Reddit. All mirrors failed. Wait 60s and retry."}))
            sys.exit(1)
        if e.code == 429:
            raise
        raise
    except urllib.error.URLError as e:
        if retry_mirrors:
            sys.stderr.write(f"[WARN] URLError on {url}: {e}, trying mirrors...\n")
            for mirror in REDDIT_MIRRORS[1:]:
                try:
                    mirror_url = original_url.replace("https://www.reddit.com", mirror)
                    time.sleep(2)
                    return fetch_json(mirror_url, retry_mirrors=False)
                except Exception:
                    continue
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


def classify_pain_signals(text):
    """Classify a comment's pain signals using pattern matching."""
    signals = {}
    text_lower = text.lower()

    for signal_type, patterns in PAIN_PATTERNS.items():
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            matches.extend(found)
        if matches:
            signals[signal_type] = len(matches)

    return signals


def score_pain_intensity(text):
    """Score emotional intensity of text (0-10)."""
    text_lower = text.lower()
    max_intensity = 0

    for level, (words, score) in INTENSITY_WORDS.items():
        for word in words:
            if word in text_lower:
                max_intensity = max(max_intensity, score)

    return max_intensity


def compute_pain_score(comment):
    """Compute composite pain score (0-100) for a comment.

    Formula: (signal_breadth * 25) + (intensity * 5) + (engagement * 10)
    - signal_breadth: number of distinct signal types (0-4, capped)
    - intensity: emotional intensity (0-10)
    - engagement: log-scaled reddit score (0-5)
    """
    import math

    signals = comment.get("pain_signals", {})
    intensity = comment.get("pain_intensity", 0)
    reddit_score = comment.get("score", 0)

    # Signal breadth: how many different signal categories triggered (max 4)
    signal_breadth = min(len(signals), 4)

    # Engagement: log-scaled reddit score (0-5)
    engagement = min(math.log2(max(reddit_score, 1) + 1), 5)

    # Composite score
    score = (signal_breadth * 25) + (intensity * 5) + (engagement * 10)
    return min(round(score, 1), 100)


def enrich_comment_with_pain(comment):
    """Add pain classification and scoring to a comment dict."""
    body = comment.get("body", "")
    comment["pain_signals"] = classify_pain_signals(body)
    comment["pain_intensity"] = score_pain_intensity(body)
    comment["pain_score"] = compute_pain_score(comment)
    return comment


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


def generate_pain_summary(result):
    """Generate a pain analysis summary from scored comments."""
    comments = result.get("top_comments", [])
    if not comments:
        comments = []
        for post in result.get("posts", []):
            comments.extend(post.get("comments", []))

    # Only include comments with pain signals
    pain_comments = [c for c in comments if c.get("pain_score", 0) > 0]

    if not pain_comments:
        return {"total_pain_signals": 0, "signal_distribution": {}, "top_pain_comments": []}

    # Aggregate signal distribution
    signal_dist = {}
    for c in pain_comments:
        for sig_type in c.get("pain_signals", {}):
            signal_dist[sig_type] = signal_dist.get(sig_type, 0) + 1

    # Sort by pain score
    pain_comments.sort(key=lambda c: c.get("pain_score", 0), reverse=True)

    # Top 20 highest-pain comments
    top_pain = []
    for c in pain_comments[:20]:
        top_pain.append({
            "body": c["body"][:500],
            "score": c["score"],
            "pain_score": c["pain_score"],
            "pain_signals": c["pain_signals"],
            "pain_intensity": c["pain_intensity"],
        })

    return {
        "total_pain_signals": len(pain_comments),
        "total_comments_analyzed": len(comments),
        "pain_ratio": round(len(pain_comments) / max(len(comments), 1), 3),
        "signal_distribution": signal_dist,
        "avg_pain_score": round(sum(c["pain_score"] for c in pain_comments) / max(len(pain_comments), 1), 1),
        "top_pain_comments": top_pain,
    }


def main():
    parser = argparse.ArgumentParser(description="Reddit Pain Finder v2 - scrape Reddit for user pain points")
    parser.add_argument("target", help="Subreddit name, r/name, or full Reddit URL")
    parser.add_argument("--posts", type=int, default=25, help="Max posts to scan (default: 25)")
    parser.add_argument("--comments", type=int, default=150, help="Max top comments to return (default: 150)")
    parser.add_argument("--min-score", type=int, default=2, help="Min comment score to include (default: 2)")
    parser.add_argument("--score-pain", action="store_true",
                        help="Enable pain signal detection & scoring (adds pain_score, pain_signals, pain_intensity to each comment)")

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

    # Enrich with pain scoring if requested
    if args.score_pain:
        sys.stderr.write("[INFO] Scoring pain signals...\n")

        # Score all comments in posts
        for post in result.get("posts", []):
            post["comments"] = [enrich_comment_with_pain(c) for c in post.get("comments", [])]

        # Score top_comments
        if "top_comments" in result:
            result["top_comments"] = [enrich_comment_with_pain(c) for c in result["top_comments"]]

        # Add pain summary
        result["pain_summary"] = generate_pain_summary(result)
        sys.stderr.write(f"[INFO] Pain signals found: {result['pain_summary']['total_pain_signals']}\n")

    # Output JSON to stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
