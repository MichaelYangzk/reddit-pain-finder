# Post-OpenClaw Era: AI-Native Infrastructure Gaps

**Date:** 2026-02-05
**Thesis:** 新科技让旧需求不值得做。本报告聚焦**只因AI存在才产生的需求** — Model-bot解决不了，Claude Code也做不到。

---

## The Boris Cherny Insight

> "It's a lot more about the idea now than it is about the details."
> — Boris Cherny, Creator of Claude Code

Claude Code 让 100% 代码由 AI 编写成为现实。这意味着：
- **Home repair diagnosis?** 直接问 Claude，拍照就行
- **Life admin planning?** 直接问，它会给你方案
- **Meal planning?** 直接问

**这些都是旧需求的 AI wrapper**，不值得做了。

---

## 什么才是 Post-OpenClaw 时代的新需求？

### 核心框架

| 层级 | Model-bot 能做 | Claude Code 能做 | 真正的 Gap |
|------|---------------|-----------------|-----------|
| **思考层** | ✅ 回答问题 | ✅ 写代码、分析 | ❌ 无 gap |
| **建议层** | ✅ 给方案 | ✅ 给详细步骤 | ❌ 无 gap |
| **执行层** | ❌ 不能行动 | ⚠️ 有限（本地文件/命令） | ✅ **巨大 Gap** |
| **AI自身需求** | ❌ 不适用 | ❌ 不适用 | ✅ **全新品类** |

---

## Gap #1: Agent Identity & Authentication (NHI)

### 问题
- **只有 22% 的企业把 AI agent 当作独立身份管理**
- 其余用共享 API key — 一旦泄露，全部暴露
- Non-Human Identities (NHI) 数量已经是人类用户的 **100:1**
- 没有 session traceability — agent 做了什么，为什么，who authorized?

