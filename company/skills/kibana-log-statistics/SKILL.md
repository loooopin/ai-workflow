---
name: kibana-log-statistics
description: Kibana日志分析工具套件。支持四大功能：1) 生成 Kibana 页面链接（用于分享）；2) 查询具体错误日志内容和堆栈信息；3) 统计日志条数和关键词分布；4) 自动扫描代码提取日志关键词。适用于日志分析、问题排查、错误监控、团队协作等场景。
---

# Kibana 日志分析工具套件

提供四大核心功能：

## 🎯 核心功能

### 1. 🔗 生成 Kibana 页面链接（NEW! 推荐）
**生成可分享的 Kibana 日志查看链接**

使用场景：
- 分享日志链接给团队成员
- 快速定位问题现场
- 团队协作排查问题
- 预设过滤条件（时间、级别、关键词）

### 2. 📋 查询日志内容
**查询具体的错误日志内容、异常堆栈、方便问题排查**

使用场景：
- 查看最近的错误日志详细内容
- 获取完整的异常堆栈信息
- 根据关键词过滤日志
- 命令行快速查看日志

### 3. 📊 日志关键词统计
**统计服务的日志关键词条数**

支持模式：
- **自动模式**：扫描 Java 项目代码，提取所有日志关键词并统计
- **手动模式**：统计用户指定的关键词列表

### 4. 📈 日志级别统计
**统计各个日志级别的总条数，了解整体分布**

## 快速使用

### 功能 1：生成 Kibana 日志链接（NEW! 推荐用于分享）

生成可分享的 Kibana 页面链接：

```
"帮我生成线上环境的日志查看链接"
"生成最近 24 小时 ERROR 日志的 Kibana 链接"
"生成包含 'timeout' 关键词的日志链接"
"给我一个查看最近 6 小时 WARN 日志的链接"
```

### 功能 2：查询错误日志内容（推荐用于问题排查）

查询具体的错误日志内容和异常堆栈：

```
"帮我查看线下环境最近10条错误日志"
"查询最近20条ERROR日志的详细内容"
"查看包含 'timeout' 关键词的错误日志"
"分析一下最近的错误日志"
```

### 功能 2：自动扫描关键词（推荐用于统计分析）

扫描Java项目代码，自动提取所有日志关键词并统计：

```
"帮我统计当前项目所有日志关键词的条数"
"扫描项目代码，统计所有ERROR日志的关键词"
"生成当前服务的日志关键词分布报告"
```

### 功能 3：手动指定关键词统计

统计指定的关键词：

```
"帮我统计 'NewcomerTask' 这个关键词的日志条数"
"统计这几个关键词：'timeout'、'exception'、'failed'"
"查询 'user login' 和 'user logout' 的日志数量"
```

### 功能 4：日志级别统计（基础模式）

统计各个日志级别的总条数：

```
"统计 ultron-user 最近 24 小时各级别日志"
"给我一份线上环境的日志级别分布"
```

---

## 📋 功能 1：查询错误日志详细内容

### 使用场景

- **问题排查**: 查看最近出现的错误，获取完整堆栈信息
- **错误分析**: 分析错误原因，定位代码位置
- **监控告警**: 定期查看是否有新的错误
- **趋势分析**: 查看错误频率和类型变化

### 快速开始

```bash
# 🔗 生成 Kibana 页面链接（推荐用于分享）
cd /path/to/project
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --link --env online

# 生成包含特定关键词的日志链接
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --link --env online --keyword "timeout"

# 生成最近 6 小时的 WARN 日志链接
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --link --env online --level WARN --hours 6

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📋 查询日志内容（推荐用于命令行查看）
# 查询最近10条ERROR日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py

# 查询最近20条错误日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --size 20

# 查询包含特定关键词的错误
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --keyword "timeout"

# 查询WARN级别日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --level WARN --size 15

# 查询线上环境错误日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --env online --size 10
```

### 参数说明

**log_query.py** 参数：

- `--appkey`: AppKey（可选，自动检测）
- `--env`: 环境（offline/online，默认: offline）
- `--hours`: 时间范围（小时，默认: 24）
- `--level`: 日志级别（ERROR/WARN/INFO/DEBUG，默认: ERROR）
- `--size`: 查询条数（默认: 10，仅用于 API 查询）
- `--keyword`: 日志消息关键词（可选）
- `--link`: 🆕 生成 Kibana 页面链接（而不是查询日志）

