#!/bin/bash

# healthcheck.sh
# 检查园区服务健康状态

PORT=8000
HOST="127.0.0.1"
BASE_URL="http://$HOST:$PORT"

echo ">>> 开始健康检查 ($BASE_URL)..."

check_url() {
    local endpoint=$1
    local name=$2
    
    echo -n "    检查 $name ($endpoint) ... "
    status_code=$(curl -o /dev/null -s -w "%{http_code}\n" "$BASE_URL$endpoint")
    
    if [ "$status_code" == "200" ]; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED (Status: $status_code)"
        return 1
    fi
}

# 检查关键端点
FAILED=0

check_url "/health" "基础健康" || FAILED=1
check_url "/park" "园区大屏" || FAILED=1
check_url "/docs-cn" "中文文档" || FAILED=1

check_url "/api/v1/ticker" "公告数据" || FAILED=1

# 检查 Ticker 返回是否正常
echo -n "    检查 Ticker 完整性 ... "
TICKER_RES=$(curl -s "$BASE_URL/api/v1/ticker")
if [[ "$TICKER_RES" == *"items"* ]]; then
    echo "✅ OK"
else
    echo "⚠️  WARNING (Ticker invalid)"
fi

if [ $FAILED -eq 0 ]; then
    echo ">>> 所有检查通过！服务运行正常。"
    exit 0
else
    echo ">>> 检查发现异常，请查看上方错误信息。"
    echo "    建议运行: ./scripts/run_park.sh 查看详细日志"
    exit 1
fi
