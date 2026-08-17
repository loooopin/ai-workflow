---
name: aiflow-amar
description: >-
  HelloGroup amar/ultron 公司适配层：内部组件知识库、用户代码风格规范、仓库结构惯例、
  公司工具对接清单。由 aiflow-dev/aiflow-bugfix 在探测到公司仓库时自动加载，
  也可触发词手动加载："加载公司规范"、"amar 规范"。非公司项目禁止加载。
---

# aiflow-amar 公司适配层

仅在公司仓库（pom.xml 含 `com.immomo` groupId，或目录为 `ultron-*`）生效。编码、评审、测试时必须遵守本文件。

## 1. 仓库结构与分层

典型 ultron-* 仓库为 Maven 多模块三件套：

```
{repo}/
├── {repo}-api/        # RPC 契约：interfaces + model(req/resp/dto/enums)，独立发布到 Nexus
├── {repo}-service/    # 业务实现：启动类、打包部署
└── {repo}-wrapper/    # 对下游暴露的 wrapper（或 *-wrapper-starter 自动装配）
```

- 公共基础库：`ultron-dependency`（子模块 ultron-common / ultron-common-export / ultron-common-component / ultron-util），被所有业务仓库依赖
- 公共调用封装层：`ultron-wrapper`（mdp-wrapper / platform-wrapper / ultron-components 20+ 组件）
- 业务仓库之间**只交换 -api 契约包，不依赖对方实现**
- service 模块根包：`com.immomo.moaservice.ultron.{域}`，子包惯例：facade(internal/external) → service(按业务域) → dao/redis → kafka → handler → pangu(配置) → bean/dto/enums/convert/aspect/utils

## 2. 基础组件选型（写代码时按此选型，禁止自选轮子）

| 能力 | 组件 | 用法 |
|------|------|------|
| RPC | MOA | `@MoaProvider` / `@MoaConsumer`；consumer 声明在 `application-prod.yml` 的 `momo.spring.moa.consumer.configs`（serviceUri/interfaceName/timeout） |
| 配置（读） | MSE 配置中心 | `@MomoConfig(key = "xxx", defaultVal = "{}")` 回调方法接收 JSON，本地缓存；禁止运行期配置落文件 |
| 配置（写） | MseClient / MseConfigClient | ultron-common 已有封装，优先复用 |
| Redis | momostore `IStoreDao` | `setex/get/writablePipeline`；key 集中在 Keys 工具类；分布式锁用 `RedisLockUtil`（包装 `RedisSimpleLock`），优先 try-with-resources 的 AutoCloseableLock 写法 |
| MQ | Kafka `MomoKafkaProducer` / `@KafkaMessageListener`；延迟回调用 goback-client | |
| JSON | `com.immomo.mcf.util.JsonUtilsV2`（toJSONV2/toMapV2） | 禁止引入 fastjson |
| HTTP | OkHttp（内部既有惯例） | |
| 告警 | `AlarmUtil.sendAlarmAsync`（钉钉）/ `HubbleAlarm.sendAlarm(msg, format, 1)` | 关键失败路径必须发告警 |
| 多语言 | `multilingual-autoload` | |

## 3. 代码风格规范（从真实提交提炼，必须遵守）

### 异常处理

- 业务异常统一抛 `BusinessCheckException(EcInfo.XXX)`，错误码集中在 EcInfo 枚举
- 精准捕获 `catch (BusinessCheckException e)` 单独处理；兜底 `catch (Exception/Throwable e)` 打 error 日志 + 告警
- 禁止吞异常

### 日志

- Lombok `@Slf4j`，占位符风格：`log.info("xxx, userId={}, roomId={}", userId, roomId)`
- 对外调用前后成对打印：`log.info("[mseclient] req:{}", req)` / `resp:{}`
- 排查问题时"加日志"是常规手段，修复后可保留关键日志

### 命名与结构偏好

- lowerCamelCase，业务语义直白（如 `dispatchCouponPreCheckAndBuild`）
- 升级版方法用 `V2` 后缀（如 `lockV2`），不删旧方法（兼容期）
- 重复的分支逻辑倾向重构为策略模式（handler 包）
- 旁路/异步逻辑用既有线程池：`ThreadPoolConfig.XXX_EXECUTOR.execute(() -> {...})`
- 注释极少，仅在必要时写中文 javadoc；工具类加 `@author` 标记

### Commit 规范

- 格式：`类型前缀: 中文描述`，前缀集合：`feat:` / `fix:` / `opt:` / `perf:`
- 单号写在**分支名**不写在 message：`feat/{版本或单号}/{功能名}`、`fix/{日期}`、`dev/{迭代号}`
- 合并走 GitLab MR：功能分支 → test 联调 → master

## 4. 公司工具对接清单（排查/验证时可用）

| 能力 | 工具 | 安全约束 |
|------|------|---------|
| 日志查询/统计 | Kibana（线下 alpha-kibana.wemomo.com / 线上 aws-kibana-mdp-logs.wemomo.com），按 appKey 过滤 | 只读 |
| 配置查询 | MSE 配置中心 mse.wemomo.com REST API | 线上查询需二次确认 |
| 运行时数据探查 | BeanShell 后门（经 MSE 代理） | **红线：仅线下可用；线上禁止；写操作需确认** |
| 监控告警 | Hubble | 兜底异常必须打 ERROR 日志 + 告警 |
| appKey 探测 | 从 pom.xml artifactId / app.yaml 自动探测 | Kibana/MSE/后门统一寻址键 |

环境抽象：`env=offline`（线下，默认）/ `env=online`（线上，操作前必须用户确认）。

## 5. 测试与 CI 注意

- 根 pom 默认 `skipTests=true`，跑测试需显式 `-DskipTests=false`
- CI：GitLab checkstyle + spotbugs + jacoco，提交前自查 checkstyle
- JDK 1.8，语法不要超纲

## 6. 用户工作模式画像（供 Agent 对齐）

- 提交粒度小、频率高，联调期大量小修复 → 工作流应支持"小步快跑"式编码，不要攒大改动
- bugfix 占比约 6 成 → aiflow-bugfix 是高频链路
- 工作时间集中 10:00-21:00，涉及线上操作提醒注意时段与审批