### 输出示例

```
🔍 查询结果
   服务: momo.bpm.biz.overseas-matchmaker.ultron-user
   环境: 线下环境
   级别: ERROR
   时间范围: 最近 24 小时
   找到: 10 条日志
================================================================================

📋 日志 #1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ 时间: 2026-01-29T10:30:15.123Z
🔖 级别: ERROR
🧵 线程: http-nio-8080-exec-123
📦 Logger: c.i.m.u.domain.task.service.UserTaskDomainService
⚠️  异常: java.lang.NullPointerException

💬 日志消息:
[UserTask] handlerTask exception, uid=106233755, taskId=1001

📚 异常堆栈:
java.lang.NullPointerException: Cannot invoke method on null object
    at com.immomo.moaservice.ultron.user.domain.task.service.UserTaskDomainService.handleTask(UserTaskDomainService.java:856)
    at com.immomo.moaservice.ultron.user.domain.task.service.UserTaskDomainService.processTask(UserTaskDomainService.java:423)
    at com.immomo.moaservice.ultron.user.application.service.TaskApplicationService.execute(TaskApplicationService.java:89)
    ...

================================================================================

📋 日志 #2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
```

### AI 使用指南

当用户请求查询错误日志时，执行以下步骤：

1. **识别用户意图**：
   - 关键词：查看/查询/分析 + 错误/ERROR/异常 + 日志
   - 示例："查看最近的错误日志"、"分析一下ERROR日志"

2. **确定参数**：
   - 条数：从用户请求中提取（默认10）
   - 级别：ERROR/WARN等（默认ERROR）
   - 环境：线下/线上（默认线下）
   - 时间：最近N小时（默认24）
   - 关键词：如果用户提到特定关键词

3. **执行查询**：
   ```bash
   cd /path/to/project
   python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py \
     --size 10 \
     --level ERROR \
     --hours 24
   ```

4. **分析结果**：
   - 查看日志消息，理解错误类型
   - 查看异常堆栈，定位代码位置
   - 查看 Logger 名称，确定出错模块
   - 查看时间，了解错误发生频率

5. **提供建议**：
   - 根据异常类型给出可能的原因
   - 指出需要检查的代码位置
   - 建议可能的修复方案

---

## 功能特性

### 🎯 智能文件生成

**所有统计完成后，都会先输出到控制台，然后询问用户是否保存为文件**

#### 默认行为（询问模式）
- 统计完成后，先在控制台显示完整结果
- 然后提示：`📄 是否保存为报告文件 log_statistics.md? (y/n)`
- 用户输入 `y` 或 `yes` 才会保存文件
- 输入 `n` 或其他，则跳过保存

#### 自动保存模式（--auto-save）
- 使用 `--auto-save` 参数时，统计完成后自动保存文件
- 不询问用户，直接生成报告
- 适合脚本自动化场景

#### 关键词统计的特殊规则
- **≤ 3 个关键词**：只输出到控制台，不生成文件（也不询问）
  - 适合快速查询单个或少量关键词
  - 避免产生不必要的临时文件
  - 结果直接可见，即查即看

- **> 3 个关键词**：询问用户是否生成报告文件
  - 统计完成后会提示：`是否保存为报告文件? (y/n)`
  - 用户确认后才会生成文件
  - 如需自动保存，可使用 `--auto-save` 参数

### 示例

```bash
# 日志级别统计 - 默认询问是否保存
python3 log_stats.py --env online --hours 24
# 输出统计结果后提示：📄 是否保存为报告文件 log_statistics.md? (y/n): 

# 日志级别统计 - 自动保存模式（不询问）
python3 log_stats.py --env online --hours 24 --auto-save
# 输出：✅ 报告已保存: log_statistics.md

# 单个关键词 - 只输出到控制台
python3 log_keyword_stats.py --keywords "timeout"
# 输出：💡 关键词数量较少（1 个），直接输出到控制台

# 多个关键词 - 询问是否保存
python3 log_keyword_stats.py --keywords "error" "warn" "timeout" "exception"
# 输出：📄 统计完成！共 4 个关键词
#      是否保存为报告文件 log_keyword_statistics.md? (y/n): 

# 关键词统计 - 自动保存模式（不询问）
python3 log_keyword_stats.py --keywords "error" "warn" "timeout" "exception" --auto-save
# 输出：✅ 报告已生成: log_keyword_statistics.md
```

