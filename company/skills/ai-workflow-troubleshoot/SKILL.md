---
name: ai-workflow-troubleshoot
description: >-
  公司级问题排查能力编排：整合日志查询、配置查询、Redis 探查、ES 数据验证、
  BeanShell 后门调用、跨服务代码搜索六大能力，驱动证据式定位。
  触发词："排查问题"、"查日志"、"查配置"、"查 Redis"、"查 ES 数据"、"troubleshoot"，
  或由 ai-workflow-bugfix 阶段 2 自动加载。仅公司仓库可用。
---

# ai-workflow-troubleshoot 公司级排查能力

公司仓库（pom.xml 含 `com.immomo` 或目录名 `ultron-*`）专用。
非公司仓库禁止加载，降级为纯代码 + 本地日志链路。

## Python 执行环境

所有依赖脚本（日志/配置/后门）统一使用专用 venv 解释器，**不要用系统 `python3`**（Homebrew Python 为 PEP 668 externally-managed，无法全局装包）：

```bash
# ✅ 正确的解释器（依赖已安装：requests / pyyaml / browser_cookie3）
PYBIN="$HOME/.cursor/skills-venv/bin/python"

# 示例：查询日志
$PYBIN ~/.cursor/skills/kibana-log-statistics/scripts/log_query.py --size 20

# 示例：查询配置
$PYBIN ~/.cursor/skills/mse-config-query/scripts/query_mse_config.py --config-key <key>

# 示例：执行后门代码
$PYBIN ~/.cursor/skills/generate-spring-bean-call/scripts/execute_with_mse.py --code '<代码>'
```

> 本文档其余示例中若出现 `python3`，一律替换为 `$PYBIN`。
> 若 venv 缺失或依赖损坏：`python3 -m venv ~/.cursor/skills-venv && ~/.cursor/skills-venv/bin/pip install requests pyyaml browser_cookie3`

---

## 核心纪律

1. **代码优先，数据其次** —— 先跨服务搜索代码逻辑，梳理完整检查链路后再查数据
2. **证据先于断言** —— 三级标注（已证实/待验证/推测），禁止"根因可能是…"
3. **先展示原始数据** —— 任何查询结果先完整展示给用户，再做分析
4. **安全红线** —— 后门/Redis/ES 仅线下可执行；线上操作禁止或需二次确认

---

## 能力矩阵

| # | 能力 | 实现方式 | 所依赖的 Skill / 脚本 | 环境约束 |
|---|------|---------|----------------------|---------|
| 1 | 跨服务代码搜索 | 本地仓库代码分析 | `cross-repo-search` | 无限制 |
| 2 | Kibana 日志查询 | Kibana API / 链接生成 | `kibana-log-statistics` | 只读 |
| 3 | MSE 配置查询 | MSE REST API | `mse-config-query` | 线上查询需确认 |
| 4 | Redis 数据探查 | BeanShell 后门 + IStoreDao | `generate-spring-bean-call` + 本 skill 模板 | **仅线下** |
| 5 | ES 业务数据查询 | BeanShell 后门 + ES 客户端 | `generate-spring-bean-call` + 本 skill 模板 | **仅线下** |
| 6 | 通用后门调用 | BeanShell 代码执行 | `generate-spring-bean-call` | 线下自动/线上禁止 |

---

## 排查流程编排

```
┌─────────────────────────────────────────────────────┐
│ 第 0 步：环境探测                                      │
│   检测公司仓库 → 加载 ai-workflow-amar 知识             │
│   识别 appKey → 确认日志/配置/后门的寻址键              │
└───────────────┬─────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────┐
│ 第 1 步：跨服务代码搜索（必须先做）                      │
│   cross-repo-search → 梳理完整检查链路                 │
│   输出：涉及的服务、检查点、判断逻辑、数据来源            │
└───────────────┬─────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────┐
│ 第 2 步：按代码逻辑精准查数据                           │
│   根据检查点逐项验证：                                  │
│   ① 日志查询（Kibana）→ 错误日志 + 成功案例对比          │
│   ② 配置查询（MSE）→ 配置值确认                        │
│   ③ Redis 数据探查 → 缓存/状态/锁 验证                  │
│   ④ ES 数据查询 → 索引数据与 DB 一致性验证               │
│   ⑤ 通用后门 → 其他运行时数据                           │
│   每查一项 → 先展示原始数据 → 更新假设清单               │
└───────────────┬─────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────┐
│ 第 3 步：根因收敛                                      │
│   对比所有证据 → 三级标注 → 定位根因                     │
│   根因必须有证据（日志/代码/数据三选一）                  │
└─────────────────────────────────────────────────────┘
```

**严禁跳过第 1 步直接查数据！**

