---
name: ai-workflow-dev
description: >-
  AI-Workflow 功能开发主链路：需求录入 → 需求澄清 → 设计评审 → 任务拆解与工时预估 →
  编码实现 → 单元测试 → 复盘。触发词："ai-workflow"、"走流程"、"新需求"、"开发需求"、
  "启动工作流"，或用户提供 PRD/需求描述并要求端到端完成。多轮对话、逐关卡人工确认。
---

# ai-workflow-dev 功能开发主链路

端到端功能开发编排器。

## 核心原则

- **务实优先**：流程服务于交付，不是反过来。过程文档的数量应与任务规模匹配
- **确认点必须有价值**：每个确认点让用户做实质判断，禁止纯走流程的空确认
- **禁止向用户展示内部评分**：模糊度评分等内部机制不对用户输出
- **对外文档极简**：只写变更字段名、类型、取值说明，不暴露服务端实现

## 行为准则（全阶段 checklist）

- **B1 先想再写**：不假设、不藏疑惑。多种理解列出让用户选，搞不清就停下来问
- **B2 极简优先**：刚好解决问题的最少代码。不加未被要求的功能、抽象、灵活性
- **B3 外科手术式变更**：不顺手改相邻代码/注释/格式。diff 每一行都可追溯到用户请求
- **B4 目标驱动执行**：转化为可验证目标，循环到通过。前端项目必须浏览器验证

> ⚠️ **上下文预算纪律**：只 Read 当前阶段的指令文件，禁止一次性 Read 所有 `stages/` 文件。
> 对话 ≥30 轮或已 Read ≥10 个文件时，主动建议用户开新会话 `ai-workflow --continue`。

---

## 任务分流（阶段 0 后立即判断）

| 通道 | 条件 | 走哪些阶段 |
|------|------|-----------|
| 快速 | ≤5 文件，无架构影响，需求明确 | 澄清(可合并到录入) → 编码 → 自检 |
| 标准 | 6-15 文件，或有跨模块影响 | 全部，但设计/拆解可轻量 |
| 重型 | >15 文件，或架构变更 | 全部，设计需独立评审 |

分流结果告知用户，用户可随时升级/降级。

## 任务产物存放

业务产物：`{project}/.docs/PROCESS/{YYYYMMDD}-{slug}/`
（state.md / 01-requirement.md / 02-clarify.md / 03-design.md / 04-tasks.md / ledger.md / retro.md）

引擎状态：`~/workspace/ai-workflow/runtime/tasks/CURRENT`（内容格式：`{project_path}/.docs/PROCESS/{task_dir}`）

---

## 阶段 0：环境与状态恢复

1. **公司环境探测**：检查 pom.xml 含 `com.immomo` 或目录名 `ultron-*`
   - 是 → Read ai-workflow-amar SKILL.md 加载公司知识
   - 否 → 仅使用通用层
2. **状态恢复**：读取 CURRENT
   - 有效 → 读 state.md，向用户确认"上次停在 X 阶段，是否继续？"
   - 上下文被压缩后重新开始时，**必须**先做本步骤，严禁凭摘要记忆续做
3. **任务分流**：根据需求描述判断改动规模，选择通道

## 阶段 1：需求录入

输入：PRD（PDF/Markdown）、用户口述、Issue 链接。
提取：背景、目标、功能点、非功能要求、验收标准、涉及系统。
显式列出文档中**不清晰的点** → 下一阶段澄清。
产物：`01-requirement.md`（快速通道可省略独立文件）。

## 阶段 2：需求澄清

**→ Read 本 SKILL.md 同目录下 `stages/stage-2-clarify.md`**

## 阶段 3：设计评审

- **快速通道**：跳过，直接编码
- **标准通道**：轻量设计，不启动独立评审。产物 `03-design.md`
- **重型通道**：调用 ai-workflow-design-review skill，独立子 Agent 对抗性评审

## 阶段 4：任务拆解与工时预估

- **快速/标准通道**：用 TODO 列表代替独立文件，不做工时预估
- **重型通道**：调用 ai-workflow-estimate skill，产物 `04-tasks.md`

## 阶段 5：编码实现

**→ Read 本 SKILL.md 同目录下 `stages/stage-5-coding.md`**

## 阶段 6-7：测试与质量自检

**→ Read 本 SKILL.md 同目录下 `stages/stage-6-7-testing.md`**

## 阶段 8：复盘关卡

调用 ai-workflow-retro skill。用户说"跳过复盘"时允许跳过。

---

## 快捷模式

- `ai-workflow-dev --light`：强制快速通道
- `ai-workflow-dev --continue`：直接恢复 CURRENT 任务
- 任意阶段可说"跳过本阶段"