## 统计参数

### 必选参数
- **appKey**: 服务的完整 appKey（如：momo.bpm.biz.overseas-matchmaker.ultron-user）

### 可选参数
- **环境**: 线下（alpha-kibana，默认）或线上（aws-kibana）
- **时间范围**: 默认 24 小时，可指定具体小时数或天数
- **日志级别**: 默认统计所有级别（ERROR, WARN, INFO, DEBUG）

## 自动识别

### AppKey 自动检测

脚本会自动尝试从项目的 `app.yaml` 文件中读取 appKey，查找路径包括：
- `./app.yaml`
- `./src/main/resources/app.yaml`
- `./config/app.yaml`
- `./conf/app.yaml`
- 以及向上 3 层父目录的相同路径

如果检测成功，会显示：
```
🔍 自动检测到 appKey: momo.bpm.biz.overseas-matchmaker.ultron-user
   (从 /path/to/app.yaml 读取)
```

### 在项目目录中使用

如果用户在项目目录中请求统计，可以不提供 appKey：

```
用户："帮我统计一下当前服务最近 24 小时的日志"
```

Agent 执行（不需要 --appkey 参数）：
```bash
cd /path/to/project
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_stats.py \
  --env offline \
  --hours 24
```

## 执行步骤

### 模式选择

根据用户请求判断使用哪个脚本：

1. **关键词统计**：使用 `log_keyword_stats.py`
   - 用户提到"关键词"、"代码"、"扫描"
   - 用户指定具体关键词（如 "NewcomerTask"）
   
2. **级别统计**：使用 `log_stats.py`
   - 用户只提到"日志级别"、"ERROR/WARN/INFO"
   - 用户想看整体分布

### 方式 1：自动扫描关键词

当用户请求统计项目中的所有关键词时：

```bash
# 进入项目目录
cd /path/to/project

# 自动扫描并统计
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --env offline \
  --hours 24 \
  --output keyword_report
```

脚本会：
1. 自动检测 appKey（从 app.yaml）
2. 扫描所有 .java 文件
3. 提取 `log.error()`, `log.warn()`, `log.info()`, `log.debug()` 中的字符串
4. 清理并去重关键词
5. 对每个关键词查询 Kibana
6. 按条数降序生成报告

### 方式 2：手动指定关键词

当用户指定具体关键词时：

```bash
# 单个关键词
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --keywords "NewcomerTask" \
  --env offline

# 多个关键词
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --keywords "timeout" "exception" "failed" \
  --env online \
  --hours 48

# 指定日志级别
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --keywords "user login" "user logout" \
  --levels ERROR WARN \
  --env offline
```

### 方式 3：日志级别统计

当用户只想看各级别的总体统计时：

```bash
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_stats.py \
  --env offline \
  --hours 24
```

### 参数说明

**log_keyword_stats.py**（关键词统计）：
- `--appkey`: AppKey（可选，自动检测）
- `--env`: 环境（offline/online）
- `--hours`: 时间范围（小时）
- `--keywords`: 手动指定的关键词列表
- `--levels`: 日志级别过滤（ERROR/WARN/INFO/DEBUG）
- `--project`: Java项目路径（默认当前目录）
- `--output`: 输出文件名前缀
- `--max-keywords`: 每个级别最多查询的关键词数量（默认 50）⚡
- `--max-files`: 最多扫描的文件数量（默认 500）⚡
- `--auto-save`: 自动保存报告文件，不询问用户（默认会询问）

**log_stats.py**（级别统计）：
- `--appkey`: AppKey（可选，自动检测）
- `--env`: 环境（offline/online）
- `--hours`: 时间范围（小时）
- `--output`: 输出文件名前缀
- `--auto-save`: 自动保存报告文件，不询问用户（默认会询问）

### 展示结果

报告包含：
- 🔥 热门关键词 Top 10
- 📈 按日志级别分类的关键词统计
- 📋 统计汇总（总数、有日志数、无日志数）
- 排序：按日志条数从高到低

## 输出示例

### 关键词统计报告