---

## 能力 1：跨服务代码搜索

**用途**：梳理问题相关的完整调用链路、检查逻辑、数据来源。

**使用方式**：读取并遵循 `cross-repo-search` skill：
```
Read: /Users/user/.cursor/skills/cross-repo-search/SKILL.md
```

**关键动作**：
1. 从问题现象提取涉及的服务名
2. 在本地兄弟仓库中定位代码
3. 顺着入口梳理完整调用链，列出所有检查点
4. 标注每个检查点的数据来源（MySQL / Redis / ES / 配置 / 外部服务）

---

## 能力 2：Kibana 日志查询

**用途**：查询错误日志、成功案例对比、关键词统计、生成分享链接。

**使用方式**：读取并遵循 `kibana-log-statistics` skill：
```
Read: /Users/user/.cursor/skills/kibana-log-statistics/SKILL.md
```

**排查场景常用命令**：

```bash
# 查询错误日志（至少 10 条，用于分析）
cd /path/to/project
$PYBIN ~/.cursor/skills/kibana-log-statistics/scripts/log_query.py \
  --size 20 --level ERROR --hours 6

# 【必须】查询成功案例做对比
$PYBIN ~/.cursor/skills/kibana-log-statistics/scripts/log_query.py \
  --size 10 --level INFO --keyword "成功关键词"

# 按关键词过滤
$PYBIN ~/.cursor/skills/kibana-log-statistics/scripts/log_query.py \
  --keyword "具体错误关键词" --size 20

# 生成 Kibana 链接分享给团队
$PYBIN ~/.cursor/skills/kibana-log-statistics/scripts/log_query.py \
  --link --env online --keyword "错误关键词"
```

**纪律**：先展示原始日志内容，再分析；必须找成功案例做对比。

---

## 能力 3：MSE 配置查询

**用途**：查询配置中心的配置值，验证配置是否符合预期。

**使用方式**：读取并遵循 `mse-config-query` skill：
```
Read: /Users/user/.cursor/skills/mse-config-query/SKILL.md
```

**排查场景常用命令**：

```bash
# 查询线下配置
$PYBIN ~/.cursor/skills/mse-config-query/scripts/query_mse_config.py \
  --config-key <configKey>

# 查询线上配置（需确认）
$PYBIN ~/.cursor/skills/mse-config-query/scripts/query_mse_config.py \
  --config-key <configKey> --overseas

# 列出可用命名空间
$PYBIN ~/.cursor/skills/mse-config-query/scripts/query_mse_config.py \
  --list-namespaces
```

**纪律**：先展示原始配置 JSON，再分析；线上查询需用户确认。

---

## 能力 4：Redis 数据探查

**用途**：验证 Redis 中的缓存数据、状态标记、分布式锁等。

**实现方式**：通过 BeanShell 后门调用 `IStoreDao`。

**环境约束**：🔴 **仅限线下环境**。线上禁止执行。

### 常用 Redis 查询模板

#### 4.1 查询单个 Key

```java
// ⚠️ 修改参数：key 改为实际的 Redis Key
// ⚠️ 修改参数：storeDaoBean 改为实际的 IStoreDao Bean 名称

// 查询 String 类型
String value = context.getBean("${STORE_DAO_BEAN}").get("${REDIS_KEY}");
value
```

#### 4.2 查询 Hash 类型

```java
// 查询 Hash 的所有字段
java.util.Map result = context.getBean("${STORE_DAO_BEAN}").hgetAll("${REDIS_KEY}");
result

// 查询 Hash 的单个字段
String value = context.getBean("${STORE_DAO_BEAN}").hget("${REDIS_KEY}", "${FIELD}");
value
```

#### 4.3 批量查询（Pipeline）

```java
// 批量 GET
java.util.ArrayList keys = new java.util.ArrayList();
keys.add("key1");
keys.add("key2");
keys.add("key3");
java.util.List values = context.getBean("${STORE_DAO_BEAN}").mget(keys);
values
```

#### 4.4 检查 Key 是否存在 / TTL

```java
// 检查存在性
Boolean exists = context.getBean("${STORE_DAO_BEAN}").exists("${REDIS_KEY}");
exists

// 查询 TTL（秒）
Long ttl = context.getBean("${STORE_DAO_BEAN}").ttl("${REDIS_KEY}");
ttl
```

#### 4.5 查询 Set / List 类型

```java
// Set 成员
java.util.Set members = context.getBean("${STORE_DAO_BEAN}").smembers("${REDIS_KEY}");
members

// List 范围查询
java.util.List list = context.getBean("${STORE_DAO_BEAN}").lrange("${REDIS_KEY}", 0, -1);
list

// Sorted Set 范围查询（含分数）
java.util.Set zset = context.getBean("${STORE_DAO_BEAN}").zrangeWithScores("${REDIS_KEY}", 0, -1);
zset
```

