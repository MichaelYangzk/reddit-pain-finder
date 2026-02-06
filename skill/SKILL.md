---
name: reddit-pain-finder
description: |
  分析 Reddit 用户痛点和创业机会。当用户提到 "分析 subreddit"、"reddit 痛点"、
  "reddit pain"、"找痛点"、"startup ideas from reddit" 时自动激活。
  也可通过 /reddit-pain 命令手动触发。
argument-hint: "[subreddit name or Reddit URL]"
allowed-tools: Bash, Read, WebFetch, WebSearch
---

# Reddit Pain Finder v2

基于 Reddit JSON Hack + 多平台信号融合方法论，自动抓取用户真实痛点，发现创业机会。

**v2 新增：** 痛点评分算法（0-100）、付费意愿信号检测、7-Signal 分析框架、mirror 容错。

## 工作流程

### Step 1: 获取数据

运行 scraper 抓取 Reddit 数据（**始终加 `--score-pain` 启用痛点评分**）：

```bash
python3 /workspace/tools/reddit-pain-finder/scraper.py "<用户提供的 subreddit 或 URL>" --posts 25 --comments 150 --min-score 2 --score-pain
```

参数说明：
- 输入支持：subreddit 名称（`SaaS`）、`r/SaaS`、完整 URL
- `--posts N`: 扫描帖子数（默认 25）
- `--comments N`: 返回 top 评论数（默认 150）
- `--min-score N`: 最低评论分数（默认 2，过滤垃圾）
- `--score-pain`: **启用痛点评分**（为每条评论添加 pain_score, pain_signals, pain_intensity）

**注意：** 脚本每个帖子间隔 1.2s 避免被 Reddit 限流。扫描 25 帖大约需要 30-40s，提前告知用户。遇到 429 自动尝试 mirror（old.reddit.com）。

### Step 2: 分析痛点（3-Prompt 方法论）

拿到 JSON 数据后，按以下 3-Prompt 流水线分析：

#### Prompt 1: 痛点提取与分类

利用 scraper 输出的 `pain_summary` 字段，重点分析：

1. **痛点聚类** — 将相似痛点归类。用 `pain_signals` 分类：
   - `frustration`: 用户抱怨什么？情绪多强烈？
   - `solution_request`: 用户在找什么解决方案？
   - `tool_switch`: 用户想从什么工具迁走？为什么？
   - `willingness_to_pay`: 谁愿意付钱？付多少？
   - `unmet_need`: 什么功能/产品不存在？

2. **频率 × 强度矩阵** — 用 Pain Point Matrix 评估每个痛点聚类：
   - X 轴: 频率 (1-10) — 在数据中出现了多少次？
   - Y 轴: 强度 (1-10) — 用户的情绪有多激烈？（参考 `pain_intensity`）
   - **优先关注右上象限**（高频 + 高强度）

3. **付费意愿信号** — 特别标注以下信号：
   - 直接报价: "willing to pay $X", "would pay $X/month"
   - 间接信号: "current tool costs too much", "worth every penny"
   - 工具替换: "switching from X because...", "alternatives to Y"

#### Prompt 2: ICP（理想客户画像）识别

从高痛点评论中提取用户画像：
- 角色/职位指标
- 公司阶段（startup / scale-up / enterprise）
- 技术栈提及
- 预算约束
- 决策权

输出 2-3 个 buyer persona。

#### Prompt 3: 验证与综合

用 4 维度评分 (1-10) 验证每个痛点聚类：
- **频率** — 出现次数（阈值: 8+ 次 = 验证通过）
- **紧迫性** — 用户情绪强度
- **预算信号** — 付费意愿证据
- **方案缺口** — 现有工具是否失败？

**验证标准：** 时效性 (<90天)、变通方案证据、ICP 一致性。

### Step 3: 7-Signal 深度分析

基于 SubredditSignals 7-Signal System 深度评估：

| # | 信号 | 含义 | 数据来源 |
|---|------|------|----------|
| 1 | **Tool-Switch Language** | "switching from X" = 活跃买家 | `tool_switch` signals |
| 2 | **Budget + Constraints** | 价格上限、团队规模、合规需求 | `willingness_to_pay` signals |
| 3 | **Repeated Pain Posts** | 同一投诉在 2+ 个 subreddit 出现 5+ 次 = 真实需求 | 跨 subreddit 交叉验证 |
| 4 | **High-Signal Comments** | 高赞评论分享结果和失败尝试 | `pain_score` > 60 |
| 5 | **Moderator Rules** | 社区是否允许推广？是否可以做客户开发？ | 手动检查 |
| 6 | **Community Trends** | 上升趋势 vs 长期存在的问题 | 时间维度分析 |
| 7 | **Asset-Convertible Threads** | 讨论可转化为 FAQ、对比页、视频脚本 | 内容复用评估 |