```markdown
# 📊 Kibana 日志关键词统计报告

**生成时间**: 2026-01-26 17:30:15
**服务**: `momo.bpm.biz.overseas-matchmaker.ultron-user`
**环境**: 线下（测试环境）
**时间范围**: 最近 24 小时
**统计关键词数**: 47 个

## 🔥 热门关键词 Top 10

| 排名 | 关键词 | 日志级别 | 日志条数 | 格式化 |
|------|--------|---------|---------|--------|
| 1 | NewcomerTask Issue full attendance | INFO | 1,234 | 1.2K |
| 2 | user login success | INFO | 856 | 856 |
| 3 | request timeout | ERROR | 523 | 523 |
| 4 | database connection failed | ERROR | 234 | 234 |
| 5 | cache miss | WARN | 189 | 189 |
| 6 | API call success | DEBUG | 145 | 145 |
| 7 | user logout | INFO | 98 | 98 |
| 8 | invalid parameter | ERROR | 67 | 67 |
| 9 | retry attempt | WARN | 45 | 45 |
| 10 | process completed | INFO | 23 | 23 |

## 📈 按日志级别统计

### ERROR 级别 (15 个关键词，共 1,234 条日志)

| 排名 | 关键词 | 日志条数 | 格式化 |
|------|--------|---------|--------|
| 1 | request timeout | 523 | 523 |
| 2 | database connection failed | 234 | 234 |
| 3 | invalid parameter | 67 | 67 |
| ... | ... | ... | ... |

### WARN 级别 (12 个关键词，共 856 条日志)
...

### INFO 级别 (18 个关键词，共 2,345 条日志)
...

## 📋 统计汇总

- **总关键词数**: 47 个
- **有日志的关键词**: 42 个
- **无日志的关键词**: 5 个
- **查询失败**: 0 个
```

### 日志级别统计报告

```markdown
# 📊 Kibana 日志统计报告

**服务**: `momo.bpm.biz.overseas-matchmaker.ultron-user`
**时间范围**: 最近 24 小时

## 📈 统计结果

| 日志级别 | 日志条数 | 格式化 | 占比 |
|---------|---------|--------|------|
| ALL | 1,234,567 | 1.2M | 100.0% |
| INFO | 856,234 | 856.2K | 69.4% |
| WARN | 234,567 | 234.6K | 19.0% |
| ERROR | 123,456 | 123.5K | 10.0% |
| DEBUG | 20,310 | 20.3K | 1.6% |

## 🔍 查询详情

- **查询成功率**: 95.2% (1880/1979 分片)
- **失败分片**: 99 个
- **查询耗时**: 18.5 秒
```

## 高级用法

### 自定义时间范围

```bash
# 统计最近 7 天（168 小时）
--hours 168

# 统计最近 12 小时
--hours 12
```

### 指定输出路径

```bash
# 输出到特定目录
--output ~/Documents/reports/ultron_user_stats
```

### 仅统计特定级别

如果用户只关心某个级别，可以在脚本中添加 `--levels` 参数：

```bash
--levels ERROR,WARN
```

## 常见场景

### 场景 1：日常健康检查

```
用户："帮我看看 ultron-user 最近有多少错误日志"
```

执行：统计最近 24 小时的 ERROR 日志，如果数量异常则提醒。

### 场景 2：问题排查

```
用户："统计一下线上 ultron-user 最近 6 小时各级别日志"
```

执行：设置 --hours 6，--env online，生成完整统计报告。

### 场景 3：趋势分析

```
用户："对比一下 ultron-user 最近 7 天和昨天的日志量"
```

执行：分别统计 168 小时和 24 小时，对比变化趋势。

## 故障排除

### 问题：API 超时

如果统计时间范围过大，可能超时。建议：
- 缩短时间范围（如改为 12 小时）
- 分批统计（先统计 ALL，再统计各级别）

### 问题：找不到日志

检查：
- appKey 是否正确
- 环境是否选对（线上/线下）
- 时间范围内是否真的有日志

### 问题：查询成功率低

部分分片失败是正常的（通常是不相关的索引），只要成功率 > 80% 即可。

## 最佳实践

1. **先统计 ALL 级别** - 快速了解总体情况
2. **关注 ERROR 占比** - 超过 5% 需要关注
3. **保存历史报告** - 便于对比趋势
4. **定期清理报告** - 避免累积过多文件

## 脚本位置

- **日志内容查询**: `~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py`
- **关键词统计**: `~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_keyword_stats.py`
- **级别统计**: `~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_stats.py`

---

## 功能对比表

