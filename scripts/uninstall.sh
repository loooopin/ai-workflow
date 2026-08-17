#!/usr/bin/env bash
# aiflow 卸载脚本：仅删除指向本仓库的符号链接，不影响任何其他文件。
set -euo pipefail

AIFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CURSOR_SKILLS_DIR="$HOME/.cursor/skills"

removed=0
kept=0

for link in "$CURSOR_SKILLS_DIR"/*; do
  [ -L "$link" ] || continue
  target="$(readlink "$link")"
  case "$target" in
    "$AIFLOW_DIR"/*)
      rm "$link"
      echo "  移除软链: $(basename "$link")"
      removed=$((removed + 1))
      ;;
    *)
      kept=$((kept + 1))
      ;;
  esac
done

echo "完成：移除 ${removed} 个软链，保留 ${kept} 个非 aiflow 链接。"
