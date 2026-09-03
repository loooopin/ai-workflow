# Kibana 日志统计 Skill

这是一个 Cursor Agent Skill，提供两种统计模式：

1. **关键词统计**：自动扫描Java项目代码提取日志关键词，或手动指定关键词，统计每个关键词的日志条数
2. **级别统计**：统计各日志级别（ERROR, WARN, INFO, DEBUG）的总条数

## 功能特性

### 关键词统计（log_keyword_stats.py）

- ✅ **自动扫描**：扫描 Java 项目代码，提取所有日志语句中的关键词
- ✅ **手动指定**：支持手动输入关键词列表
- ✅ **智能清理**：自动移除占位符（{}）、多余空格
- ✅ **分级统计**：按日志级别（ERROR/WARN/INFO/DEBUG）分组
- ✅ **排序展示**：按条数从高到低排序，突出热门关键词
- ✅ **Top 10 榜单**：显示最常出现的关键词
- ✅ **详细报告**：生成 Markdown 格式的完整报告

### 级别统计（log_stats.py）

- ✅ 统计所有日志级别（ALL, ERROR, WARN, INFO, DEBUG）
- ✅ 支持线上/线下环境
- ✅ 可自定义时间范围（默认 24 小时）
- ✅ 自动按条数降序排序
- ✅ 生成 Markdown 格式报告
- ✅ 显示查询成功率和耗时
- ✅ 计算各级别日志占比

## 使用方法

### 在 Cursor 中使用（推荐）

直接在 Cursor 中用自然语言请求：

**关键词统计**：
```
"帮我统计当前项目所有日志关键词的条数"
"扫描代码，看看哪些ERROR日志最多"
"统计 'NewcomerTask' 这个关键词的日志数量"
"查询 'timeout' 和 'exception' 的日志条数"
```

**级别统计**：
```
"统计 ultron-user 最近 24 小时各级别日志"
"给我一份线上环境的日志级别分布"
"看看最近 7 天的日志分布情况"
```

Cursor Agent 会自动识别这个 skill 并执行统计。

### 命令行使用

#### 关键词统计

```bash
# 自动扫描项目代码提取关键词
cd /path/to/java/project
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_keyword_stats.py

# 手动指定单个关键词
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --keywords "NewcomerTask"

# 手动指定多个关键词
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --keywords "timeout" "exception" "failed" \
  --env online \
  --hours 48

# 只查询特定日志级别
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --keywords "database error" \
  --levels ERROR WARN

# 指定项目路径
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_keyword_stats.py \
  --project /path/to/another/project \
  --output keyword_report
```

#### 级别统计

```bash
# 在项目目录中使用（自动检测 appKey）
cd /path/to/your/project
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py

# 明确指定 appKey
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user"

# 指定环境和时间范围
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --env online \
  --hours 168

# 自定义输出文件名
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --output ~/Documents/level_stats
```

### 参数说明

#### log_keyword_stats.py（关键词统计）

| 参数 | 必选 | 默认值 | 说明 |
|------|------|--------|------|
| `--appkey` | ❌ | 自动检测 | 服务的完整 appKey |
| `--env` | ❌ | offline | 环境：offline（线下）或 online（线上） |
| `--hours` | ❌ | 24 | 时间范围（小时） |
| `--keywords` | ❌ | 自动扫描 | 手动指定关键词列表（空格分隔） |
| `--levels` | ❌ | 全部 | 日志级别过滤（ERROR/WARN/INFO/DEBUG） |
| `--project` | ❌ | 当前目录 | Java 项目路径 |
| `--output` | ❌ | log_keyword_statistics | 输出文件名前缀 |

#### log_stats.py（级别统计）

| 参数 | 必选 | 默认值 | 说明 |
|------|------|--------|------|
| `--appkey` | ❌ | 自动检测 | 服务的完整 appKey |
| `--env` | ❌ | offline | 环境：offline（线下）或 online（线上） |
| `--hours` | ❌ | 24 | 时间范围（小时） |
| `--output` | ❌ | log_statistics | 输出文件名前缀 |

**自动功能**：
- **AppKey 检测**：自动从 `app.yaml` 提取 appKey
- **关键词提取**：扫描 Java 代码中的 log.error/info/warn/debug 语句
- **智能清理**：移除占位符和无意义词

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

## 📈 按日志级别统计

### ERROR 级别 (15 个关键词，共 1,234 条日志)

| 排名 | 关键词 | 日志条数 | 格式化 |
|------|--------|---------|--------|
| 1 | request timeout | 523 | 523 |
| 2 | database connection failed | 234 | 234 |
| 3 | invalid parameter | 67 | 67 |

## 📋 统计汇总

- **总关键词数**: 47 个
- **有日志的关键词**: 42 个
- **无日志的关键词**: 5 个
- **查询失败**: 0 个
```

### 级别统计报告

```markdown
# 📊 Kibana 日志统计报告

**生成时间**: 2026-01-26 16:45:23  
**服务**: `momo.bpm.biz.overseas-matchmaker.ultron-user`  
**环境**: 线下（测试环境）  
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

## 常见问题

### Q: 统计速度慢怎么办？

A: 统计所有级别需要 5 次 API 查询，总耗时约 15-30 秒。可以：
- 缩短时间范围（如改为 12 小时）
- 只统计关心的级别

### Q: 查询成功率低是什么原因？

A: 部分索引分片失败是正常的（如多语言搜索索引），只要成功率 > 80% 即可。失败的分片不影响统计结果。

### Q: 能否统计多个服务？

A: 当前版本只支持单个服务。如需统计多个服务，可以多次运行脚本。

### Q: 报告文件保存在哪里？

A: 默认保存在当前目录下的 `log_statistics.md`，可以通过 `--output` 参数指定其他路径。

## 技术说明

### API 调用

脚本直接调用 Kibana 的 Elasticsearch API：
- **线下**: `https://alpha-kibana.wemomo.com/alpha-public/api/console/proxy`
- **线上**: `https://aws-kibana-mdp-logs.wemomo.com/api/console/proxy`

无需登录认证，只需要网络可达即可。

### 查询逻辑

对每个日志级别执行独立的 count 查询：
```json
{
  "query": {
    "bool": {
      "must": [
        {"match_phrase": {"appKey": "服务appKey"}},
        {"match": {"logLevel": "级别"}}
      ]
    }
  }
}
```

### 依赖项

只使用 Python 标准库，无需安装第三方依赖：
- `urllib` - HTTP 请求
- `json` - JSON 处理
- `argparse` - 命令行参数解析
- `datetime` - 时间处理

## 更新日志

### v1.0.0 (2026-01-26)
- ✨ 初始版本
- ✅ 支持按日志级别分组统计
- ✅ 支持线上/线下环境
- ✅ 生成 Markdown 格式报告
- ✅ 自动排序和占比计算

## 贡献

如有建议或问题，欢迎反馈！

## 许可

MIT License