| 功能 | 脚本 | 用途 | 输出 |
|------|------|------|------|
| **查询日志内容** | log_query.py | 问题排查、错误分析 | 具体的日志消息、异常堆栈 |
| 关键词统计 | log_keyword_stats.py | 日志分布分析 | 关键词出现次数统计 |
| 级别统计 | log_stats.py | 整体健康度监控 | 各级别日志总数 |

## 使用建议

### 场景 1：线上出现错误，需要快速排查

```bash
# 第一步：查看最近的错误日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py \
  --env online \
  --size 20 \
  --level ERROR

# 第二步：根据堆栈信息定位代码
# 查看具体的异常类型和出错位置

# 第三步：如果需要查看更多上下文
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py \
  --env online \
  --keyword "具体的错误关键词" \
  --size 50
```

### 场景 2：定期巡检，检查系统健康度

```bash
# 第一步：查看整体日志级别分布
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_stats.py \
  --env offline \
  --hours 24

# 第二步：如果ERROR占比异常，查看具体错误
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py \
  --env offline \
  --size 10 \
  --level ERROR

# 第三步：分析错误类型分布
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --env offline \
  --levels ERROR \
  --max-keywords 20
```

### 场景 3：分析特定功能的日志

```bash
# 查询包含特定关键词的错误日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py \
  --keyword "NewcomerTask" \
  --size 30 \
  --level ERROR
```

---

## 📌 服务日志索引说明

### 🎯 Kibana 索引模式的两种用途

**索引模式 ID 有两种使用场景**：

1. **生成 Kibana 页面链接** ✅（本工具支持）
   - 用于生成可分享的日志查看链接
   - 让团队成员可以直接在 Kibana 页面上查看日志

2. **API 直接查询日志** ✅（本工具默认方式）
   - 通过 API 获取日志内容并展示
   - 不需要索引 ID，通过 appKey 过滤

### 📋 服务专用索引模式配置

各服务在 Kibana 中的索引模式 ID：

#### 核心服务（独立索引）

| 服务名称 | 服务 appKey | 线上索引 ID | 线下索引 ID |
|---------|------------|------------|------------|
| **ultron-user** | `momo.bpm.biz.overseas-matchmaker.ultron-user` | `c107cb00-6f8d-11ef-aa03-d3bc0b7f0e23` | `0310dce0-d400-11ef-af13-7bb4d61b8a53` |
| **ultron-composite** | `momo.bpm.biz.overseas-matchmaker.ultron-composite` | `5ded4280-6f7d-11ef-afb0-fd6a31e42ab8` | `0310dce0-d400-11ef-af13-7bb4d61b8a53` |
| **ultron-discover** | `momo.bpm.biz.overseas-matchmaker.ultron-discover` | `1945ec30-6f7e-11ef-afb0-fd6a31e42ab8` | `0310dce0-d400-11ef-af13-7bb4d61b8a53` |

#### 其他服务（通用索引）

| 环境 | 索引 ID | 说明 |
|-----|--------|------|
| **线上** | `850705e0-7243-11ef-aa03-d3bc0b7f0e23` | 除 user/composite/discover 外的其他服务 |
| **线下** | `0310dce0-d400-11ef-af13-7bb4d61b8a53` | 所有服务统一使用 |

**说明**：
- ✅ **线上环境**：
  - `ultron-user`、`ultron-composite`、`ultron-discover` 三个核心服务各有独立索引（日志量大）
  - 其他服务共享通用索引
- ✅ **线下环境**：所有服务共享统一索引
- 🔧 **自动回退**：如果服务未配置专用索引，自动使用通用索引
- 📝 **配置来源**：从 Kibana 页面 URL 中的 `index:` 参数获取

### 🔗 功能 1：生成 Kibana 页面链接（使用索引 ID）

**使用场景**：需要分享日志查看链接给其他人

```bash
# 生成最近 24 小时的 ERROR 日志链接
python3 scripts/log_query.py --link --env online

# 生成包含特定关键词的日志链接
python3 scripts/log_query.py --link --env online --keyword "timeout" --level WARN

# 生成最近 6 小时的日志链接
python3 scripts/log_query.py --link --env online --hours 6
```

**生成的链接示例**：

**线上环境 - ultron-user 服务（独立索引）**：
```
https://aws-kibana-mdp-logs.wemomo.com/app/discover#/?
  _g=(filters:!(),time:(from:2026-02-05T10:00:00Z,to:2026-02-05T18:00:00Z))
  &_a=(index:c107cb00-6f8d-11ef-aa03-d3bc0b7f0e23,
       query:(language:kuery,query:'appKey:"momo.bpm.biz.overseas-matchmaker.ultron-user" AND logLevel:ERROR'))
```

