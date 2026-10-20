---
name: ai-workflow-troubleshoot
description: >-
  公司级问题排查能力编排：整合日志查询、配置查询、Redis 探查、ES 数据验证、
  BeanShell 后门调用、跨服务代码搜索六大能力，驱动证据式定位。
  触发词："排查问题"、"查日志"、"查配置"、"查 Redis"、"查 ES 数据"、"troubleshoot"，
  或由 ai-workflow-bugfix 阶段 2 自动加载。仅公司仓库可用。
---

# ai-workflow-troubleshoot 公司级排查能力

公司仓库（pom.xml 含 `com.immomo` 或目录名 `ultron-*`）专用。非公司仓库禁止加载。

## Python 执行环境

所有脚本统一使用专用 venv：`PYBIN="$HOME/.cursor/skills-venv/bin/python"`
若 venv 缺失：`python3 -m venv ~/.cursor/skills-venv && ~/.cursor/skills-venv/bin/pip install requests pyyaml browser_cookie3`

## 核心纪律

1. **代码优先，数据其次** —— 先跨服务搜索代码逻辑，梳理完整检查链路后再查数据
2. **证据先于断言** —— 三级标注（已证实/待验证/推测），禁止"根因可能是…"
3. **先展示原始数据** —— 任何查询结果先完整展示给用户，再做分析
4. **安全红线** —— 后门/Redis/ES 仅线下可执行；线上操作禁止或需二次确认

> ⚠️ **上下文预算纪律**：按需 Read 下方各能力的详细指令或模板，禁止一次性全部 Read。

---

## 排查流程编排

```
第 0 步：环境探测 → 识别 appKey → 确认日志/配置/后门的寻址键
    ↓
第 1 步：跨服务代码搜索（⚠️ 必须先做，严禁跳过直接查数据）
    → 梳理完整检查链路，列出检查点与数据来源
    ↓
第 2 步：按代码逻辑精准查数据
    → 根据检查点逐项验证（日志 → 配置 → Redis → ES → 后门）
    → 每查一项先展示原始数据，再更新假设清单
    ↓
第 3 步：根因收敛
    → 对比所有证据 → 三级标注 → 定位根因（必须有证据）
```

---

## 能力 1：跨服务代码搜索

**用途**：梳理问题相关的完整调用链路、检查逻辑、数据来源。
**使用方式**：Read `/Users/user/.cursor/skills/cross-repo-search/SKILL.md`
**关键动作**：从问题现象提取涉及服务 → 在本地兄弟仓库定位代码 → 梳理调用链 → 标注每个检查点的数据来源

## 能力 2：Kibana 日志查询

**用途**：查询错误日志、成功案例对比、关键词统计、生成分享链接。
**使用方式**：Read `/Users/user/.cursor/skills/kibana-log-statistics/SKILL.md`
**排查关键动作**：查错误日志（≥10 条）+ 必须找成功案例对比 + 按关键词过滤
**纪律**：先展示原始日志内容，再分析。

## 能力 3：MSE 配置查询

**用途**：查询配置中心的配置值，验证配置是否符合预期。
**使用方式**：Read `/Users/user/.cursor/skills/mse-config-query/SKILL.md`
**纪律**：先展示原始配置 JSON，再分析；线上查询需用户确认。

## 能力 4：Redis 数据探查

**用途**：验证 Redis 中的缓存数据、状态标记、分布式锁等。
**环境约束**：🔴 仅限线下。
**使用方式**：需要时 Read 本 SKILL.md 同目录下 `templates/redis-queries.md`

## 能力 5：ES 业务数据查询

**用途**：验证 ES 索引中的业务数据，排查数据不一致问题。
**环境约束**：🔴 仅限线下。
**使用方式**：需要时 Read 本 SKILL.md 同目录下 `templates/es-queries.md`

## 能力 6：通用后门调用

**用途**：查询任何运行时数据（Bean 状态、线程池、缓存统计等）。
**使用方式**：Read `/Users/user/.cursor/skills/generate-spring-bean-call/SKILL.md`
**环境约束**：线下只读 ✅ | 线下写操作 ⚠️ 需确认 | 线上 ❌ 禁止

---

## 排查常见场景

按需参考：Read 本 SKILL.md 同目录下 `templates/scenarios.md`

## 证据标注规范

- **【已证实】**：有直接证据（日志/数据/配置），可称"根因"
- **【待验证】**：有间接证据，附验证方法，只能说"推断原因"
- **【推测】**：无证据，最后才用
- 🚫 禁止："根因是…可能…"（矛盾）、不看代码就查数据、查到数据不展示原始内容

## 安全约束总览

| 操作 | 线下 | 线上 |
|------|------|------|
| 代码搜索 / 日志查询 | ✅ | ✅ 只读 |
| 配置查询 | ✅ | ⚠️ 需确认 |
| Redis/ES 只读 / 后门只读 | ✅ | ❌ 禁止 |
| 后门写操作 | ⚠️ 需确认 | ❌ 禁止 |
