# Reddit Pain Finder

Automated tool for discovering user pain points from Reddit, identifying startup opportunities with $10K+ MRR potential.

## How It Works

```
Subreddit URL/name → Python scraper → Structured JSON → Claude analysis → Pain point report
```

1. **Scraper** (`scraper.py`): Fetches Reddit posts + comments via the `.json` endpoint hack (zero API keys needed)
2. **Claude Skill** (`skill/SKILL.md`): Triggers analysis directly in Claude Code conversations
3. **Reports**: Ranked pain points with TAM estimates, competitive gaps, and build recommendations

## Usage

```bash
# Scrape a subreddit
python3 scraper.py r/smallbusiness --posts 50 --comments 100

# Scrape a specific post
python3 scraper.py https://www.reddit.com/r/SaaS/comments/abc123/my_post/

# With minimum score filter
python3 scraper.py r/productivity --min-score 5
```

## Reports

| Report | Focus | Top Finding |
|--------|-------|-------------|
| [Agent Payment Reddit Voices](./reports/agent-payment-reddit-voices.md) | **Reddit 声音 (Post-OpenClaw)** | Reddit 静默 = 先发优势 |
| [Agent Payment Deep Dive](./reports/agent-payment-deep-dive.md) | **Agent Payment 竞争分析** | Task Escrow as a Service (Quick Win) |
| [Post-OpenClaw AI-Native Gaps](./reports/post-openclaw-ai-native-gaps.md) | **AI-native infrastructure** | Agent Action Guarantee Layer (A+) |
| [AI x Daily Life Pain Points](./reports/ai-daily-life-painpoints-report.md) | AI meets everyday life | AI Life Admin Agent ($50B+ TAM) |
| [AI Agent Native Apps](./reports/ai-agent-painpoints-report.md) | AI agent ecosystem | Multi-agent orchestration tools |
| [Auto Title Capitalization](./reports/auto-title-capitalization-report.md) | Title processing automation | Cross-platform title formatting |

## Claude Skill

Install for use in Claude Code:

```bash
ln -s /path/to/reddit-pain-finder/skill /path/to/.claude/skills/reddit-pain-finder
```

Trigger with: "分析 subreddit", "reddit 痛点", "reddit pain", `/reddit-pain`

## Methodology

5-round iterative research:
1. **Discovery** — Broad pain point scraping from relevant subreddits
2. **Deep Dive** — Focus on most actionable pain points
3. **Market Validation** — TAM, willingness to pay, funding signals
4. **Competitive Analysis** — Gap analysis, existing players, moats
5. **Synthesis** — Ranked opportunities with build recommendations

## Requirements

- Python 3.8+ (stdlib only, zero dependencies)
- Claude Code with Max plan (for analysis)
