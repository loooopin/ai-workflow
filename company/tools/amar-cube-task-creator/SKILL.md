---
name: amar-cube-task-creator
description: >-
  在 Cube 调度平台上自动创建定时任务。分析当前项目代码提取 appKey、MOA URI、方法名，
  收集用户输入（任务名、cron、环境），调用 Cube API 完成创建。
  当用户提到"创建 Cube 任务"、"配置定时调度"、"Cube 上建任务"、"新建调度任务"时使用。
---

# Cube 定时任务自动创建

## 前置条件

1. Python 3 + `requests` 库（`pip3 install requests`）
2. 凭据文件 `~/.aegis/credentials.json` 已填写：
   ```json
   {"username": "your_ldap_username", "password": "your_password"}
   ```

## 工作流

### Step 1：登录（自动检查）

检查 `~/.aegis/cookies.json` 是否存在。不存在或需要刷新时运行：
```bash
python3 {SKILL_DIR}/scripts/aegis-login.py
```

流程：访问 Cube → 重定向到 Aegis SSO → POST LDAP 凭据 → 获取 session cookie + momoId/momoName → 保存到 `~/.aegis/cookies.json`。

### Step 2：提取代码信息（Agent 自动完成）

1. **appKey**：读取 `{project}/*-service/src/main/resources/app.yaml` 的 `appKey` 字段
2. **MOA URI**：
   - 找到目标 Facade 类的 `@MoaProvider(uri = ...)` 注解
   - 若 uri 引用 Spring 占位符如 `${moa.serviceUri.internal.xxx}`，根据目标环境解析：
     - test → `application-test.yml`
     - prod → `application-prod.yml`
3. **方法名**：从 Schedule 接口中提取目标 `void` 方法名
4. **方法参数**：提取方法签名中的参数列表，序列化为 JSON 数组字符串

### Step 3：收集用户输入

向用户询问以下信息（使用 AskQuestion）：

| 信息 | 说明 | 示例 |
|------|------|------|
| 环境 | test 或 prod | test |
| 任务名称 `name` | Cube 上显示的任务名 | 游戏券补偿日报 |
| 任务别名 `nickName` | Cube 上显示的别名 | gameCouponDailyReport |
| 任务描述 `description` | 任务用途说明 | 每日统计游戏券补偿数据 |
| 调度规则（文字） | 用户用自然语言描述 | 每天凌晨2点执行 |

Agent 根据文字描述生成 **6 位 cron 表达式**（秒 分 时 日 月 周），确认后使用。

### Step 4：调用创建脚本

```bash
python3 {SKILL_DIR}/scripts/cube-create-task.py \
  --env test \
  --app-key "从app.yaml取到的值" \
  --name "任务名称" \
  --nick-name "任务别名" \
  --description "任务描述" \
  --cron "0 0 2 * * ?" \
  --url "/service/ultron/game/game-schedule-stage" \
  --method "generateGameCouponCompensateDailyReport"
```

可选参数（有默认值，通常无需指定）：
```
--param '[]'           # 方法入参，默认空数组
--timeout 3000         # 超时毫秒，默认3000
```

### Step 5：确认结果

脚本输出成功/失败信息。成功时输出任务名和环境。

## 默认值说明

创建任务时向用户展示以下默认配置，告知但无需逐一确认：

| 配置项 | 默认值 | 含义 |
|--------|--------|------|
| dispatchType | 1 | 并行调度 |
| misfirePolicy | 2 | 错过补一次 |
| misfireThreshold | 60000ms | misfire 阈值 |
| timeout | 3000ms | 任务超时 |
| taskSyncType | sync | 同步任务 |
| retryTime | 0 | 不重试 |
| notifyPhase | 2,3 | 失败和超时时通知 |
| notifyLevel | 1 | 仅通知 |

## 参考资料

- 完整字段规格与环境映射：[references/api-spec.md](references/api-spec.md)
