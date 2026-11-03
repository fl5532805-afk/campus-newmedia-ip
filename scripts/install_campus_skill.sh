#!/usr/bin/env bash
# 帆总不累 · 校园新媒体获客方法论 Skill 一键安装器
# 用法：bash install_campus_skill.sh
set -euo pipefail

REPO_ZIP="https://github.com/fl5532805-afk/campus-newmedia-ip/archive/refs/heads/main.zip"
SKILL_NAME="campus-newmedia-ip"

# 探测 user_skills 目录；USER_SKILLS_DIR_OVERRIDE 仅供隔离测试
if [ -n "${USER_SKILLS_DIR_OVERRIDE:-}" ]; then
  TARGET_DIR="$USER_SKILLS_DIR_OVERRIDE"
else
  CANDIDATES=(
    "$HOME/.doubao/agent_mode/workspace/.user_skills"
    "$HOME/.super_doubao/super-doubao-runtime/workspace/.user_skills"
  )
  TARGET_DIR=""
  for d in "${CANDIDATES[@]}"; do
    if [ -d "$d" ]; then TARGET_DIR="$d"; break; fi
  done
  if [ -z "$TARGET_DIR" ]; then
    TARGET_DIR="$HOME/.doubao/agent_mode/workspace/.user_skills"
  fi
fi

mkdir -p "$TARGET_DIR"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "1/4 下载 Skill ..."
curl -fsSL "$REPO_ZIP" -o "$TMP/skill.zip"

echo "2/4 解压 ..."
unzip -q "$TMP/skill.zip" -d "$TMP"
SRC="$TMP/${SKILL_NAME}-main"
[ -f "$SRC/SKILL.md" ] || { echo "错误：压缩包缺少 SKILL.md，安装中止"; exit 1; }

echo "3/4 安装到 $TARGET_DIR ..."
if [ -d "$TARGET_DIR/$SKILL_NAME" ]; then
  mv "$TARGET_DIR/$SKILL_NAME" "$TARGET_DIR/${SKILL_NAME}.bak.$(date +%s)"
  echo "    已自动备份旧版本"
fi
mv "$SRC" "$TARGET_DIR/$SKILL_NAME"

echo "4/4 校验完整性 ..."
FILE_COUNT=$(find "$TARGET_DIR/$SKILL_NAME" -type f | wc -l)
head -1 "$TARGET_DIR/$SKILL_NAME/SKILL.md" | grep -q '^---' \
  || { echo "警告：SKILL.md frontmatter 异常，请检查"; exit 1; }

echo ""
echo "安装完成：$TARGET_DIR/$SKILL_NAME（共 $FILE_COUNT 个文件）"
echo "下一步：新开一个会话，技能将自动加载；直接说出你的任务，系统会自动推荐并调用。"
