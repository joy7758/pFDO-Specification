#!/bin/bash
# 简单的健康检查脚本

# 1. Check Python Service (Port 8000)
if ! curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "❌ API Service is DOWN (Port 8000)"
    exit 1
fi

# 2. Check UI Page
if ! curl -s http://127.0.0.1:8000/park | grep "园区智能运营中心" > /dev/null; then
    echo "❌ UI Dashboard is not responding correctly"
    exit 1
fi

# 3. Check New APIs
if ! curl -s http://127.0.0.1:8000/api/v1/leader-summary > /dev/null; then
    echo "❌ API /leader-summary is DOWN"
    exit 1
fi

if ! curl -s http://127.0.0.1:8000/api/v1/risk-thermometer > /dev/null; then
    echo "❌ API /risk-thermometer is DOWN"
    exit 1
fi

if ! curl -s http://127.0.0.1:8000/api/v1/streak > /dev/null; then
    echo "❌ API /streak is DOWN"
    exit 1
fi


echo "✅ All Systems Go!"
exit 0
