#!/bin/bash

# run_park.sh
# 一键启动红岩园区数字合规平台
# 自动修复端口占用、环境激活、失败日志分析

PORT=8000
LOG_FILE="park_server.log"

echo "====================================================="
echo "   红岩 · 园区数字合规平台 (RedRock Digital Compliance)"
echo "====================================================="

# 1. 检查端口占用并清理
echo ">>> [1/4] 检查端口 $PORT ..."
PID=$(lsof -t -i:$PORT)
if [ -n "$PID" ]; then
    echo "    发现占用进程 (PID: $PID)，正在清理..."
    kill -9 $PID
    sleep 1
    echo "    端口已释放"
else
    echo "    端口空闲"
fi

# 2. 激活虚拟环境
echo ">>> [2/4] 检查虚拟环境..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "    已激活 .venv"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "    已激活 venv"
else
    echo "!!! 警告：未找到虚拟环境，将使用系统 Python..."
fi

# 3. 准备启动
echo ">>> [3/4] 准备启动服务..."
echo "    日志文件: $LOG_FILE"
echo "-----------------------------------------------------"
echo "   产品首页: http://127.0.0.1:$PORT/"
echo "   园区大屏: http://127.0.0.1:$PORT/park"
echo "   企业检测: http://127.0.0.1:$PORT/demo"
echo "   接口文档: http://127.0.0.1:$PORT/docs-cn"
echo "-----------------------------------------------------"
echo ">>> [4/4] 正在启动 uvicorn (按 Ctrl+C 停止)..."

# 4. 启动并监控
# 使用 tee 同时输出到控制台和文件，以便出错时分析
python -m uvicorn product_api.app:app --reload --host 127.0.0.1 --port $PORT 2>&1 | tee "$LOG_FILE"

# 捕获退出状态
EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "   错误：服务启动失败 (Exit Code: $EXIT_CODE)"
    echo "   最近 50 行日志:"
    echo "-----------------------------------------------------"
    tail -n 50 "$LOG_FILE"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit $EXIT_CODE
else
    echo ""
    echo ">>> 服务已停止"
fi
