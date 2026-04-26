#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://gitee.com/bolecodex/novel-writer-skills.git"
SKILL_SPEC="${REPO_URL}@web-novel-writer"
PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"

echo "============================================"
echo "  novel-writer-skills 国内一键安装（Gitee）"
echo "============================================"
echo ""

echo "[1/2] 安装 novel-cli 命令行工具..."

if command -v python3 &>/dev/null; then
  PIP="python3 -m pip"
elif command -v pip3 &>/dev/null; then
  PIP=pip3
elif command -v pip &>/dev/null; then
  PIP=pip
else
  echo "未找到 pip，请先安装 Python 3.9+。"
  exit 1
fi

$PIP install "novel-cli @ git+${REPO_URL}#subdirectory=novel-cli" -i "${PIP_INDEX_URL}" --quiet

if command -v novel-cli &>/dev/null; then
  echo "novel-cli $(novel-cli --version 2>&1 | head -1) 安装成功"
else
  echo "novel-cli 已安装但不在 PATH 中，请检查 pip 的 bin 路径"
fi

echo ""
echo "[2/2] 安装 web-novel-writer 技能..."

if command -v npx &>/dev/null; then
  if ! npx skills add "${SKILL_SPEC}" -y -g; then
    echo "精确 skill 安装失败，尝试安装整个仓库..."
    npx skills add "${REPO_URL}" -y -g
  fi
  echo "技能安装完成"
else
  echo "未找到 npx，跳过技能安装。"
  echo "请手动安装 Node.js 后运行: npx skills add ${SKILL_SPEC} -y -g"
fi

echo ""
echo "============================================"
echo "  安装完成"
echo ""
echo "  CLI 用法: novel-cli --help"
echo "============================================"