### Redis Key 定位方法

排查时需要知道具体的 Redis Key。定位步骤：

1. **在代码中搜索 Key 模式**：
   ```bash
   # 在当前服务搜索 Redis Key 定义
   rg "Keys\." --type java -l
   rg "static.*class.*Keys" --type java
   ```

2. **从 DAO 层追溯**：
   ```bash
   # 搜索使用 IStoreDao 的地方
   rg "storeDao\.(get|set|hget|hset)" --type java
   ```

3. **构造完整 Key**：根据代码中的 Key 模板（通常含 uid/roomId 等变量）替换为实际值。

### 执行方式

使用 `generate-spring-bean-call` skill 的执行脚本：

```bash
SCRIPT="/Users/user/.cursor/skills/generate-spring-bean-call/scripts/execute_with_mse.py"

# 线下执行 Redis 查询
python3 $SCRIPT --code 'context.getBean("${STORE_DAO_BEAN}").get("${REDIS_KEY}")'
```

---

## 能力 5：ES 业务数据查询

**用途**：验证 ES 索引中的业务数据（如用户画像、搜索索引），常用于排查数据不一致问题。

**实现方式**：通过 BeanShell 后门调用 ES 客户端或封装好的 ES 查询服务。

**环境约束**：🔴 **仅限线下环境**。线上禁止执行。

### 常用 ES 查询模板

#### 5.1 通过业务服务查询（推荐）

```java
// 优先使用业务层已封装的查询方法，而非直接调 ES 客户端
// ⚠️ 需要根据实际业务替换 Bean 名称和方法

// 示例：通过用户搜索服务查询用户 ES 数据
Object result = context.getBean("${ES_QUERY_BEAN}").${queryMethod}("${PARAM}");
result
```

#### 5.2 通过 RestHighLevelClient 直接查询

```java
// ⚠️ 需要确认项目中 ES 客户端的 Bean 名称
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.builder.SearchSourceBuilder;

SearchRequest request = new SearchRequest("${INDEX_NAME}");
SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
sourceBuilder.query(QueryBuilders.termQuery("${FIELD}", "${VALUE}"));
sourceBuilder.size(10);
request.source(sourceBuilder);

SearchResponse response = context.getBean("${ES_CLIENT_BEAN}").search(request);
response.getHits().getTotalHits().value + " hits, first: " + response.getHits().getHits()[0].getSourceAsString()
```

### ES 索引定位方法

1. **在代码中搜索 ES 索引名**：
   ```bash
   rg "IndexName|indexName|INDEX" --type java -l
   rg "@Document|@Setting" --type java
   ```

2. **从 ES 查询服务追溯**：
   ```bash
   rg "SearchRequest|ElasticsearchTemplate|RestHighLevelClient" --type java -l
   ```

### 执行方式

同 Redis，使用后门执行脚本：

```bash
SCRIPT="/Users/user/.cursor/skills/generate-spring-bean-call/scripts/execute_with_mse.py"

# 线下执行 ES 查询
python3 $SCRIPT --code '生成的 ES 查询代码'
```

---

## 能力 6：通用后门调用

**用途**：查询任何运行时数据（如 Bean 状态、线程池、缓存统计等）。

**使用方式**：读取并遵循 `generate-spring-bean-call` skill：
```
Read: /Users/user/.cursor/skills/generate-spring-bean-call/SKILL.md
```

**环境约束**：
| 操作 | 线下 | 线上 |
|------|------|------|
| 只读查询 | ✅ 自动 | ❌ 禁止 |
| 写操作 | ⚠️ 需确认 | ❌ 禁止 |

---

## 排查常见场景模板

### 场景 A：用户功能异常（如"无法发消息"）

```
1. 跨服务搜索 → 找到消息发送的拦截链路（哪些检查点？）
2. 逐项验证检查点：
   ├── 禁言状态 → Redis 查询 IStoreDao
   ├── 风控状态 → 后门查询风控服务
   ├── 配置开关 → MSE 配置查询
   ├── 余额/资源 → 后门查询业务服务
   └── ES 索引状态 → ES 数据查询
3. 找到不通过的检查点 → 回溯该检查点的数据来源
4. 确认根因（附证据）
```

### 场景 B：数据不一致（如"MySQL 和 ES 数据不同步"）

```
1. 跨服务搜索 → 找到数据同步链路（写 MySQL → 写 ES 的触发机制）
2. 查询 MySQL 数据 → 后门查 DAO 层
3. 查询 ES 数据 → 后门查 ES 索引
4. 对比差异字段
5. 追溯同步链路：Kafka 消息？定时任务？实时双写？
6. 查日志 → Kibana 查同步相关错误日志
7. 确认同步失败原因（附证据）
```

