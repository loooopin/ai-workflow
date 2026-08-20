# ai-workflow 设计思路文档

> 本文档记录 ai-workflow 工作流体系的完整设计思路：输入分析、决策依据、机制说明、迭代规则。
> 维护者（人或 AI Agent）在修改本体系前必须阅读本文档。
> 版本：0.1.0（2026-08-17）

---

## 1. 背景与目标

### 1.1 用户画像（设计约束的来源）

- 资深 Java 后端工程师，HelloGroup amar/ultron 业务线
- 工作构成：**70% PRD 驱动的功能开发**（大多需要与同事协同），**30% 修 bug 与代码优化**
- 已有成熟的个人技能体系（`~/.cursor/skills/` 下 11 个 skill），但要求新体系**完全独立、只借鉴思想不照搬形式**
- 明确要求：**不污染业务项目**（不向项目仓库写入任何工作流文件）

### 1.2 目标

构建一套可持续迭代、多轮对话、贴合用户代码风格的工作流，覆盖：

```
需求分析 → 需求澄清 → 设计文档 → 任务拆解/工时预估 → 编码 → 单测 → 质量自检 → 复盘
```

且区分**公司内部组件**与**公共通用能力**，保证非公司项目也能复用。

---

## 2. 三大输入的分析结论

设计不是凭空产生的。本体系建立在三份分析之上，以下是每份分析的结论及其对设计的影响。

### 2.1 开源技能体系分析（4 套仓库）

分析对象（均位于 `~/workspace/github/` 与 `~/workspace/skills/`）：

| 仓库 | 核心理念 | 对本体系的影响 |
|------|---------|--------------|
| anysearch-mcp-server / anysearch-skill | "文档即 Agent 契约"、运行时自举 | 借鉴了"SKILL 教流程、配置存映射"的分层思想 |
| context-mode | 上下文保卫与会话连续性（事件分级、快照、沙箱路由） | 借鉴**上下文预算化**思想：状态外化到文件对抗上下文压缩，即 runtime/tasks 的设计动机 |
| superpowers | 强制全流程方法论（brainstorm→plan→subagent 执行） | 借鉴了 **plan 格式**、**执行 ledger**、**红旗停表**机制 |
| mattpocock/skills（含 grill-me、grilling、tdd、code-review） | 小而美可组合技能集、user/model-invoked 二分 | 借鉴了**轻骨架**组织方式、grilling 式澄清、CONTEXT.md 共享语言 |

**跨仓库共性模式（8 条，全部被吸收）**：
1. SKILL.md + frontmatter 触发器作为技能物理形态
2. 状态外化到文件对抗上下文压缩
3. 审批门设在阶段边界
4. 红旗停表（反合理化表）
5. 证据先于断言
6. 文件产物驱动交接
7. 只读子 Agent 做评审
8. 失败追踪带量化阈值

### 2.2 amar 仓库分析（6 个仓库）

分析对象：ultron-basic-user、ultron-room、ultron-game、ultron-wrapper、ultron-dependency（含 ultron-common 子模块）、ultron-discover。

**关键结论 → 落点**：

| 结论 | 落点 |
|------|------|
| commit 风格 `feat:/fix:/opt:` + 中文描述，单号在分支名 | `ai-workflow-amar` 第 3 节 Commit 规范 |
| 代码风格：`BusinessCheckException(EcInfo)`、`AlarmUtil`/`HubbleAlarm` 告警、`JsonUtilsV2`、`@Slf4j` 占位符日志、V2 后缀、策略模式偏好 | `ai-workflow-amar` 第 3 节代码风格规范 |
| 组件栈：MOA RPC、`@MomoConfig`、momostore `IStoreDao`、Kafka/goback、Hubble | `ai-workflow-amar` 第 2 节选型表 |
| 结构惯例：api/service/wrapper 三件套，`ultron-dependency` 为公共基础库、`ultron-wrapper` 为封装层 | `ai-workflow-amar` 第 1 节 |
| bugfix : feat ≈ 6 : 4，提交粒度极小、联调期大量小修复 | `ai-workflow-bugfix` 定为高频链路；编码支持小步快跑 |
| 根 pom 默认 skipTests=true，CI 有 checkstyle/spotbugs | `ai-workflow-amar` 第 5 节测试注意 |

