#!/bin/bash

# 太平 pFDO-Inside 资产重构一键上云脚本 (macOS/Linux)
# 用法: ./scripts/push_to_cloud.sh <YOUR_GITHUB_TOKEN>

if [ -z "$1" ]; then
  echo "❌ 错误: 未提供 GitHub Token。"
  echo "用法: ./scripts/push_to_cloud.sh YOUR_TOKEN"
  echo "示例: ./scripts/push_to_cloud.sh ghp_xxxxxxxxxxxx"
  exit 1
fi

TOKEN=$1
REPO_URL="https://$TOKEN@github.com/joy7758/pFDO-Specification.git"

echo "🔄 [1/3] 正在执行强制身份重写（解决鉴权冲突）..."
git remote set-url origin "$REPO_URL"

echo "🚀 [2/3] 正在执行物理层强制推送（确立自治主权）..."
# 使用 --force 确保覆盖远程历史，确立当前“自治克隆区”的唯一真理状态
git push origin main --force

if [ $? -eq 0 ]; then
  echo "✅ 推送成功！"
  echo "🔍 [3/3] 验证上云状态..."
  git remote -v
  echo "最新提交状态："
  git log -1 --stat
else
  echo "❌ 推送失败，请检查 Token 权限或网络连接。"
  exit 1
fi
