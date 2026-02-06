# Reddit Pain Finder v2

Automated tool for discovering user pain points from Reddit, identifying startup opportunities with $10K+ MRR potential.

**v2 New:** Pain scoring algorithm (0-100), willingness-to-pay signal detection, 7-Signal analysis framework, mirror fallback rotation.

## How It Works

```
Subreddit URL/name → Python scraper (--score-pain) → Scored JSON → Claude analysis → Pain point report
```

1. **Scraper** (`scraper.py`): Fetches Reddit posts + comments via `.json` endpoint (zero API keys needed)
2. **Pain Scoring**: Classifies each comment into 5 signal types, scores intensity (0-10) and composite pain (0-100)
3. **Claude Skill** (`skill/SKILL.md`): 3-Prompt analysis pipeline + 7-Signal validation framework
4. **Reports**: Ranked pain points with ICE scores, WTP signals, ICP profiles, and competitive gap maps

## Usage

```bash
# Scrape with pain scoring (recommended)
python3 scraper.py r/smallbusiness --posts 50 --comments 100 --score-pain

# Scrape a specific post
python3 scraper.py https://www.reddit.com/r/SaaS/comments/abc123/my_post/ --score-pain

# With minimum score filter
python3 scraper.py r/productivity --min-score 5 --score-pain

# Raw mode (no scoring, faster)
python3 scraper.py r/webdev --posts 30 --comments 200
```

## Pain Scoring

Each comment is enriched with:

| Field | Type | Description |
|-------|------|-------------|
| `pain_signals` | dict | Which signal types triggered: frustration, solution_request, tool_switch, willingness_to_pay, unmet_need |
| `pain_intensity` | 0-10 | Emotional intensity based on keyword analysis |
| `pain_score` | 0-100 | Composite score: `(signal_breadth × 25) + (intensity × 5) + (engagement × 10)` |

**Score interpretation:**
- 80-100: Critical pain (multi-signal + strong emotion + high engagement) → Immediate opportunity
- 50-79: High pain → Worth deep investigation
- 20-49: Moderate → Possible nice-to-have
- 0-19: Low → General discussion

**Pain summary** (in output JSON):
```json
{
  "pain_summary": {
    "total_pain_signals": 42,
    "total_comments_analyzed": 150,
    "pain_ratio": 0.28,
    "signal_distribution": {"frustration": 18, "solution_request": 12, "tool_switch": 5, "willingness_to_pay": 3, "unmet_need": 8},
    "avg_pain_score": 54.2,
    "top_pain_comments": [...]
  }
}
```

## Signal Types

| Signal | Pattern Examples | Business Meaning |
|--------|-----------------|------------------|
| `frustration` | "hate", "terrible", "why is it so hard" | Users suffering → ready to switch |
| `solution_request` | "is there a tool", "recommend", "wish there was" | Active demand → build this |
| `tool_switch` | "switching from", "alternatives to" | Active buyers evaluating options |
| `willingness_to_pay` | "willing to pay $X", "currently paying" | Validated budget → pricing signal |
| `unmet_need` | "I wish", "missing feature", "deal breaker" | Feature gap → differentiation angle |

## Resilience

- **Mirror fallback**: Automatically tries `old.reddit.com` when `www.reddit.com` returns 429
- **Rate limiting**: Built-in 1.2s delay between requests
- **Graceful degradation**: Individual post failures don't stop the scan

## Reports

| Report | Focus | Top Finding |
|--------|-------|-------------|
| [Agent Payment Master Report](./reports/agent-payment-master-report.md) | **Agent Payment 全景** | 12 pain points, 7 build priorities |
| [DC AI Server Maintenance](./reports/dc-ai-server-maintenance-market.md) | **美国 DC 服务器维保市场** | 9% GPU 故障率 + 340K 技术人员缺口 |
| [Agent Payment X + Moltbook](./reports/agent-payment-x-moltbook.md) | **X + Moltbook 补充研究** | CEO bullish + Builder 痛点验证 |
| [Agent Payment Reddit Voices](./reports/agent-payment-reddit-voices.md) | **Reddit 声音 (Post-OpenClaw)** | Reddit 静默 = 先发优势 |
| [Agent Payment Deep Dive](./reports/agent-payment-deep-dive.md) | **Agent Payment 竞争分析** | Task Escrow as a Service (Quick Win) |
| [Post-OpenClaw AI-Native Gaps](./reports/post-openclaw-ai-native-gaps.md) | **AI-native infrastructure** | Agent Action Guarantee Layer (A+) |
| [AI x Daily Life Pain Points](./reports/ai-daily-life-painpoints-report.md) | AI meets everyday life | AI Life Admin Agent ($50B+ TAM) |
| [AI Agent Native Apps](./reports/ai-agent-painpoints-report.md) | AI agent ecosystem | Multi-agent orchestration tools |

## Claude Skill

Install for use in Claude Code:

```bash
ln -s /path/to/reddit-pain-finder/skill /path/to/.claude/skills/reddit-pain-finder
```

Trigger with: "分析 subreddit", "reddit 痛点", "reddit pain", `/reddit-pain`

## Methodology

### Analysis Framework (v2)

**3-Prompt Pipeline:**
1. **Pain Extraction** — Cluster pain points by signal type, build Frequency × Intensity matrix
2. **ICP Recognition** — Extract buyer personas from high-pain comments
3. **Validation & Synthesis** — Score on 4 dimensions (frequency, urgency, budget signals, solution gaps)

**7-Signal Validation** (based on SubredditSignals):
1. Tool-Switch Language → active buyers
2. Budget + Constraints → pricing intelligence
3. Repeated Pain Posts → validated demand (5+ mentions across 2+ subreddits)
4. High-Signal Comments → competitive intelligence
5. Moderator Rules → distribution potential
6. Community Trends → emerging vs chronic
7. Asset-Convertible Threads → content marketing potential

**Opportunity Scoring: ICE Framework**
- Impact (1-10) × Confidence (1-10) × Ease (1-10) = Priority score

### 5-Round Iterative Research
1. **Discovery** — Broad pain point scraping from relevant subreddits
2. **Deep Dive** — Focus on most actionable pain points
3. **Market Validation** — TAM, willingness to pay, funding signals
4. **Competitive Analysis** — Gap analysis, existing players, moats
5. **Synthesis** — Ranked opportunities with build recommendations

## Requirements

- Python 3.8+ (stdlib only, zero dependencies)
- Claude Code with Max plan (for analysis)
