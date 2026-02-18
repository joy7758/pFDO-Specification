#!/usr/bin/env bash

cd "$(dirname "$0")/.."

echo "当前目录：$(pwd)"

if lsof -ti :8000 >/dev/null 2>&1; then
  echo "释放 8000 端口..."
  lsof -ti :8000 | xargs kill -9
else
  echo "8000 端口空闲"
fi

source .venv/bin/activate

echo "启动服务：http://127.0.0.1:8000/demo"
uvicorn product_api.app:app --reload --host 127.0.0.1 --port 8000