### 2.3 本地旧 skills 提炼（9 个文件）

用户明确要求与旧体系隔离，因此只迁移**机制语义**，不迁移形式。

**继承的三大机制**：

1. **三角色对抗评审**（源自 ralplan）：评审者与作者是不同的 Agent，且评审者看不到作者的推理过程 → 落点 `ai-workflow-design-review` 的独立只读子 Agent
2. **三级失败闭环**（源自 ralph）：记录 → 同类 2 次生成提案 → 同问题 3 次升级用户 → 落点 `ai-workflow-retro` 的提案升级规则
3. **三级证据纪律**（源自 auto-troubleshoot）：【已证实/待验证/推测】，禁止"根因可能是…"式表述 → 落点 `ai-workflow-design-review` 第 4 节与 `ai-workflow-bugfix` 阶段 2

**隔离清单（明确不复用的东西）**：
- `.devflow/` 目录体系及全部文件命名（新体系用 `runtime/tasks/`）
- skill 间链式触发词引用
- 硬编码的公司资产映射（Kibana 索引 ID 表、旧 rule 文件名映射）
- RALPLAN-DR 等专有文档模板格式
- FeedbackGate 的 alwaysApply 全局强制（改为只在关卡点使用）

**公司工具生态能力清单**（Kibana/MSE/BeanShell 后门/Hubble/appKey 体系/环境抽象），全部收敛进 `ai-workflow-amar` 第 4 节，并保留安全红线（后门仅线下、线上操作需确认）。

---

## 3. 关键设计决策及理由

### 3.1 载体形式：git 仓库 + 用户级软链

**备选方案对比**：

| 方案 | 问题 |
|------|------|
| 装入每个项目的 `.cursor/` | 用户否决：污染项目 |
| 纯手动 @ 引用 | 无自动触发，体验差 |
| 全局 `~/.cursor/skills/` 复制文件 | 更新要重装，且混入全局目录 |
| **git 仓库 + 软链**（选定） | 单一真源、更新即时、卸载干净、版本可追溯 |

软链只指向 `~/.cursor/skills/ai-workflow-*`，`uninstall.sh` 只删指向本仓库的链接，对其他 skill 零影响。

### 3.2 双层架构：core / company

用户要求"非公司项目也能复用"且"区分内部组件与公共功能"。因此：

- `core/` 不出现任何公司资产（组件名、内部域名、工具平台）
- `company/` 封装全部公司知识，由主链路**探测后自动加载**（探测特征：pom 含 `com.immomo` 或目录名 `ultron-*`）
- 探测失败 → 自动降级为纯通用链路，工具对接段自动跳过

### 3.3 关卡式推进 + 状态外化

借鉴 superpowers 的 ledger 与 context-mode 的状态外化：

- 每阶段产物落盘（`01-requirement.md` … `ledger.md`）才能推进
- `state.md` 记录当前阶段，`runtime/tasks/CURRENT` 记录活跃任务
- **上下文压缩后必须先做状态恢复**（ai-workflow-dev 阶段 0），这是从 FeedbackGate 的压缩恢复经验学来的：长流程必须在设计期考虑压缩场景，而不是事后打补丁

### 3.4 强制复盘 + 人工反馈

迭代机制的核心。设计要点：

- **复盘是强制关卡**，未完成不得宣布任务结束
- "本次 AI 的问题"一栏**必须由用户亲填**，Agent 不得代写——这是用户明确要求的"复盘时需要人工提出本次 AI 的问题"
- 改进提案必须落到**具体文件**，禁止"以后注意"式空话
- 采纳的提案当场修改 + CHANGELOG 记版本，形成"反馈 → 修改 → 版本"闭环
- 同类问题 2 次 → 提案升级（从补充说明升级为改 skill 正文），源自旧体系三级失败闭环

### 3.5 工时预估口径

来自协同开发场景的实际需要（用户选了"任务拆解 + 预估工时"）：

- 三档估计（乐观/最可能/悲观）而非单点值
- 风险系数分档（1.2 / 1.5 / 2.0），跨服务联调和 unfamiliar 模块显式加权
- 显式列出"不含在预估内"的事项，避免排期扯皮

---

