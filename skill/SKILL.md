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

## 注意事项

- Reddit 对未认证请求限流约 1 req/sec，脚本已内置延迟
- 如果遇到 429 错误，等 60 秒重试
- 输出是 JSON 到 stdout，stderr 有进度信息
