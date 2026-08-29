#!/usr/bin/env bash
# deploy_web.sh - 构建前端并发布到 GitHub Pages（web/ 目录）
# 用法：bash scripts/deploy_web.sh [--skip-build]
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)

if [ "${1:-}" != "--skip-build" ]; then
  echo "[deploy] 构建前端..."
  (cd frontend && npm run build)
fi

# dist 静态资产直接拷入 web/（index.html + assets/）
echo "[deploy] 同步 dist -> web/"
rm -rf web/assets
cp -r frontend/dist/. web/

# data.js 与 figs/ 由每日管道写入 web/，构建不会覆盖（dist 里不含）
ls web/ | head -20
echo "[deploy] 完成。可用 git add web/ frontend/ && git commit 提交发布。"
