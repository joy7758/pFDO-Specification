# product_api/dashboard.py
# 园区合规大屏数据接口逻辑
# 提供给 /api/v1/* 使用

import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# 获取上传目录路径（与 app.py 保持一致）
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")


def _get_file_count() -> int:
    """统计实际文件数"""
    if os.path.exists(UPLOAD_DIR):
        try:
            return len([f for f in os.listdir(UPLOAD_DIR) if not f.startswith('.')])
        except OSError:
            pass
    return 0


def get_overview_stats() -> Dict[str, Any]:
    """获取概览数据 (Overview)"""
    file_count = _get_file_count()
    # 模拟数据
    total_records = file_count * 128 + 3456
    risk_score = 92 - (file_count % 5) # 动态一点
    
    return {
        "park_name": "红岩 · 数字化示范园区",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_score": risk_score,
        "total_files": file_count,
        "total_records": total_records,
        "risk_events_today": 3 + (file_count % 3),
        "handled_rate": "98.5%"
    }


def get_trends_data() -> Dict[str, Any]:
    """获取趋势数据 (Trends)"""
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
    
    # 模拟近7天数据
    return {
        "dates": dates,
        "risk_scores": [random.randint(85, 95) for _ in range(7)],
        "alerts_count": [random.randint(2, 10) for _ in range(7)],
        "pii_hits": [random.randint(10, 50) for _ in range(7)]
    }


def get_alerts_data() -> Dict[str, Any]:
    """获取实时告警数据 (Alerts)"""
    # 模拟告警库
    alert_types = ["未脱敏手机号", "明文身份证", "高密级文件传输", "异常IP访问", "API滥用", "敏感词命中"]
    levels = ["HIGH", "MEDIUM", "LOW"]
    sources = ["财务系统", "OA系统", "CRM客户管理", "园区门禁", "访客WIFI"]
    
    alerts = []
    for i in range(20):
        t = datetime.now() - timedelta(minutes=i*15 + random.randint(0, 10))
        alerts.append({
            "id": f"ALT-{int(time.time())}-{i}",
            "time": t.strftime("%H:%M:%S"),
            "level": random.choice(levels),
            "type": random.choice(alert_types),
            "source": random.choice(sources),
            "status": "PENDING" if i < 3 else "HANDLED",
            "msg": f"在{random.choice(['上传文件', 'API请求', '日志流'])}中发现敏感数据"
        })
    return {"alerts": alerts}


def get_integrations_status() -> Dict[str, Any]:
    """获取系统接入状态"""
    return {
        "systems": [
            {"name": "OA办公系统", "status": "ONLINE", "last_sync": "1分钟前", "type": "SYSTEM"},
            {"name": "CRM客户管理", "status": "ONLINE", "last_sync": "5分钟前", "type": "SYSTEM"},
            {"name": "财务审计中心", "status": "OFFLINE", "last_sync": "2小时前", "type": "SYSTEM"},
            {"name": "园区安防监控", "status": "ONLINE", "last_sync": "实时", "type": "IOT"},
            {"name": "访客小程序", "status": "ONLINE", "last_sync": "30秒前", "type": "APP"},
        ]
    }


def get_weather_data() -> Dict[str, Any]:
    """获取天气数据 (模拟)"""
    return {
        "current": {
            "temp": 24,
            "condition": "多云",
            "humidity": "65%",
            "wind": "东南风 2级"
        },
        "forecast": [
            {"time": "14:00", "temp": 25, "icon": "sun"},
            {"time": "15:00", "temp": 25, "icon": "cloud"},
            {"time": "16:00", "temp": 24, "icon": "cloud"},
            {"time": "17:00", "temp": 23, "icon": "rain"},
            {"time": "18:00", "temp": 22, "icon": "rain"}
        ],
        "warning": {"level": "YELLOW", "type": "雷电", "msg": "预计未来3小时有雷电活动"}
    }


def get_air_quality_data() -> Dict[str, Any]:
    """获取空气质量数据 (模拟)"""
    return {
        "aqi": 45,
        "level": "优",
        "pollutants": {
            "pm25": 12,
            "pm10": 28,
            "o3": 45,
            "no2": 18
        },
        "tip": "空气很好，可以外出活动"
    }
