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
        "handled_rate": "98.5%",
        "scans_today": 128 + random.randint(0, 50),
        "hits_today": 12 + random.randint(0, 5),
        "alerts_active": 3
    }


def get_trends_data() -> Dict[str, Any]:
    """获取趋势数据 (Trends)"""
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
    
    # 模拟近7天数据
    return {
        "dates": dates,
        "risk_scores": [random.randint(85, 95) for _ in range(7)],
        "alerts_count": [random.randint(2, 10) for _ in range(7)],
        "pii_hits": [random.randint(10, 50) for _ in range(7)],
        "scan_volume": [random.randint(100, 300) for _ in range(7)]
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
    # 模拟已有和可接入系统
    active_systems = [
        {"name": "OA办公系统", "status": "ONLINE", "last_sync": "1分钟前", "type": "SYSTEM"},
        {"name": "CRM客户管理", "status": "ONLINE", "last_sync": "5分钟前", "type": "SYSTEM"},
        {"name": "园区安防监控", "status": "ONLINE", "last_sync": "实时", "type": "IOT"},
        {"name": "访客小程序", "status": "ONLINE", "last_sync": "30秒前", "type": "APP"},
    ]
    
    available_plugins = [
        {"name": "智能门禁系统", "provider": "Hikvision", "category": "安防"},
        {"name": "智慧能耗管理", "provider": "StateGrid", "category": "能源"},
        {"name": "工单流转中心", "provider": "Kingdee", "category": "ERP"},
        {"name": "AI 视频分析", "provider": "SenseTime", "category": "AI"},
        {"name": "财务审计对接", "provider": "Yonyou", "category": "财务"},
    ]
    
    return {
        "systems": active_systems,
        "available_plugins": available_plugins
    }


def get_weather_data() -> Dict[str, Any]:
    """获取天气数据 (模拟)"""
    # 更加丰富的天气数据
    return {
        "current": {
            "temp": 24,
            "feels_like": 26,
            "condition": "多云",
            "humidity": "65%",
            "wind": "东南风 2级",
            "pressure": "1012 hPa",
            "visibility": "10 km",
            "uv": "中等",
            "precip_prob": "10%"
        },
        "hourly": [
            {"time": f"{(datetime.now() + timedelta(hours=i)).hour}:00", 
             "temp": 24 - (i if i < 5 else 10-i), 
             "icon": random.choice(["sun", "cloud", "rain"]), 
             "precip": f"{random.randint(0, 30)}%"} 
            for i in range(12)
        ],
        "daily": [
            {"date": (datetime.now() + timedelta(days=i)).strftime("%m/%d"),
             "high": 28 - random.randint(0, 5),
             "low": 18 + random.randint(0, 3),
             "cond": random.choice(["晴", "多云", "小雨", "雷阵雨"]),
             "precip": f"{random.randint(0, 60)}%"}
            for i in range(7)
        ],
        "warning": {
            "level": "YELLOW", 
            "type": "雷电", 
            "msg": "预计未来3小时有雷电活动", 
            "active": True
        }
    }


def get_air_quality_data() -> Dict[str, Any]:
    """获取空气质量数据 (模拟)"""
    aqi = 45
    return {
        "aqi": aqi,
        "level": "优",
        "primary": "-",
        "pollutants": {
            "pm25": 12,
            "pm10": 28,
            "o3": 45,
            "no2": 18,
            "so2": 6,
            "co": 0.6
        },
        "health_tip": "空气很好，可以外出活动，适宜开窗通风。"
    }

def get_calendar_data() -> Dict[str, Any]:
    """获取日历数据 (模拟)"""
    # 简单模拟农历和节气，实际项目应引入 lunardate 库
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    
    # 模拟下一个节日倒计时
    holidays = [
        {"name": "清明节", "date": "2026-04-05"},
        {"name": "劳动节", "date": "2026-05-01"},
        {"name": "端午节", "date": "2026-06-19"}, 
    ]
    
    next_holiday = holidays[0]
    days_left = (datetime.strptime(next_holiday["date"], "%Y-%m-%d") - now).days
    
    return {
        "solar_date": now.strftime("%Y年%m月%d日"),
        "weekday": weekdays[now.weekday()],
        "lunar": "农历丙午年正月十二", # 假定 2026年
        "term": "雨水", # 假定
        "auspicious": "祭祀, 祈福, 求嗣, 解除, 伐木", # 宜
        "inauspicious": "安床, 栽种, 作灶", # 忌
        "next_holiday": {
            "name": next_holiday["name"],
            "days_left": days_left,
            "date": next_holiday["date"]
        }
    }
