# AGENTS.md - 给接手本仓库的 AI Agent

你正在维护一套**研发工作流体系**（不是业务代码）。它的所有者是一位资深 Java 后端工程师（HelloGroup/amar 业务线，git 身份 `hu.xiaodong_205145`），70% 工作是 PRD 驱动的功能开发（多人协同），30% 是修 bug 与代码优化。

## 做任何修改前，必读

1. `docs/DESIGN.md` —— 完整设计思路：体系来源、每个设计决策的依据、机制说明
2. `CHANGELOG.md` —— 历史演进记录，了解为什么是现在这个样子
3. 最近的复盘：`runtime/tasks/*/retro.md`（如有）—— 用户的真实反馈是改进的第一依据

## 修改纪律（红线）

- **改进必须来自复盘或用户明确要求**，不允许自发重构工作流
- 每条改动在 `CHANGELOG.md` 追加记录，注明来源（哪份 retro 或哪次用户要求）
- 只改增量，不重构无关内容；skill 正文修改后需用户确认
- **不得污染业务项目**：本体系通过 `~/.cursor/skills/` 软链接入，禁止向任何业务仓库写入工作流文件
- **不得与旧体系混合**：`~/.cursor/skills/` 下的 deep-interview/ralplan/ralph/harness-retro 等是旧体系，只可参考思想，禁止引用其目录约定（`.devflow/`）、触发词或文件命名
- core 层不得引用任何公司资产；公司专属内容只能放 company 层

## 仓库结构速览

```
core/skills/          通用层技能（任何项目可用）
company/skills/       公司适配层（仅 amar/ultron 仓库激活）
core/templates/       文档模板
runtime/tasks/        运行时任务目录（执行日志、复盘），CURRENT 记录活跃任务
runtime/templates/    日志/复盘模板
scripts/              install.sh / uninstall.sh（软链管理）
docs/DESIGN.md        设计思路（本文件的详细版）
```

## 常见维护操作

| 场景 | 做法 |
|------|------|
| 复盘采纳了改进提案 | 改对应 skill/模板 → 追加 CHANGELOG → git commit |
| 新增节点/skill | 先更新 docs/DESIGN.md 的架构节，再建目录，命名前缀 `ai-workflow-` |
| 公司组件栈变化 | 只改 `company/skills/ai-workflow-amar/SKILL.md` |
| 累计 ≥5 份 retro | 可触发聚类分析，产出结构性改进建议（需用户批准） |