## 4. 技能体系架构

```
                        ai-workflow-dev（主链路编排器）
                              │
   ┌──────────┬───────────┼───────────┬──────────┐
   ▼          ▼           ▼           ▼          ▼
 阶段2      阶段3        阶段4       阶段5-6    阶段8
 澄清      ai-workflow-      ai-workflow-     编码+单测   ai-workflow-retro
（内联）   design-review  estimate  （内联）      │
              │                                  │
              └── 公司仓库时自动加载 ──┐          │
                                    ai-workflow-amar ◄┘
                                        ▲
                        ai-workflow-bugfix ──┘（独立链路，共享 amar 与 retro）
```

| Skill | 类型 | 职责 |
|-------|------|------|
| ai-workflow-dev | 编排器 | 功能开发全流程，关卡式推进 |
| ai-workflow-design-review | 阶段 skill | 设计文档 + 独立对抗评审，可独立使用 |
| ai-workflow-estimate | 阶段 skill | 拆解与工时，可独立使用 |
| ai-workflow-bugfix | 编排器 | 修 bug 独立链路（高频，占用户工作 6 成） |
| ai-workflow-retro | 关卡 skill | 复盘，被两条链路强制调用 |
| ai-workflow-amar | 知识层 | 公司组件/风格/工具知识，仅公司仓库加载 |

设计取舍：**bugfix 不复用 dev 链路**。因为两者节奏完全不同——dev 是关卡式长流程，bugfix 是证据驱动的侦查流程，强行统一会让两边都难用（这也是旧体系 prd-reader/ralplan/ralph 线性流水线的教训）。

---

## 5. 核心机制详解

### 5.1 关卡式推进

每阶段：落盘产物 → 用户确认 → 推进。跳过必须用户显式声明并记录。轻量豁免：≤3 文件且无架构影响可跳过设计评审（仍需用户同意）。

### 5.2 红旗停表（ai-workflow-dev 阶段 5）

五种情况立即停止询问，禁止自行绕路：设计冲突、跨团队改动、新依赖、同错误失败 2 次、需求遗漏。源自 superpowers 的反合理化表思想——预先列出 Agent 容易"自作聪明"的场景。

### 5.3 证据纪律

三级标注贯穿设计评审与 bugfix：【已证实】附证据 /【待验证】附验证方法 /【推测】显式标注。完成声明必须附实际命令输出。

### 5.4 对抗评审

只读子 Agent 只看产物不看推理过程，prompt 强制要求"必须找出最薄弱环节、给出最强反对论证"，结论三档（通过/有条件通过/驳回），最多 2 轮重做，超限呈给用户裁决——有上限防无限循环（源自 ralplan 的 5 轮上限设计）。

### 5.5 迭代闭环

```
任务执行 → 强制复盘 → 人工填写 AI 问题 → AI 草拟提案（落具体文件）
    ↑                                            │
    └── CHANGELOG 记版本 ◄── 用户采纳 ◄──────────┘
```

累计 ≥5 份 retro 可触发聚类：按问题类别统计频率，找系统性弱点。

---

## 6. 已知限制与演进方向

| 限制 | 说明 | 可能的演进 |
|------|------|-----------|
| 公司工具未脚本化 | ai-workflow-amar 只描述能力清单，实际查询仍依赖旧 skill/手工 | 若高频使用，可仿 kibana-log-statistics 的"SKILL+scripts 分层"模式沉淀脚本 |
| 工时预估靠系数 | 无历史数据校准 | 积累 ≥10 份 estimate 产物后，用实际耗时回填校准系数 |
| 单测覆盖策略粗 | 仅"核心逻辑必测" | 可结合 CI jacoco 数据细化 |
| 协同通知未打通 | 拆解产物有分工建议，但无自动通知同事 | 需要 IM 集成，暂缓 |
| retro 聚类未实现 | 仅预留机制 | 第 5 份 retro 出现时实现 |

---

## 7. 需求追溯表

