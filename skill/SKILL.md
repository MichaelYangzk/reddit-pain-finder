---
name: reddit-pain-finder
description: |
  分析 Reddit 用户痛点和创业机会。当用户提到 "分析 subreddit"、"reddit 痛点"、
  "reddit pain"、"找痛点"、"startup ideas from reddit" 时自动激活。
  也可通过 /reddit-pain 命令手动触发。
argument-hint: "[subreddit name or Reddit URL]"
allowed-tools: Bash, Read, WebFetch
---

# Reddit Pain Finder

基于 "Reddit JSON Hack" 方法论，自动抓取 subreddit 用户真实痛点，发现创业机会。

## 工作流程

### Step 1: 获取数据

运行 scraper 抓取 Reddit 数据：

```bash
python3 /workspace/tools/reddit-pain-finder/scraper.py "<用户提供的 subreddit 或 URL>" --posts 25 --comments 150 --min-score 2
```

参数说明：
- 输入支持：subreddit 名称（`SaaS`）、`r/SaaS`、完整 URL
- `--posts N`: 扫描帖子数（默认 25）
- `--comments N`: 返回 top 评论数（默认 150）
- `--min-score N`: 最低评论分数（默认 2，过滤垃圾）

**注意：** 脚本每个帖子间隔 1.2s 避免被 Reddit 限流。扫描 25 帖大约需要 30-40s，提前告知用户。

### Step 2: 分析痛点

拿到 JSON 数据后，直接在对话中分析。重点关注：

1. **痛点提取** — 用户在抱怨什么？什么功能不好用？什么需求没被满足？
2. **频率统计** — 同类痛点出现几次？高分评论代表更多人认同
3. **情感强度** — 用词越激烈（"hate", "terrible", "wish", "need"）= 付费意愿越强
4. **现有方案** — 他们现在用什么解决？有没有提到竞品？

### Step 3: 输出分析报告

格式：

```
## r/{subreddit} 痛点分析报告

**扫描范围:** X 帖子 / Y 条评论

### Top 痛点排名

| # | 痛点 | 提及次数 | 情感强度 | 代表性评论 |
|---|------|---------|---------|-----------|
| 1 | ... | N | 高/中/低 | "原文引用" |

### 创业机会

**机会 1: [产品名称建议]**
- 解决的痛点: ...
- 目标用户: ...
- 商业模式: SaaS / marketplace / tool
- 预估 TAM: ...
- 现有竞品: ...
- 差异化方向: ...

**机会 2: ...**

### 下一步行动建议
- 值得深挖的 subreddit
- 可以做的快速验证
- landing page 测试方向
```

## 高级用法

- 分析单个帖子（深度评论挖掘）：传入帖子完整 URL
- 调整参数：`--posts 50 --comments 300` 扫描更多
- 降低门槛：`--min-score 1` 看更多长尾评论

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
汇总分析 → 输出报告
```

**优势：** 并行加速，单个 source 失败不影响整体

## 自主研究流水线（Self-Healing Pipeline）

完全自主运行的研究流水线，自动检测失败并重试：

### 架构

```
Coordinator Agent (监控 + 汇总)
    ├── Task Agent 1: r/subreddit1 (3 fallback strategies)
    ├── Task Agent 2: r/subreddit2 (3 fallback strategies)
    ├── Task Agent 3: r/subreddit3 (3 fallback strategies)
    ├── Task Agent 4: r/subreddit4 (3 fallback strategies)
    └── Task Agent 5: r/subreddit5 (3 fallback strategies)
            ↓
    Aggregate successful results → Markdown report → Email
```

### 关键特性

1. **每个 agent 3 层 fallback**
   - Strategy 1: Reddit .json endpoint
   - Strategy 2: WebSearch fallback
   - Strategy 3: WebFetch specific threads

2. **Coordinator 监控逻辑**
   - 成功: 汇总结果到报告
   - 部分失败 (≤2 agents): 继续，用成功的数据
   - 大面积失败 (>2 agents): 暂停，询问用户

3. **TodoWrite 全程追踪**
   - 每个 agent 状态实时更新
   - 失败原因记录
   - 最终报告状态

### 启动模板

```
Create an autonomous research pipeline: spawn 5 parallel Task agents
to scrape different subreddits for pain points about [TOPIC].

Each agent should attempt 3 different scraping strategies if the first fails.

A coordinator agent monitors all tasks, aggregates successful results
into a markdown report, and emails it to me.

If more than 2 agents fail completely, pause and ask for guidance.

Use TodoWrite to track progress across all agents.
```

### 适用场景

- 大规模痛点研究（5+ subreddits）
- 需要 overnight 运行的深度调研
- Reddit 限流严重时的弹性抓取

## 注意事项

- Reddit 对未认证请求限流约 1 req/sec，脚本已内置延迟
- 如果遇到 429 错误，等 60 秒重试
- 输出是 JSON 到 stdout，stderr 有进度信息
