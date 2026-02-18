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
    local temp_file=$(mktemp)
    
    echo -n "    检查 $name ($endpoint) ... "
    # Capture body to temp file, write http code to stdout
    status_code=$(curl -s -w "%{http_code}" -o "$temp_file" "$BASE_URL$endpoint")
    
    if [ "$status_code" == "200" ]; then
        echo "✅ 通过"
        rm "$temp_file"
        return 0
    else
        echo "❌ 失败 (状态码: $status_code)"
        echo "    响应内容 (前200字符):"
        head -c 200 "$temp_file"
        echo "" # newline
        rm "$temp_file"
        return 1
    fi
}

# 检查关键端点
FAILED=0

check_url "/health" "基础健康" || FAILED=1
check_url "/park" "园区大屏" || FAILED=1
check_url "/docs-cn" "中文文档" || FAILED=1

check_url "/api/v1/ticker" "公告总线" || FAILED=1
check_url "/api/v1/briefing" "运营简报" || FAILED=1
check_url "/api/v1/overview" "概览数据" || FAILED=1
check_url "/api/v1/trends" "趋势数据" || FAILED=1
check_url "/api/v1/alerts" "告警数据" || FAILED=1
check_url "/api/v1/integrations" "集成状态" || FAILED=1
check_url "/api/v1/actions" "操作列表" || FAILED=1
check_url "/api/v1/risk-map" "风险地图" || FAILED=1
check_url "/api/v1/weather" "天气数据" || FAILED=1
check_url "/api/v1/air" "空气质量" || FAILED=1
check_url "/api/v1/calendar" "日历黄历" || FAILED=1

# 行为驱动引擎检查
check_url "/api/v1/must-focus" "必须关注" || FAILED=1
check_url "/api/v1/behavior-stats" "行为统计" || FAILED=1
check_url "/api/v1/time-pressure" "时间压力" || FAILED=1

# 风险模型检查
check_url "/api/v1/risk-model" "风险模型定义" || FAILED=1

# 叙事引擎检查 (New)
check_url "/api/v1/narrative/status" "叙事引擎状态" || FAILED=1
check_url "/api/v1/narrative/series" "叙事趋势序列" || FAILED=1
check_url "/api/v1/narrative/summary" "叙事摘要" || FAILED=1

# 检查操作列表返回
echo -n "    检查操作列表结构 ... "
ACT_RES=$(curl -s "$BASE_URL/api/v1/actions")
if [[ "$ACT_RES" == *"actions"* ]]; then
    echo "✅ 通过"
else
    echo "⚠️  失败（操作列表缺失）"
    FAILED=1
fi

# 检查公告总线返回是否包含 items
echo -n "    检查公告总线结构 (items) ... "
TICKER_RES=$(curl -s "$BASE_URL/api/v1/ticker")
VALID_TICKER=$(echo "$TICKER_RES" | python3 -c "import sys, json; data=json.load(sys.stdin); print('OK' if 'items' in data and isinstance(data['items'], list) else 'FAIL')")

if [ "$VALID_TICKER" == "OK" ]; then
    echo "✅ 通过"
else
    echo "❌ 失败（公告总线结构不合法）"
    echo "    返回内容: $TICKER_RES"
    FAILED=1
fi

# 检查概览结构：risk_score / compliance_score 必须存在且在 0-100
echo -n "    校验概览字段 (risk_score/compliance_score 范围) ... "
OVERVIEW_RES=$(curl -s "$BASE_URL/api/v1/overview")
VALID_OVERVIEW=$(echo "$OVERVIEW_RES" | python3 -c "import sys, json; d=json.load(sys.stdin); r=d.get('risk_score'); c=d.get('compliance_score'); ok=isinstance(r,(int,float)) and isinstance(c,(int,float)) and 0<=r<=100 and 0<=c<=100; print('OK' if ok else 'FAIL')")
if [ "$VALID_OVERVIEW" == "OK" ]; then
    echo "✅ 通过"
else
    echo "❌ 失败（概览字段缺失或越界）"
    echo "    返回内容: $OVERVIEW_RES"
    FAILED=1
fi

# 检查 Narrative Status 协议字段
echo -n "    校验叙事状态协议 (schema_version/generated_at) ... "
NAR_STATUS_RES=$(curl -s "$BASE_URL/api/v1/narrative/status")
VALID_NAR_STATUS=$(echo "$NAR_STATUS_RES" | python3 -c "import sys, json; d=json.load(sys.stdin); ok=(d.get('schema_version')=='NSE-1.0' and isinstance(d.get('generated_at'), str)); print('OK' if ok else 'FAIL')")
if [ "$VALID_NAR_STATUS" == "OK" ]; then
    echo "✅ 通过"
else
    echo "❌ 失败（叙事状态协议字段不合法）"
    echo "    返回内容: $NAR_STATUS_RES"
    FAILED=1
fi

# 检查 Narrative Summary 结构与协议
echo -n "    校验叙事摘要结构与协议 ... "
NAR_SUMMARY_RES=$(curl -s "$BASE_URL/api/v1/narrative/summary")
VALID_NAR_SUMMARY=$(echo "$NAR_SUMMARY_RES" | python3 -c "import sys, json; d=json.load(sys.stdin); ok=(isinstance(d.get('title'), str) and isinstance(d.get('summary'), str) and isinstance(d.get('evidence'), list) and isinstance(d.get('actions'), list) and d.get('schema_version')=='NSE-1.0' and isinstance(d.get('generated_at'), str) and isinstance(d.get('inputs'), dict)); print('OK' if ok else 'FAIL')")
if [ "$VALID_NAR_SUMMARY" == "OK" ]; then
    echo "✅ 通过"
else
    echo "❌ 失败（叙事摘要结构或协议不合法）"
    echo "    返回内容: $NAR_SUMMARY_RES"
    FAILED=1
fi

if [ $FAILED -eq 0 ]; then
    echo ">>> 所有检查通过！服务运行正常。"
    exit 0
else
    echo ">>> 检查发现异常，请查看上方错误信息。"
    echo "    建议运行: ./scripts/run_park.sh 查看详细日志"
    exit 1
fi
