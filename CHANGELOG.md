# CHANGELOG

工作流体系自身的版本记录。每次根据复盘采纳的改进项更新工作流定义时，必须在此追加一条。

格式：`## [版本号] - YYYY-MM-DD`，条目注明来源复盘（关联 retro 文件）。

## [0.2.1] - 2026-08-27

来源：对照原始借鉴 skills 审查后补缺。

### 补充借鉴
- `ai-workflow-dev` 阶段 6：补 seam（测试边界）原则 + 3 条测试反模式表（源自 mattpocock/tdd）
- `ai-workflow-dev` 阶段 7：补反合理化表 6 条（源自 superpowers/verification-before-completion）；质量自检门各项补命令示例
- `ai-workflow-bugfix` 阶段 5：回归测试补红-绿循环完整步骤 + seam 原则

## [0.2.0] - 2026-08-27

来源：用户审查后的补充裁决与一致性修复。

### 新增
- `docs/PROMPTS-SUPPLEMENT.md`：原始提示词的补充裁决文件（[S1] 产物允许放 .docs/、[S2] 复盘允许跳过、[S3] --light 阈值统一 ≤5）
- `runtime/templates/state-template.md`：任务状态模板（含阶段进度、恢复上下文字段）
- `runtime/tasks/CURRENT`：空文件占位，供工作流引擎写入活跃任务路径

### 修复（一致性）
- `ai-workflow-retro` SKILL：retro 产物路径改为 `{project}/.docs/PROCESS/{task}/retro.md`，与 dev 主链路一致
- `runtime/tasks/README.md`：明确本目录只存 CURRENT 指针，产物在项目 `.docs/PROCESS/` 下
- `AGENTS.md`：红线条款区分"工作流引擎文件"与"任务过程文档"，后者允许写入 `.docs/`；必读清单加入 PROMPTS-SUPPLEMENT
- `DESIGN.md`：复盘关卡改为"Agent 主动发起，用户可跳过"；架构图阶段编号对齐实际实现（0-8）
- `PROMPTS.md`：--light 阈值从 ≤3 改为 ≤5，与 SKILL.md 一致
- `ai-workflow-bugfix` SKILL：补充产物目录结构约定（state/symptom/evidence/rootcause/fix-summary/retro）
- `ai-workflow-dev` SKILL：恢复机制补充读取 state.md 并向用户确认；澄清阶段 5 维度补充具体判断标准；编码阶段补 git 分支策略指导

### 修复（脚本）
- `scripts/install.sh`：修复 for 循环尾斜杠导致 readlink 对比失败的问题

## [0.1.3] - 2026-08-20

- 新增 `docs/ORIGINAL-PROMPTS.md`：所有者全部原始提示词忠实记录（需求溯源），作为意图冲突时的最高裁决依据
- 新增 `docs/DESIGN.md` 附录 A：借鉴溯源对照表（本地旧 skills / GitHub 四套 / 未借鉴 / 取舍项），落实 [P12] 待办
- AGENTS.md 必读清单加入 ORIGINAL-PROMPTS.md

## [0.1.2] - 2026-08-17

- 新增 `docs/PROMPTS.md`：提示词速查表（主链路/快捷模式/单独节点/关卡应答/组合示例/排障），作为触发词的唯一权威来源
- README 与 AGENTS.md 增加对该文档的指引
- 命名统一：全部 `aiflow` 改为 `ai-workflow`（前次提交 55e0a8c 已含）

## [0.1.1] - 2026-08-17

- 新增 `AGENTS.md`：new agent 接手本仓库时的入口指引（必读清单、修改红线、仓库结构速览、常见维护操作）
- 新增 `docs/DESIGN.md`：完整设计思路文档（背景与用户画像、三大输入分析结论、关键设计决策及理由、技能体系架构、核心机制详解、已知限制与演进方向、需求追溯表）
- 目的：后续迭代时 new agent 可直接读取上述文档获得完整上下文，无需重新推导设计依据

## [0.1.0] - 2026-08-17

- 初始版本：建立 core（通用层）+ company（公司适配层）双层结构
- 建立执行日志 / 复盘 / 改进提案的可持续迭代机制