**线上环境 - ultron-composite 服务（独立索引）**：
```
https://aws-kibana-mdp-logs.wemomo.com/app/discover#/?
  _g=(filters:!(),time:(from:2026-02-05T10:00:00Z,to:2026-02-05T18:00:00Z))
  &_a=(index:5ded4280-6f7d-11ef-afb0-fd6a31e42ab8,
       query:(language:kuery,query:'appKey:"momo.bpm.biz.overseas-matchmaker.ultron-composite" AND logLevel:ERROR'))
```

**线上环境 - 其他服务（通用索引）**：
```
https://aws-kibana-mdp-logs.wemomo.com/app/discover#/?
  _g=(filters:!(),time:(from:2026-02-05T10:00:00Z,to:2026-02-05T18:00:00Z))
  &_a=(index:850705e0-7243-11ef-aa03-d3bc0b7f0e23,
       query:(language:kuery,query:'appKey:"..." AND logLevel:ERROR'))
```

**线下环境 - 任意服务（统一索引）**：
```
https://alpha-kibana.wemomo.com/alpha-public/app/discover#/?
  _g=(filters:!(),time:(from:2026-02-05T10:00:00Z,to:2026-02-05T18:00:00Z))
  &_a=(index:0310dce0-d400-11ef-af13-7bb4d61b8a53,
       query:(language:kuery,query:'appKey:"..." AND logLevel:ERROR'))
```

**链接包含的过滤条件**：
- ✅ 服务 appKey
- ✅ 时间范围（根据 `--hours` 参数）
- ✅ 日志级别（`--level` 参数）
- ✅ 关键词（`--keyword` 参数，如果有）
- ✅ 排序方式（按时间倒序）

### 🔧 功能 2：API 查询日志（不使用索引 ID）

**使用场景**：在命令行直接查看日志内容

```bash
# 查询最近 10 条 ERROR 日志
python3 scripts/log_query.py --size 10 --env online

# 查询包含特定关键词的日志
python3 scripts/log_query.py --size 20 --keyword "timeout" --env online
```

**查询方式**：
```python
# 通过 Kibana API Proxy 查询 ES
url = 'https://aws-kibana-mdp-logs.wemomo.com/api/console/proxy?path=_search&method=POST'

# 查询所有索引，通过 appKey 过滤
query = {
    "query": {
        "bool": {
            "must": [
                {"match_phrase": {"appKey": "momo.bpm.biz.overseas-matchmaker.ultron-user"}}
            ]
        }
    }
}
```

**关键点**：
- ✅ **不需要指定索引 ID**：API 查询会搜索所有索引
- ✅ **通过 appKey 过滤**：每个服务都有唯一的 appKey
- ✅ **自动区分服务**：即使服务有独立索引，appKey 过滤也能正确查询
- ✅ **线上线下统一**：查询方式完全一样，无需特殊配置

### 📊 两种方式对比

| 特性 | 生成 Kibana 链接 | API 查询日志 |
|-----|----------------|------------|
| **使用索引 ID** | ✅ 需要 | ❌ 不需要 |
| **适用场景** | 分享链接给团队 | 命令行快速查看 |
| **输出内容** | Kibana 页面 URL | 格式化的日志文本 |
| **交互方式** | 在浏览器中查看 | 在终端中查看 |
| **灵活性** | 可在 Kibana 调整过滤 | 固定查询条件 |
| **命令参数** | `--link` | 默认（不加 `--link`）|

---

## 快速参考

### 最常用的命令

```bash
# 查看最近10条错误日志（最常用！）
cd /path/to/project
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py

# 查看最近20条错误日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --size 20

# 查看线上环境错误日志
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_query.py --env online --size 10

# 统计日志关键词分布
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_keyword_stats.py

# 统计日志级别分布
python3 ~/workspace/ai-workflow/company/skills/kibana-log-statistics/scripts/log_stats.py
```

---

## 版本历史

- **v2.0** (2026-01-29): 新增日志内容查询功能 `log_query.py`
- **v1.1** (2026-01-26): 优化关键词统计，支持自动扫描代码
- **v1.0** (2026-01-20): 初始版本，支持日志级别统计