### Step 4: 输出分析报告

格式：

```
## r/{subreddit} 痛点分析报告 v2

**扫描范围:** X 帖子 / Y 条评论 / Z 条有痛点信号
**平均痛点分数:** {avg_pain_score}/100
**痛点覆盖率:** {pain_ratio}%

### 痛点信号分布

| 信号类型 | 出现次数 | 占比 |
|----------|---------|------|
| frustration | N | X% |
| solution_request | N | X% |
| tool_switch | N | X% |
| willingness_to_pay | N | X% |
| unmet_need | N | X% |

### Top 痛点排名（Pain Point Matrix: 频率 × 强度）

| # | 痛点聚类 | 提及次数 | 平均 pain_score | 信号类型 | 代表性评论 |
|---|---------|---------|----------------|---------|-----------|
| 1 | ... | N | XX.X | frustration, WTP | "原文引用" |

### 付费意愿信号

| # | 信号 | 预估金额 | 来源评论 |
|---|------|---------|---------|
| 1 | "willing to pay $50/mo for..." | $50/mo | u/xxx (score: 45) |

### ICP 画像

**Persona 1: [名称]**
- 角色: ...
- 公司阶段: ...
- 预算: ...
- 核心痛点: ...

### 创业机会（ICE 评分）

**机会 1: [产品名称建议]** — ICE: X/30
- Impact (1-10): ...
- Confidence (1-10): ...
- Ease (1-10): ...
- 解决的痛点: ...
- 目标用户: ...
- 商业模式: SaaS / marketplace / tool
- 预估 TAM: ...
- 现有竞品: ...
- 差异化方向: ...
- 7-Signal 验证: ✅ Signal 1, ✅ Signal 3, ❌ Signal 5

### 竞品弱点地图

| 竞品 | 用户投诉 | 提及次数 | 机会 |
|------|---------|---------|------|
| Tool X | "slow", "expensive" | N | 做更快更便宜的版本 |

### 下一步行动建议
- 值得深挖的 subreddit
- 可以做的快速验证（DM 高痛点用户 / landing page / poll）
- 竞品差异化切入点
```

## 高级用法

- 分析单个帖子（深度评论挖掘）：传入帖子完整 URL
- 调整参数：`--posts 50 --comments 300` 扫描更多
- 降低门槛：`--min-score 1` 看更多长尾评论
- 不加 `--score-pain` 可以获取原始数据（更快，适合大量抓取后离线分析）

## 多源并行研究模式

当研究涉及多个 subreddit 时，使用 Task agent 并行抓取：

1. **为每个 subreddit 启动独立 Task agent** — 并行执行，互不阻塞
2. **每个 agent 完整完成后返回** — 不要中途汇报
3. **最后汇总所有结果** — 编译成单一报告

```
# 示例：并行研究 3 个 subreddit
Task agent 1: scrape r/cryptocurrency → 返回 JSON
Task agent 2: scrape r/defi → 返回 JSON
Task agent 3: scrape r/fintech → 返回 JSON
↓
汇总分析 → 交叉验证 Signal 3 (Repeated Pain Posts) → 输出报告
```

**优势：** 并行加速，单个 source 失败不影响整体。跨 subreddit 交叉验证可触发 Signal 3。

## 多源信息采集

除了 Reddit，还应采集以下信息源作为补充：

### 信息源优先级

| Source | 方法 | 适合内容 |
|--------|------|----------|
| **Reddit** | scraper.py --score-pain | 用户痛点、长篇讨论、付费意愿信号 |
| **X (Twitter)** | WebSearch `site:x.com` | 实时动态、Builder 观点、行业 KOL |
| **Hacker News** | WebFetch `news.ycombinator.com/item?id=X` | 技术社区、创业者视角 |
| **Moltbook** | Moltbook REST API | AI Agent 社区讨论、crypto-native 视角 |
| **IndieHackers** | WebSearch `site:indiehackers.com` | 创业者经验、MRR 数据 |
| **DEV.to** | WebSearch `site:dev.to` | 技术深度、实操经验 |
| **Product Hunt** | WebSearch `site:producthunt.com` | 产品反馈、竞品分析 |
| **行业博客** | WebSearch | 分析报告、市场数据 |

