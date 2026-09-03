# 使用示例

## 示例 0：自动检测（在项目目录中）

### 场景
用户在项目目录中工作，项目的 `app.yaml` 包含 appKey 配置。

### 用户请求
```
"帮我统计一下当前服务最近 24 小时的日志"
```

### Agent 执行
```bash
# 进入项目目录
cd /Users/user/IdeaProjects/ultron-user

# 执行统计（不需要指定 appKey）
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py
```

### 输出
```
📍 未指定 appKey，尝试自动检测...

🔍 自动检测到 appKey: momo.bpm.biz.overseas-matchmaker.ultron-user
   (从 /Users/user/IdeaProjects/ultron-user/app.yaml 读取)

🔍 正在统计日志...
   服务: momo.bpm.biz.overseas-matchmaker.ultron-user
   环境: 线下
   时间范围: 最近 24 小时

   查询 ALL   级别... ✅ 1,234,567 条
   ...
```

**优点**：
- ✅ 无需手动输入 appKey
- ✅ 适合日常在项目中快速统计
- ✅ 减少输入错误

---

## 示例 1：基本统计（线下环境，24小时）

### 用户请求
```
"帮我统计 ultron-user 服务最近 24 小时的日志"
```

### Agent 执行
```bash
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --env offline \
  --hours 24 \
  --output log_statistics
```

### 输出结果
```
🔍 正在统计日志...
   服务: momo.bpm.biz.overseas-matchmaker.ultron-user
   环境: 线下
   时间范围: 最近 24 小时

   查询 ALL   级别... ✅ 1,234,567 条
   查询 ERROR 级别... ✅ 123,456 条
   查询 WARN  级别... ✅ 234,567 条
   查询 INFO  级别... ✅ 856,234 条
   查询 DEBUG 级别... ✅ 20,310 条

✅ 报告已生成: log_statistics.md
```

生成的报告文件包含完整的统计信息和排序结果。

---

## 示例 2：线上环境长时间统计

### 用户请求
```
"统计一下线上 ultron-user 最近 7 天的日志分布"
```

### Agent 执行
```bash
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --env online \
  --hours 168 \
  --output ultron_user_7days
```

### 分析要点

Agent 会在报告中重点关注：
1. ERROR 日志占比是否异常（通常应 < 5%）
2. 各级别日志是否均衡分布
3. 查询成功率是否正常（应 > 80%）

---

## 示例 3：问题排查场景

### 用户请求
```
"线上 ultron-user 最近 6 小时错误日志特别多，帮我看看各级别分布"
```

### Agent 执行步骤

1. **先统计最近 6 小时**
```bash
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --env online \
  --hours 6 \
  --output recent_6h
```

2. **对比正常时段（24小时）**
```bash
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --env online \
  --hours 24 \
  --output normal_24h
```

3. **分析对比结果**

假设结果显示：
- 6小时内 ERROR 占比 25%（异常高）
- 24小时内 ERROR 占比 8%（正常范围）

Agent 会建议：
- 检查最近 6 小时是否有部署或配置变更
- 使用插件的"查询日志"功能查看具体错误内容
- 关注 WARN 级别是否也同步上升

---

## 示例 4：多服务对比

### 用户请求
```
"帮我对比 ultron-user 和 ultron-discover 的日志量"
```

### Agent 执行

分别统计两个服务：

**Service 1: ultron-user**
```bash
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --output ultron_user_stats
```

**Service 2: ultron-discover**
```bash
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-discover" \
  --output ultron_discover_stats
```

### 对比分析

Agent 会展示：

| 服务 | 总日志数 | ERROR | WARN | INFO | DEBUG |
|------|----------|-------|------|------|-------|
| ultron-user | 1.2M | 123K (10%) | 235K (19%) | 856K (69%) | 20K (2%) |
| ultron-discover | 856K | 45K (5%) | 189K (22%) | 612K (71%) | 10K (1%) |

**结论**：
- ultron-user 的 ERROR 占比较高，需要关注
- ultron-discover 日志量相对健康

---

## 示例 5：定期健康检查

### 用户请求
```
"每天下午 5 点统计一下 ultron-user 今天的日志情况"
```

### Agent 建议

可以创建一个 cron 任务或脚本：

```bash
#!/bin/bash
# daily_log_check.sh

TODAY=$(date +%Y%m%d)
OUTPUT_DIR=~/log_reports/$TODAY

mkdir -p $OUTPUT_DIR

python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --env online \
  --hours 24 \
  --output "$OUTPUT_DIR/ultron_user_daily"

echo "✅ Daily log report saved to $OUTPUT_DIR"
```

然后添加到 crontab：
```
0 17 * * * /path/to/daily_log_check.sh
```

---

## 示例 6：趋势分析

### 用户请求
```
"对比一下 ultron-user 最近 7 天和今天的日志量变化"
```

### Agent 执行

```bash
# 最近 7 天
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --hours 168 \
  --output stats_7days

# 今天（24小时）
python3 ~/.cursor/skills/kibana-log-statistics/scripts/log_stats.py \
  --appkey "momo.bpm.biz.overseas-matchmaker.ultron-user" \
  --hours 24 \
  --output stats_today
```

### 趋势分析

假设结果：
- 7天平均每天：176K 条日志
- 今天：234K 条日志（+33% ⚠️）

Agent 会提醒：
- 今天日志量异常增长 33%
- 建议检查是否有流量激增或问题发生
- 重点关注 ERROR 和 WARN 级别的增长

---

## 技巧与最佳实践

### 1. 快速健康检查
只看 ERROR 占比：
- < 1%：非常健康 ✅
- 1-5%：正常范围 ✅
- 5-10%：需要关注 ⚠️
- \> 10%：异常，需要排查 ❌

### 2. 时间范围选择
- **实时监控**：1-6 小时
- **日常检查**：24 小时
- **趋势分析**：7 天（168 小时）
- **长期统计**：30 天（720 小时，可能较慢）

### 3. 报告存档
建议按日期分类存储：
```
~/log_reports/
  ├── 2026-01-26/
  │   ├── ultron_user_stats.md
  │   └── ultron_discover_stats.md
  ├── 2026-01-25/
  └── ...
```

### 4. 自动化场景
- 部署后自动统计（验证部署影响）
- 定时健康检查（每日/每周）
- 告警触发后统计（问题排查）

---

## 常见错误处理

### 错误：网络超时
```
❌ 错误: 网络错误: timed out
```

**解决方案**：
- 检查网络连接
- 尝试缩短时间范围
- 重试几次（有时是临时网络问题）

### 错误：AppKey 不存在
```
❌ 错误: 查询失败: no such index
```

**解决方案**：
- 检查 appKey 是否拼写正确
- 确认环境选择（线上/线下）
- 验证该服务是否在该环境有日志

### 错误：查询成功率过低
```
⚠️  查询成功率: 45.2% (895/1979 分片)
```

**说明**：
- 成功率 > 80% 是正常的
- 成功率 < 50% 可能是网络不稳定
- 不影响统计准确性（失败的通常是不相关索引）

---

## 进阶用法

### 集成到工作流

在 Cursor 中可以组合使用：

```
1. "统计 ultron-user 最近 6 小时日志"
   → 发现 ERROR 占比 15%（异常）

2. "帮我查询 ultron-user ERROR 日志，关键词：timeout"
   → 使用 QueryLogsAction 查看详细错误

3. "打开 ultron-user 的配置中心"
   → 使用 ConfigCenterAction 检查配置

4. "查看 ultron-user 的服务 IP"
   → 使用 GetServiceIPAction 查看实例状态
```

完整的工作流整合，提升排查效率！
