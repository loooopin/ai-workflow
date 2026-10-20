# Context Engineering 规范

> 本文档规定 ai-workflow 体系中所有 skill/template 文件的上下文工程规范。
> 新增或修改 skill 时必须遵守。复盘产出的改进提案也必须符合本规范。
> 来源：2026-10-20 上下文占用审计（诊断出 bugfix 全链路指令量达 157KB、Lost-in-the-Middle 效应导致指令遗漏）。

---

## 核心原则

1. **上下文是稀缺资源**：LLM 的注意力预算有限，token 越多单条指令被遵循的概率越低（Lost in the Middle 效应）
2. **按需加载，及时释放**：只在执行某能力/阶段时才 Read 其详细指令，不预加载
3. **关键规则置顶**：最重要的行为约束放在 SKILL.md 开头，利用模型对首部内容的注意力优势

## 文件规范

| 规则 | 标准 | 说明 |
|------|------|------|
| SKILL.md 体积上限 | **≤ 6KB** | 编排器/路由层，不含模板和示例代码 |
| 模板/示例代码 | 提取到 `templates/` 子目录 | 在需要执行时才 Read |
| 阶段指令 | 提取到 `stages/` 子目录 | 进入该阶段时才 Read |
| 跨 skill 重复 | **禁止逐字复制** | 共性规则压缩为 checklist |
| 行为准则（B1-B4） | 压缩为 ≤ 500 字节 checklist | 模型已内化这些原则，提醒即可，不需展开论述 |

## 加载策略

### 阶段式按需加载（Stage-based JIT）

```
编排器 SKILL.md（始终在上下文）
  → 进入阶段 N → Read stages/stage-N.md（只读当前阶段）
  → 阶段 N 完成 → 自然被后续内容推远，无需主动清除
```

**禁止一次性 Read 所有阶段文件。**

### 能力式按需加载（Capability-based JIT）

```
排查编排器（始终在上下文，只含路由表）
  → 需要查 Redis → Read templates/redis-queries.md
  → 需要查日志 → Read kibana-log-statistics SKILL.md
```

**禁止在编排器加载时就连锁 Read 所有能力 SKILL。**

### 长会话主动拆分

当对话达到以下任一条件时，Agent 应**主动建议**用户开新会话 `ai-workflow --continue`：

- 对话轮次 ≥ 30 轮
- 已 Read 超过 10 个文件
- 明显感到早期指令被"忘记"（如重复犯已有规则禁止的错误）

## 复盘合规检查

复盘（ai-workflow-retro）产出改进提案时，**必须逐条检查**：

1. 目标文件修改后是否仍 ≤ 6KB？超出则必须拆分到 stages/ 或 templates/
2. 新增规则是否与已有 skill 文件重复？重复则合并到最具体的已有文件
3. 新增的示例/模板/代码块是否可以放到 templates/ 子目录？可以则外置
4. 优先追加到已有文件，而非新建文件

---

*修改本文档时，请同步更新 CHANGELOG.md。*
