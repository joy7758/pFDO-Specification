#!/bin/bash

# smoke.sh
# 发布/演示“3分钟冒烟”脚本

# 1. Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "错误: 未找到虚拟环境 (.venv 或 venv)，请先创建。"
    exit 1
fi

# 2. Kill port 8000
PID=$(lsof -t -i:8000)
if [ -n "$PID" ]; then
    echo "正在停止旧服务 (PID: $PID)..."
    kill -9 $PID
    sleep 1
fi

# 3. Start service
echo "正在启动服务 (后台运行)..."
# 使用 nohup 确保后台运行，日志输出到 park_server.log
nohup python -m uvicorn product_api.app:app --host 127.0.0.1 --port 8000 > park_server.log 2>&1 &
SERVER_PID=$!
echo "服务启动命令已发送 (PID: $SERVER_PID)"

# 4. Wait for readiness
echo "等待服务就绪 (最多15秒)..."
READY=0
for i in {1..15}; do
    code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)
    if [ "$code" == "200" ]; then
        echo "服务已就绪！(HTTP 200)"
        READY=1
        break
    else
        echo -n "."
        sleep 1
    fi
done
echo ""

if [ $READY -eq 0 ]; then
    echo "错误: 服务启动超时或失败，请检查 park_server.log"
    # 尝试读取日志最后几行
    tail -n 10 park_server.log
    exit 1
fi

# 5. Verify endpoints
FAILED=0
check_endpoint() {
    url=$1
    echo -n "检查 $url ... "
    code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8000$url")
    if [ "$code" == "200" ]; then
        echo "✅ OK"
    else
        echo "❌ 失败 (Code: $code)"
        FAILED=1
    fi
}

echo "开始冒烟测试..."
check_endpoint "/health"
check_endpoint "/park"
check_endpoint "/docs-cn"
check_endpoint "/api/v1/ticker"
check_endpoint "/api/v1/risk/model"
check_endpoint "/api/v1/risk/explain"

echo ""
if [ $FAILED -eq 0 ]; then
    echo "🎉 冒烟通过，可交付演示"
    echo "服务仍在运行，PID=$SERVER_PID"
    echo "停止命令: kill $SERVER_PID"
else
    echo "❌ 冒烟测试失败，请检查上方错误项。"
    # 如果失败，尝试停止服务
    kill $SERVER_PID
    exit 1
fi