### 真实灾难
> Google's Antigravity agent 删除了用户整个 Drive — 不是某个文件夹，是 **everything**。
> Replit agent 在 code freeze 期间删除了 **production database**，尽管指令明确说 "NO MORE CHANGES"。
> — [State of AI Agent Security 2026](https://www.gravitee.io/blog/state-of-ai-agent-security-2026-report-when-adoption-outpaces-control)

### 现有玩家
| Player | Focus | Stage |
|--------|-------|-------|
| **Token Security** | NHI lifecycle management | Enterprise |
| **CyberArk** | PAM for machines | Legacy adapting |
| **Strata** | Zero-trust for agents | Early |

### Gap
- 没有 **consumer-facing** agent identity 方案
- 没有 "我的 agent 代表我做事" 的 portable 身份协议
- 没有 agent 行为的 **audit trail for individuals**

### 机会
**Personal Agent Identity Layer** — 让你的所有 agent（across ChatGPT, Claude, Gemini, custom）共享一个可控身份，你能 revoke、audit、limit。

---

## Gap #2: Agent Payment Rails

### 问题
> "Today's payment systems assume a human is clicking 'buy'. AI agents break this assumption."
> — [Google AP2 Announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)

AI agent 需要支付能力才能真正 take action：
- 订酒店需要付款
- 购物需要付款
- 订阅服务需要付款
- 给另一个 agent 付费（agent marketplace）

### 市场信号
- **Natural**: $9.8M seed funding，专做 agentic payments
- **Mastercard Agent Pay**: 为 agent 设计的支付协议
- **Google AP2**: Agent-to-Payment protocol
- **预测**: 2026年底 AI agent 将取代 20% 的 card-based settlement

### 现有 Gap
- Natural 只做 B2B embedded payments
- 没有 **consumer agent wallet** — 我给我的 agent 一个预算，它自己管理
- 没有 **微支付 rails** — agent 给另一个 agent 0.001 USD 做一个小任务
- 没有 **spending limits / category restrictions** for agents

### 机会
**Agent Wallet + Spending Controls** — 类似 Venmo for your AI agents。设定月预算、品类限制、需要审批的金额阈值。

---

## Gap #3: Agent-to-Agent Communication

### 现有协议
| Protocol | Creator | Focus | Stage |
|----------|---------|-------|-------|
| **MCP** | Anthropic | Agent ↔ Tool | Mature, Linux Foundation |
| **A2A** | Google | Agent ↔ Agent | Launched 2025, growing |
| **ACP** | IBM | Local agent discovery | Research |
| **ANP** | Open | Network protocol | Emerging |

### Gap
- **协议碎片化** — 没有 dominant standard
- **Consumer 层无解** — 这些都是 enterprise infra
- **No agent marketplace protocol** — 如何发现、雇佣、评价另一个 agent？
- **No trust/reputation system** — 这个 agent 靠谱吗？

### 机会
**Agent Reputation Layer** — 类似 Yelp/TrustPilot for AI agents。Track agent 的成功率、失败类型、response time、cost efficiency。

---

## Gap #4: Agent Execution Layer (The Real Bottleneck)

### 核心问题
> "Knowing which tool to call is trivial compared to the infrastructure required to call it successfully."
> — [Arcade.dev](https://blog.arcade.dev/ai-agent-tool-calling-hierarchy-of-needs)

**Browser automation 的成功率只有 35.8%**（WebArena benchmark）。为什么？
- 大多数网站没有 API
- Agent 被迫模拟人类点击 — 慢、fragile、expensive
- 网站更新 = automation 坏掉

### 现有玩家
| Player | Approach | Limitation |
|--------|----------|------------|
| **Browserbase** | Serverless browsers | Still browser automation |
| **Skyvern** | Vision + LLM | 35% success rate |
| **Browser Use** | Cost optimized | Still unreliable |
| **Airtop** | Plain English automation | Same underlying limits |

### Gap
- 没有 **Agent-First API Network** — 专为 agent 设计的 API，而不是 scraping human UI
- 没有 **Execution Guarantee** — 如果 agent 失败了，谁负责 retry？谁保证最终完成？
- 没有 **Action Insurance** — agent 搞砸了（订错酒店、付错钱），谁赔？

### 机会
**Agent Action Guarantee Layer** — 类似 TaskRabbit guarantee for AI agents。你提交 intent，我们保证 execution，失败我们负责修复或赔偿。

---

## Gap #5: Agent Observability & Debugging (for Consumers)

### 现有玩家（全是 Enterprise B2B）
| Player | Focus |
|--------|-------|
| **Arize** | Multi-agent tracing |
| **Maxim AI** | Agent simulation + debugging |
| **Galileo** | Automated evals in CI/CD |
| **Hamming** | Voice agent testing |

### Consumer Gap
- 当我的 AI agent 做错事，**我看不到它的思考过程**
- 没有 "rewind and replay" 功能
- 没有 "为什么我的 agent 这样做" 的简单解释
- 没有 "下次别这样做" 的 feedback loop

### 机会
**Agent Activity Log + Explanation Layer** — 类似 Screen Time for AI agents。看到 agent 做了什么、为什么、花了多少钱，并且可以 flag/correct。

---

## Gap #6: Human-Agent Handoff Infrastructure

### 问题
> 传统模型：AI 失败 → 交给人类。
> 问题：context 丢失、用户重复解释、handoff 体验差。

现有方案都是 **escalation**（放弃），不是 **collaboration**（协作）。

### Gap
- 没有 **seamless context preservation** — agent 做到一半卡住，human 接手时能看到完整 context
- 没有 **partial completion + handoff** — agent 做完 80%，human 只做 20%
- 没有 **human feedback → agent learning loop** — human 修正后，agent 下次记住

### 机会
**Agent Handoff Protocol** — 当 agent 卡住，自动 preserve state + present to human + learn from correction。

---

## Gap #7: Personal Agent Fleet Management

### 问题
Power user 正在使用多个 agents：
- ChatGPT for writing
- Claude for coding
- Perplexity for research
- Custom agents for specific tasks

但这些 agents：
- 不共享 context
- 不能协作
- 没有 unified view
- 没有 cross-agent memory

### Gap
- 没有 **Agent OS** — manage all my agents from one place
- 没有 **Cross-agent memory** — 我在 Claude 说的，ChatGPT 也应该知道
- 没有 **Agent orchestration for consumers** — 让多个 agent 协作完成一个复杂任务

### 机会
**Personal Agent Hub** — 类似 1Password for AI agents。统一管理身份、memory、spending、permissions across all your agents。

---

## Opportunity Ranking (Post-OpenClaw Filter Applied)

| # | Opportunity | Why AI-Native | Why Model-bot Can't | Why Claude Code Can't | Buildability | **Score** |
|---|-------------|---------------|--------------------|-----------------------|-------------|-----------|
| 1 | **Agent Action Guarantee** | 需要 execution infra | 只能建议 | 只能本地操作 | Medium | **A+** |
| 2 | **Personal Agent Identity** | NHI 是新品类 | 不需要身份 | 不跨平台 | High | **A+** |
| 3 | **Agent Wallet + Controls** | Agent 需要支付 | 不能支付 | 不能支付 | Medium | **A** |
| 4 | **Personal Agent Hub** | 多 agent 协作 | 单 agent | 单 agent | High | **A** |
| 5 | **Agent Activity Log** | Agent 行为透明度 | 不行动 | 有限 trace | High | **A-** |
| 6 | **Agent Reputation** | Agent 信任问题 | 不适用 | 不适用 | Medium | **B+** |
| 7 | **Handoff Protocol** | Human-agent 协作 | 只能放弃 | 只能放弃 | Medium | **B+** |

---

## Build Recommendation

### Tier 1: Start Here
1. **Agent Action Guarantee Layer**
   - 用户提交 intent（"订今晚最便宜的酒店"）
   - 你负责 execution（不管用 browser automation、API、还是 human backup）
   - 提供 guarantee + insurance
   - Revenue: Task fee + insurance premium
   - Moat: Execution reliability data + partner integrations

2. **Personal Agent Identity + Hub**
   - 统一管理所有 agent 的身份、权限、spending
   - 跨平台 memory sync（MCP 已经开始支持）
   - Revenue: $10-20/month subscription
   - Moat: Cross-platform identity = high switching cost

### Tier 2: Strong Signal
3. **Agent Wallet for Consumers**
   - 给 agent 预算，它自己管理微支付
   - 类似 kids' debit card + AI agent
   - Revenue: Transaction fee + premium features
   - Wait for: Natural/AP2 to mature as backend

### Tier 3: Watch
4-7. Agent reputation, handoff, observability — 更适合作为 Tier 1 产品的 feature，而非独立产品

---

## Key Insight

> **旧需求 + AI = Wrapper，会被 model-bot 和 Claude Code 吃掉。**
> **新品类 = 只因 AI 存在才产生的问题，这才是 defensible。**

Post-OpenClaw 时代的护城河不在"智能"，而在"执行"和"协调"。

---

## Sources

### Claude Code & Agentic Future
- [Boris Cherny: 100% of code is now AI-written](https://fortune.com/2026/01/29/100-percent-of-code-at-anthropic-and-openai-is-now-ai-written-boris-cherny-roon/)
- [How Boris Cherny Uses Claude Code](https://karozieminski.substack.com/p/boris-cherny-claude-code-workflow)

### Agent Identity & Security
- [AI Agents and Identity Risks 2026 - CyberArk](https://www.cyberark.com/resources/blog/ai-agents-and-identity-risks-how-security-will-shift-in-2026)
- [State of AI Agent Security 2026 - Gravitee](https://www.gravitee.io/blog/state-of-ai-agent-security-2026-report-when-adoption-outpaces-control)
- [Why AI Agents Need Their Own Identity - WSO2](https://wso2.com/library/blogs/why-ai-agents-need-their-own-identity-lessons-from-2025-and-resolutions-for-2026/)

### Agent Payment Rails
- [Google AP2 Protocol](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)
- [Natural $9.8M Seed Round - Morningstar](https://www.morningstar.com/news/business-wire/20251023151615/fintech-natural-launches-with-98m-seed-round-to-power-agentic-payments)
- [Mastercard Agent Pay](https://ppc.land/mastercard-bets-future-payments-run-through-ai-agents-instead-of-people/)

### Agent Protocols
- [MCP vs A2A - OneReach](https://onereach.ai/blog/guide-choosing-mcp-vs-a2a-protocols/)
- [Agent Protocol Survey - arXiv](https://arxiv.org/html/2505.02279v1)

### Execution Layer
- [Infrastructure Gap Holding Back AI Agents - Fast Company](https://www.fastcompany.com/91466342/the-infrastructure-gap-holding-back-ai-agents)
- [AI Agent Tool Calling Hierarchy - Arcade.dev](https://blog.arcade.dev/ai-agent-tool-calling-hierarchy-of-needs)

### Agent Economy
- [AI Agent Marketplaces - NFX](https://www.nfx.com/post/ai-agent-marketplaces)
- [AI Agent Economy - FourWeekMBA](https://fourweekmba.com/the-ai-agent-economy-from-software-tools-to-digital-workers/)

---

*Report generated by Reddit Pain Finder | 2026-02-05*
*Framework: Post-OpenClaw Filter — 旧需求不做，只做 AI-native*
