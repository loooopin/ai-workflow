#!/usr/bin/env bash
# ai-workflow 安装脚本：在用户级目录创建符号链接，不向任何项目写入文件。
set -euo pipefail

AI_WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CURSOR_SKILLS_DIR="$HOME/.cursor/skills"

echo "ai-workflow 仓库路径: $AI_WORKFLOW_DIR"
echo "目标目录:       $CURSOR_SKILLS_DIR"

mkdir -p "$CURSOR_SKILLS_DIR"

installed=0
skipped=0
conflict=0

for skill_dir in "$AI_WORKFLOW_DIR"/core/skills/*/ "$AI_WORKFLOW_DIR"/company/skills/*/; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  target="$CURSOR_SKILLS_DIR/$name"

  if [ -L "$target" ]; then
    current="$(readlink "$target")"
    if [ "$current" = "$skill_dir" ]; then
      echo "  已存在（跳过）: $name"
      skipped=$((skipped + 1))
      continue
    fi
    ln -sfn "$skill_dir" "$target"
    echo "  更新软链:       $name -> $skill_dir"
    installed=$((installed + 1))
  elif [ -e "$target" ]; then
    echo "  !! 冲突（非软链同名目录已存在，未覆盖）: $name"
    conflict=$((conflict + 1))
  else
    ln -s "$skill_dir" "$target"
    echo "  新增软链:       $name -> $skill_dir"
    installed=$((installed + 1))
  fi
done

echo ""
echo "完成：新增/更新 ${installed}，跳过 ${skipped}，冲突 ${conflict}。"
if [ "${conflict}" -gt 0 ]; then
  echo "存在冲突项，请人工确认后手动处理。"
  exit 1
fi
