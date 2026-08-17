# ai-workflow

一套可持续迭代、多轮对话、贴合本人代码风格的研发工作流，覆盖从需求分析到质量保证的全链路。

## 架构

```
ai-workflow/
├── core/                      # 通用层：任何项目可复用
│   ├── skills/
│   │   ├── ai-workflow-dev/        # 功能开发主链路（编排器）
│   │   ├── ai-workflow-design-review/  # 设计文档 + 独立对抗评审
│   │   ├── ai-workflow-estimate/   # 任务拆解与工时预估
│   │   ├── ai-workflow-bugfix/     # 修 bug 链路（公司项目自动对接工具）
│   │   └── ai-workflow-retro/      # 复盘关卡（人工反馈 + 改进提案）
│   └── templates/             # 设计文档等模板
├── company/                   # 公司适配层：仅 amar/ultron 项目加载
│   └── skills/ai-workflow-amar/    # 内部组件知识 + 代码风格 + 工具对接
├── runtime/                   # 运行时产物（执行日志、复盘、任务状态）
│   ├── tasks/                 # 任务目录 + CURRENT 状态文件
│   └── templates/
├── scripts/                   # install.sh / uninstall.sh
└── CHANGELOG.md               # 工作流自身版本记录
```

## 安装与卸载

```bash
./scripts/install.sh     # 在 ~/.cursor/skills/ 创建软链，不污染任何项目
./scripts/uninstall.sh   # 仅删除指向本仓库的软链
```

仓库更新后无需重装（软链始终指向最新内容）。

## 使用

| 场景 | 触发 |
|------|------|
| 功能开发（PRD 驱动） | "ai-workflow 新需求" / "走流程" + 需求描述或 PRD |
| 修 bug / 优化 | "ai-workflow bugfix" + 现象描述 |
| 继续上次任务 | "ai-workflow --continue" |
| 单独设计评审 | "出设计文档" / "设计评审" |
| 单独拆解排期 | "拆解任务" / "预估工时" |
| 复盘 | "复盘"（主链路结尾会强制触发） |

## 设计原则

1. **双层隔离**：core 通用层不引用任何公司资产；company 层仅在公司仓库自动激活，非公司项目自动降级。
2. **关卡式推进**：每阶段产物落盘 + 用户确认才能推进，支持中断恢复（runtime/tasks/CURRENT）。
3. **证据先于断言**：关键判断必须标注【已证实/待验证/推测】；完成声明必须附实际输出证据。
4. **红旗停表**：遇到设计冲突、跨团队改动、新依赖、连续失败、需求遗漏时停止并询问，禁止自行绕路。
5. **可持续迭代**：每次任务强制复盘；人工指出 AI 问题 → 改进提案落到具体文件 → CHANGELOG 记版本。工作流本身用 git 管理。

## 与旧体系的关系

本仓库独立于 `~/.cursor/skills/` 下的既有技能体系（deep-interview/ralplan/ralph 等），只借鉴其机制思想（对抗评审、失败闭环、证据纪律、模糊度评分），不复用其目录约定、触发词与文件形式，互不干扰。
