---
name: amar-leave-balance
description: >-
  查询 Moji 平台的加班和调休记录，计算剩余可调休小时数。
  分析每天加班的总时长与已关联调休时长，输出逐日余额明细。
  当用户提到"调休余额"、"还有多少调休"、"可调休小时"、"加班调休"时使用。
---

# 调休余额计算工具

## 前置条件

1. Python 3 + `requests` 库（`pip3 install requests`）
2. 可选但推荐：`beautifulsoup4`（`pip3 install beautifulsoup4`），增强 HTML 解析
3. 凭据文件 `~/.aegis/credentials.json` 已填写：
   ```json
   {"username": "your_ldap_username", "password": "your_password"}
   ```

## 工作流

### Step 1：登录 Moji

检查 `~/.aegis/moji-cookies.json` 是否存在。不存在或登录态过期时运行：
```bash
python3 {SKILL_DIR}/scripts/moji-login.py
```
流程：访问 Moji → 重定向到 Aegis SSO → POST LDAP 凭据 → 回跳 Moji 建立 session →
保存 cookie 到 `~/.aegis/moji-cookies.json`。

### Step 2：计算调休余额（自动模式）

```bash
python3 {SKILL_DIR}/scripts/leave-balance.py
```

脚本自动完成以下步骤：
1. 获取加班记录列表（`ef_type=4`，自动翻页）
2. 获取调休记录列表（`ef_type=1&type=9`，自动翻页）
3. 逐条获取调休详情页（`/care/ef/{id}`），提取关联的加班日期和扣减小时数
4. 按加班日汇总：总加班时长 − 已调休时长 = 剩余可调小时
5. 输出明细和汇总

可选参数：
```
--debug        保存原始 HTML 到 /tmp/moji-debug/，便于排查解析问题
--discover     仅抓取页面并保存到 /tmp/moji-debug/，不做解析（用于首次了解页面格式）
--json         以 JSON 格式输出结果
--cookie-file  指定 cookie 文件路径（默认 ~/.aegis/moji-cookies.json）
```

### Step 3（备选）：自动解析失败时的处理

脚本可能因为 Moji 页面格式变化而解析失败，此时分两种情况：

**情况 A：SPA 应用（脚本报 exit code 2）**

页面是前端渲染的 SPA，HTTP 请求拿不到数据。改用浏览器工具：
1. 运行 `moji-login.py` 确保登录态
2. 使用浏览器工具（cursor-ide-browser MCP）逐页访问：
   - `https://moji.wemomo.com/care/ef?ef_type=4` → 提取加班记录（日期、时长）
   - `https://moji.wemomo.com/care/ef?ef_type=1&type=9` → 提取调休记录 ID
   - 对每条调休点击详情 → 提取关联加班日期和时长
3. 按照 **计算逻辑** 手动计算余额

**情况 B：HTML 格式不匹配（脚本报 exit code 1）**

1. 运行 `python3 leave-balance.py --discover` 保存原始页面
2. 读取 `/tmp/moji-debug/` 下的 HTML 文件，分析实际数据结构
3. 调整脚本中的解析逻辑（`parse_overtime_from_html`、`parse_leave_detail`）

## 计算逻辑

```
核心公式：剩余可调 = 加班总时长 − 已调休时长（按加班日汇总）
```

- 只计算 **已通过**（approved）状态的记录
- 1 天调休 = 8 小时
- 同一天加班可被多条调休部分引用
  - 例：加班 8h，调休 A 用了 3h，调休 B 用了 2h → 剩余 3h
- 调休关联的加班日不在列表中的，输出警告但不影响已知余额

## 输出示例

```
📊 调休余额计算结果
=======================================================

可调休明细：
  2026-09-20  加班   8.0h  已调休   8.0h  剩余   0.0h
  2026-10-01  加班   8.0h  已调休   3.0h  剩余   5.0h ✅
  2026-10-15  加班   4.0h  已调休   0.0h  剩余   4.0h ✅

───────────────────────────────────────────────────────
  加班总计:    20.0 小时
  已调休:       11.0 小时
  剩余可调:     9.0 小时
```

## 参考

- Moji 加班列表：`https://moji.wemomo.com/care/ef?ef_type=4`
- Moji 调休列表：`https://moji.wemomo.com/care/ef?ef_type=1&type=9`
- Moji 单据详情：`https://moji.wemomo.com/care/ef/{id}`
