#!/usr/bin/env bash
#
# update.sh — 重新產生 dashboard 並推送到 GitHub Pages
#
# 用法：
#   ./update.sh                  # commit 訊息預設為 "update: YYYY-MM-DD"
#   ./update.sh "你的訊息"        # 自訂 commit 訊息
#
set -euo pipefail

# 切到此腳本所在資料夾（不論從哪裡執行都正確）
cd "$(dirname "$0")"

MSG="${1:-update: $(date +%Y-%m-%d)}"

echo "🔧 重新產生 dashboard…"
python3 generate_dashboard.py

echo "📦 加入變更…"
git add docs/index.html wiki/

# 沒有任何變更就直接結束，不產生空 commit
if git diff --cached --quiet; then
  echo "✅ 沒有需要更新的內容，結束。"
  exit 0
fi

echo "📝 Commit：$MSG"
git commit -m "$MSG"

echo "🚀 推送到 GitHub…"
git push

echo "🎉 完成！1–2 分鐘後重新整理網站即可看到更新："
echo "   https://daai1230-yeh.github.io/ev-wiki/"