### 场景 C：配置相关问题（如"功能在线上不生效"）

```
1. 跨服务搜索 → 找到功能入口，确认配置读取逻辑
2. MSE 配置查询 → 线下 vs 线上配置对比
3. 代码分析 → @MomoConfig 回调逻辑是否正确
4. Redis 缓存 → 是否有配置缓存未刷新
5. 日志 → 查配置加载/变更日志
6. 确认配置问题根因
```

### 场景 D：性能问题（如"接口超时"）

```
1. 日志查询 → 查超时相关日志，提取耗时信息
2. 跨服务搜索 → 梳理接口完整调用链
3. 逐段排查：
   ├── 本地计算 → 代码分析（循环、锁竞争）
   ├── Redis 调用 → 查 Redis 响应时间（日志）
   ├── DB 调用 → 查慢查询日志
   ├── RPC 调用 → 查下游服务响应时间（日志）
   └── ES 查询 → 查 ES 查询耗时
4. 找到瓶颈环节 → 确认根因
```

---

## 证据标注规范

### 已证实（可称"根因"）

```
✅ 【已证实】描述
   📋 证据：具体的查询结果/日志/代码
   🔗 来源：Kibana 日志 / Redis 查询 / ES 数据 / MSE 配置 / 代码
```

### 待验证（只能说"推断原因"）

```
❓ 【待验证】描述
   🔍 验证方法：具体步骤（用本 skill 的哪个能力验证）
   💬 需要用户提供：额外信息（如有）
```

### 推测（最后才用）

```
💭 【推测】描述
   ⚠️ 注意：这是推测，需要验证
   📖 依据：推测的理由
```

### 🚫 严格禁止

- ❌ "问题根因：XXX"（未查询验证）→ 只能说"推断原因"
- ❌ "问题根因：可能是 XXX"（"根因"与"可能"矛盾）
- ❌ 不看代码就盲目查数据
- ❌ 查询后直接分析，不展示原始数据

---

## 配置说明

### Bean 名称配置

Redis 和 ES 查询依赖正确的 Bean 名称。首次使用时需要确认：

| 配置项 | 说明 | 确认方式 |
|--------|------|---------|
| `${STORE_DAO_BEAN}` | IStoreDao 实现类的 Bean 名称 | 在服务代码中搜索：`@Service.*StoreDao\|@Component.*StoreDao\|implements IStoreDao` |
| `${ES_CLIENT_BEAN}` | ES 客户端的 Bean 名称 | 在服务代码中搜索：`RestHighLevelClient\|ElasticsearchTemplate` |
| `${ES_QUERY_BEAN}` | 业务 ES 查询服务的 Bean 名称 | 在服务代码中搜索业务封装的 ES 查询类 |

**每个仓库的 Bean 名称可能不同**，排查时需先确认当前项目的 Bean 配置。

### 快捷确认脚本

```bash
# 在项目中快速找到 IStoreDao 的 Bean 名称
rg "implements.*IStoreDao|@Autowired.*IStoreDao|@Resource.*IStoreDao" --type java

# 在项目中快速找到 ES 客户端配置
rg "RestHighLevelClient|ElasticsearchClient|@Bean.*elastic" --type java
```

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| `ai-workflow-bugfix` | **被调用方**：bugfix 阶段 2（证据定位）自动加载本 skill 能力 |
| `ai-workflow-amar` | **知识依赖**：本 skill 使用 amar 的组件知识（IStoreDao 用法、Key 管理惯例等） |
| `auto-troubleshoot` | **功能重叠**：本 skill 在 ai-workflow 体系内提供等价能力，ai-workflow 链路内优先用本 skill |
| 各独立 skill | **能力委托**：日志/配置/后门的具体执行委托给各自的 skill 脚本 |

---

## 安全约束总览

| 操作 | 线下 | 线上 |
|------|------|------|
| 代码搜索 | ✅ 无限制 | ✅ 无限制 |
| 日志查询 | ✅ 自动 | ✅ 只读 |
| 配置查询 | ✅ 自动 | ⚠️ 需确认 |
| Redis 只读 | ✅ 自动 | ❌ 禁止 |
| ES 只读 | ✅ 自动 | ❌ 禁止 |
| 后门只读 | ✅ 自动 | ❌ 禁止 |
| 后门写操作 | ⚠️ 需确认 | ❌ 禁止 |

---

**版本**: v1.0.0
**创建日期**: 2026-09-03
**来源**: 用户明确要求新增公司级排查能力
