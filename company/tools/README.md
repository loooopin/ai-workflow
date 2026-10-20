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

## 目录结构

```
company/tools/
├── common/                    # 公共模块（各工具共享）
│   └── aegis_auth.py          #   Aegis SSO 登录、凭据读取、cookie 持久化
├── amar-cube-task-creator/    # Cube 定时任务创建
├── amar-leave-balance/        # 调休余额计算
├── install-tools.sh           # 安装脚本
└── README.md
```

`common/` 目录不是独立工具，而是各 `amar-*` 工具脚本的共享依赖。
各工具脚本通过 `os.path.realpath(__file__)` 解析软链接后定位到 `common/`，
因此通过软链接安装后也能正常工作。

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
| [amar-leave-balance](amar-leave-balance/) | "调休余额"、"还有多少调休"、"加班调休" | 查询加班/调休记录，计算剩余可调休小时数 |

## 卸载

删除 `~/.cursor/skills/` 下对应的软链接即可。
