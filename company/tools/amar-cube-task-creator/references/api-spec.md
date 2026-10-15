# Cube createTask API 完整规格

## API 端点

```
POST https://cube.wemomo.com/apirest/httpproxy/web/createTask
Content-Type: application/x-www-form-urlencoded
```

## 请求参数

Form 表单有 5 个参数：`json`（URL-encoded JSON 字符串）、`corp`、`env`、`momoId`、`momoName`。

## 环境映射

| 环境 | `corp` | `env` (query) | `ext.env` (JSON) | YAML 文件 |
|------|--------|---------------|-------------------|-----------|
| 测试 | `alpha` | `stage` | `1` | `application-test.yml` |
| 生产 | `overseas` | `prod` | `0` | `application-prod.yml` |

## JSON 字段规格

### 外层

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `appKey` | string | `app.yaml` 的 `appKey` | 应用标识 |
| `name` | string | 用户输入 | 任务名称 |
| `nickName` | string | 用户输入 | 任务别名 |
| `description` | string | 用户输入 | 任务描述 |
| `cronExpression` | string | Agent 生成 | 6位cron（秒 分 时 日 月 周） |
| `momoId` | string | 登录获取 | 加密用户标识 |
| `momoName` | string | 登录获取 | 加密用户名 |
| `executeType` | int | 固定 `1` | |
| `dispatchType` | int | 固定 `1` | 并行调度 |
| `misfirePolicy` | int | 固定 `2` | 错过补一次 |
| `misfireThreshold` | int | 固定 `60000` | misfire 阈值 ms |
| `delayDispatchPolicy` | int | 固定 `1` | |
| `type` | int | 固定 `1` | |
| `subType` | int | 固定 `0` | |
| `coreType` | int | 固定 `0` | |
| `creator` | string | 固定 `""` | |

### ext 字段（JSON 字符串）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `url` | string | 代码 `@MoaProvider` uri 解析 | MOA 服务 URI |
| `method` | string | 代码接口方法名 | 调用方法 |
| `param` | string | 用户输入，默认 `"[]"` | 方法入参 JSON 数组 |
| `timeout` | string | 默认 `"3000"` | 超时 ms |
| `taskSyncType` | string | 固定 `"sync"` | 同步任务 |
| `env` | int | test=`1`, prod=`0` | 环境标识 |
| `retryTime` | string | 固定 `"0"` | 重试次数 |
| `retryDelay` | string | 固定 `"100"` | 重试间隔 ms |
| `failRetryTime` | string | 固定 `"0"` | 失败重试次数 |
| `failRetryDelay` | string | 固定 `"100"` | 失败重试间隔 ms |
| `notifyPhase` | string | 固定 `"2,3"` | 失败+超时通知 |
| `notifyLevel` | string | 固定 `"1"` | 仅通知 |
| `enablePreferredHost` | bool | 固定 `false` | |
| `preferredHost` | string | 固定 `""` | |
| `preferredHostAddress` | string | 固定 `""` | |
| `contentType` | string | 固定 `""` | |
| `scriptType` | string | 固定 `""` | |
| `scriptCommand` | string | 固定 `""` | |
| `scriptUser` | string | 固定 `""` | |
| `execHosts` | array | 固定 `[]` | |

## MOA URI 解析

`@MoaProvider(uri = ...)` 的值通常是 Spring 占位符，需要从 YAML 解析：

```
@MoaProvider(uri = "${moa.serviceUri.internal.gameschedule}")
                      ↓
application-test.yml → moa.serviceUri.internal.gameschedule = /service/ultron/game/game-schedule-stage
application-prod.yml → moa.serviceUri.internal.gameschedule = /service/ultron/game/game-schedule-prod
```

## 认证

所有请求需要 Aegis SSO session cookie。`momoId` 和 `momoName` 从登录会话获取。
Cookie 文件存放在 `~/.aegis/cookies.json`。
