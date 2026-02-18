#!/bin/bash

# run_park.sh
# 一键启动红岩园区数字合规平台

PORT=8000
echo ">>> 正在检查端口 $PORT ..."

# 查找占用 8000 端口的进程并杀掉
PID=$(lsof -t -i:$PORT)
if [ -n "$PID" ]; then
    echo ">>> 发现端口占用 (PID: $PID)，正在释放..."
    kill -9 $PID
    sleep 1
    echo ">>> 端口已释放"
else
    echo ">>> 端口空闲"
fi

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo ">>> 激活虚拟环境..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo ">>> 激活虚拟环境..."
    source venv/bin/activate
else
    echo ">>> 警告：未找到虚拟环境，尝试直接运行..."
fi

echo ">>> 正在启动 uvicorn 服务..."
echo "-----------------------------------------------------"
echo "   产品首页: http://127.0.0.1:$PORT/"
echo "   园区大屏: http://127.0.0.1:$PORT/park"
echo "   企业检测: http://127.0.0.1:$PORT/demo"
echo "   接口文档: http://127.0.0.1:$PORT/docs-cn"
echo "-----------------------------------------------------"

python -m uvicorn product_api.app:app --reload --host 127.0.0.1 --port $PORT
