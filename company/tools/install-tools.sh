#!/usr/bin/env bash
# amar-tools 独立安装脚本
# 用法：将 company/tools/ 目录拷贝到任意位置，进入目录运行 ./install-tools.sh
set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURSOR_SKILLS_DIR="$HOME/.cursor/skills"

echo "工具目录: $TOOLS_DIR"
echo "安装目标: $CURSOR_SKILLS_DIR"
echo ""

mkdir -p "$CURSOR_SKILLS_DIR"

installed=0
skipped=0
conflict=0

for tool_dir in "$TOOLS_DIR"/amar-*/; do
  [ -d "$tool_dir" ] || continue
  tool_dir="${tool_dir%/}"
  name="$(basename "$tool_dir")"

  # 跳过非 skill 目录（没有 SKILL.md）
  [ -f "$tool_dir/SKILL.md" ] || continue

  target="$CURSOR_SKILLS_DIR/$name"

  if [ -L "$target" ]; then
    current="$(readlink "$target")"
    current="${current%/}"
    if [ "$current" = "$tool_dir" ]; then
      echo "  已存在（跳过）: $name"
      skipped=$((skipped + 1))
      continue
    fi
    ln -sfn "$tool_dir" "$target"
    echo "  更新软链:       $name"
    installed=$((installed + 1))
  elif [ -e "$target" ]; then
    echo "  !! 冲突（同名目录已存在，未覆盖）: $name"
    conflict=$((conflict + 1))
  else
    ln -s "$tool_dir" "$target"
    echo "  新增软链:       $name"
    installed=$((installed + 1))
  fi
done

echo ""
echo "完成：新增/更新 ${installed}，跳过 ${skipped}，冲突 ${conflict}。"

# 检查 Python 依赖
if ! python3 -c "import requests" 2>/dev/null; then
  echo ""
  echo "⚠️  部分工具需要 Python requests 库，请安装："
  echo "   pip3 install requests"
fi

# 检查凭据
if [ ! -f "$HOME/.aegis/credentials.json" ]; then
  echo ""
  echo "⚠️  首次使用需要配置 Aegis 登录凭据："
  echo "   mkdir -p ~/.aegis"
  echo '   echo '"'"'{"username": "your_ldap_username", "password": "your_password"}'"'"' > ~/.aegis/credentials.json'
fi

if [ "${conflict}" -gt 0 ]; then
  exit 1
fi