### X (Twitter) 搜索技巧

```bash
# WebSearch 查询模板
"site:x.com [topic] 2026"
"site:x.com [topic] from:@kol_handle"
"site:x.com [topic] AI agent payment"
```

### Moltbook API 调用

```bash
# 获取 feed
curl -s "https://www.moltbook.com/api/v1/feed?sort=hot&limit=25" \
  -H "Authorization: Bearer $MOLTBOOK_API_KEY"

# 搜索话题
curl -s "https://www.moltbook.com/api/v1/search?q=[topic]" \
  -H "Authorization: Bearer $MOLTBOOK_API_KEY"
```

**Moltbook credentials:** `~/.config/moltbook/credentials.json`

---

## 自主研究流水线（Self-Healing Pipeline）

完全自主运行的研究流水线，自动检测失败并重试：

### 架构

```
Coordinator Agent (监控 + 汇总)
    ├── Task Agent 1: Reddit scraper --score-pain (3 fallback strategies)
    ├── Task Agent 2: X/Twitter search
    ├── Task Agent 3: Moltbook API
    ├── Task Agent 4: HN / IndieHackers / DEV.to
    └── Task Agent 5: Additional subreddits
            ↓
    Aggregate → Cross-validate Signal 3 → Pain Point Matrix → Markdown report
```

### 关键特性

1. **每个 agent 3 层 fallback**
   - Strategy 1: Primary source (Reddit/X/Moltbook)
   - Strategy 2: WebSearch fallback
   - Strategy 3: WebFetch specific threads/posts

2. **Coordinator 监控逻辑**
   - 成功: 汇总结果到报告
   - 部分失败 (≤2 agents): 继续，用成功的数据
   - 大面积失败 (>2 agents): 暂停，询问用户

3. **痛点交叉验证**
   - 同一痛点在 2+ 个 source 出现 = 高置信度
   - pain_score > 60 + WTP signal = 高优先级机会
   - 竞品投诉 + unmet_need = 差异化切入点

### 启动模板

```
Create an autonomous research pipeline: spawn 5 parallel Task agents
to scrape different subreddits for pain points about [TOPIC].

Each agent should use --score-pain flag and attempt 3 different
scraping strategies if the first fails.

A coordinator agent monitors all tasks, aggregates successful results,
cross-validates pain points across sources using the Pain Point Matrix
(frequency × intensity), and generates a ranked opportunity report.

If more than 2 agents fail completely, pause and ask for guidance.
```

### 适用场景

- 大规模痛点研究（5+ subreddits）
- 需要 overnight 运行的深度调研
- Reddit 限流严重时的弹性抓取

## 痛点评分算法说明

scraper v2 为每条评论计算以下指标：

### 信号分类 (`pain_signals`)

| 类型 | 检测的语言模式 |
|------|-------------|
| `frustration` | "hate", "terrible", "worst", "frustrated", "why is it so hard" |
| `solution_request` | "is there a tool", "looking for", "recommend", "wish there was" |
| `tool_switch` | "switching from", "alternatives to", "replacing", "left X for" |
| `willingness_to_pay` | "willing to pay", "would pay $X", "currently paying", "worth $X" |
| `unmet_need` | "I wish", "missing feature", "doesn't support", "deal breaker" |

### 强度评分 (`pain_intensity`, 0-10)

基于情绪关键词权重：
- 10: hate, nightmare, disaster, impossible
- 7: terrible, awful, frustrated, unacceptable
- 4: annoying, disappointing, buggy, slow
- 2: wish, hope, prefer, minor

### 综合评分 (`pain_score`, 0-100)

公式: `(signal_breadth × 25) + (intensity × 5) + (engagement × 10)`
- signal_breadth: 触发的信号类别数 (0-4)
- intensity: 情绪强度 (0-10)
- engagement: Reddit 评分的 log 值 (0-5)

**解读:**
- 80-100: 极高痛点（多信号 + 强情绪 + 高赞）→ 立即关注
- 50-79: 高痛点 → 值得深入研究
- 20-49: 中等 → 可能是 nice-to-have
- 0-19: 低痛点 → 一般讨论

## 注意事项

- Reddit 对未认证请求限流约 1 req/sec，脚本已内置延迟
- 如果遇到 429 错误，脚本自动尝试 old.reddit.com mirror
- 所有 mirror 失败后，等 60 秒重试
- 输出是 JSON 到 stdout，stderr 有进度信息
- `--score-pain` 不增加网络请求，仅在本地处理，无额外延迟
