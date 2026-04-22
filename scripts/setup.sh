#!/usr/bin/env bash
set -euo pipefail

REPO="bolecodex/novel-writer-skills"
REPO_URL="https://github.com/${REPO}.git"

echo "============================================"
echo "  novel-writer-skills 一键安装"
echo "============================================"
echo ""

# --- 1. Install novel-cli (Python pip package) ---
echo "[1/2] 安装 novel-cli 命令行工具..."

if command -v pip3 &>/dev/null; then
  PIP=pip3
elif command -v pip &>/dev/null; then
  PIP=pip
else
  echo "❌ 未找到 pip，请先安装 Python 3.9+。"
  exit 1
fi

$PIP install "novel-cli @ git+${REPO_URL}#subdirectory=novel-cli" --quiet

if command -v novel-cli &>/dev/null; then
  echo "✅ novel-cli $(novel-cli --version 2>&1 | head -1) 安装成功"
else
  echo "⚠️  novel-cli 已安装但不在 PATH 中，请检查 pip 的 bin 路径"
fi

# --- 2. Install skill via npx skills add ---
echo ""
echo "[2/2] 安装 web-novel-writer 技能..."

if command -v npx &>/dev/null; then
  npx skills add "${REPO}" -y -g
  echo "✅ 技能安装完成"
else
  echo "⚠️  未找到 npx，跳过技能安装。"
  echo "   请手动安装 Node.js 后运行: npx skills add ${REPO} -y -g"
fi

echo ""
echo "============================================"
echo "  安装完成！"
echo ""
echo "  CLI 用法:   novel-cli --help"
echo "  技能位置:   ~/.agents/skills/ (或对应 Agent 目录)"
echo "============================================"