| 用户原始需求 | 实现位置 |
|-------------|---------|
| 可持续迭代 | ai-workflow-retro + CHANGELOG + git 版本管理 |
| 多轮对话 | 关卡式推进 + 状态外化（CURRENT/state.md）+ 中断恢复 |
| 符合我的代码风格 | ai-workflow-amar（从真实提交提炼） |
| 需求分析到澄清到设计到编码到质量保证 | ai-workflow-dev 阶段 1-7 |
| 区分内部组件与公共功能、非公司可复用 | core/company 双层 + 自动探测降级 |
| 任务拆解 + 预估工时 | ai-workflow-estimate |
| 单元测试 | ai-workflow-dev 阶段 6 |
| 修 bug 链路 | ai-workflow-bugfix |
| 复盘需人工提出 AI 问题、记录执行日志 | ai-workflow-retro + runtime 模板 |
| 不污染项目 | 软链方案 + install/uninstall 脚本 |
| 与旧体系隔离、只借鉴思想 | 见 2.3 隔离清单、AGENTS.md 红线 |

---

## 附录 A：借鉴溯源对照表

> 记录工作流各机制的来源（2026-08-19 应 [P12] 整理）。迭代时用途：防止重复借鉴、防止误删已借鉴机制、评估某机制时回溯原始出处。
> 用户原始意图见 `docs/ORIGINAL-PROMPTS.md`。

### A.1 本地旧 skills 借鉴

| 旧 skill | 借鉴的部分 | 落点 |
|---------|-----------|------|
| deep-interview | 模糊度量化评分、每轮只问一个问题、就绪关卡、轮次上限 | ai-workflow-dev 阶段 2 |
| ralplan | 独立只读子 Agent 对抗评审、最强反对论证、被掩盖的权衡、三档结论、迭代上限呈报 | ai-workflow-design-review 2-3 步 |
| ralph | ledger 纪律、完成检查附实际证据、失败闭环量化阈值 | dev 阶段 5/7、retro 提案升级规则 |
| harness-retro | 提案落到具体文件、【非流程可解】标注、≥5 份日志触发聚类 | ai-workflow-retro 3 步与聚类节 |
| prd-reader | 结构化提取要素、待澄清项显式传下游 | dev 阶段 1 |
| auto-troubleshoot | 先读代码再查数据、三级证据纪律、成功失败对比、先展示原始数据 | ai-workflow-bugfix 阶段 2-3（借鉴最深） |
| kibana/mse/bean-call | 公司工具能力目录 + 安全红线 | ai-workflow-amar 第 4 节（知识化，未脚本化） |
| FeedbackGate.mdc | 上下文压缩后的状态恢复优先级 | dev/bugfix 阶段 0 |

### A.2 GitHub 四套借鉴

| 仓库 | 借鉴的部分 | 落点 |
|------|-----------|------|
| superpowers | 执行 ledger、红旗停表（反合理化表）、≥2 候选方案+排除理由、阶段边界审批门 | dev 阶段 5、design-review 1 步 |
| mattpocock/skills | grill-me/grilling 轻量澄清、tdd 先写失败测试、CONTEXT.md 共享语言 | 阶段 2、bugfix 阶段 5、AGENTS/DESIGN 定位 |
| context-mode | 状态外化对抗压缩、上下文预算化思想 | runtime/tasks/ + CURRENT + state.md |
| anysearch | SKILL 教流程/配置存映射的分层、文档即契约 | ai-workflow-amar 组织方式（较浅） |

### A.3 完全未借鉴

- lanhu-analyzer（本地）：蓝湖设计稿分析，与后端研发工作流无关
- mattpocock 写作/个人类 skill：writing-beats、obsidian-vault、edit-article、teach、handoff、loop-me 等
- superpowers 的 hooks 机制：Cursor 侧无对应设施
- context-mode 的 CLI/沙箱实现：只借思想

### A.4 部分借鉴、部分弃用（明确取舍）

- ralph 每次执行后独立 Architect 验收 → 成本太高，改为质量自检门，仅设计评审保留独立子 Agent
- deep-interview 三种挑战模式（对立者/简化者/本体论者）→ 太重，澄清只保留评分+关卡
- ralplan Architect + Critic 双角色 → 简化为单一评审 Agent
- harness-retro 健康度量化评分 → 未引入，复盘先靠人工反馈驱动
- FeedbackGate alwaysApply 全局弹窗 → 太打扰，完全未采用

---

*修改本文档时，请同步更新 CHANGELOG。*
