# Amar 上线工具集

Cursor Agent 可用的上线/运维自动化工具。

## 安装

```bash
# 1. 把这个目录拷贝到你本地任意位置
# 2. 进入目录运行安装脚本
cd /path/to/tools
./install-tools.sh
```

脚本会在 `~/.cursor/skills/` 下创建软链接，所有项目自动可用。

## 首次使用

```bash
# 安装 Python 依赖
pip3 install requests

# 配置 Aegis 登录凭据
mkdir -p ~/.aegis
echo '{"username": "your_ldap_username", "password": "your_password"}' > ~/.aegis/credentials.json
```

## 工具列表

| 工具 | 触发词 | 说明 |
|------|--------|------|
| [amar-cube-task-creator](amar-cube-task-creator/) | "创建 Cube 任务"、"新建调度任务" | 分析代码自动在 Cube 平台创建定时任务 |

## 卸载

删除 `~/.cursor/skills/` 下对应的软链接即可。
