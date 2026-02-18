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
    
    # 模拟黄历数据 (基于日期hash确保当天固定，隔天变化)
    seed = int(now.strftime("%Y%m%d"))
    random.seed(seed)
    
    yi_pool = ["理发", "出行", "沐浴", "祭祀", "祈福", "求嗣", "解除", "伐木", "装修", "动土", "搬家", "结婚", "开业"]
    ji_pool = ["安床", "栽种", "作灶", "入宅", "安葬", "诉讼", "掘井", "破土", "纳畜"]
    
    yi = random.sample(yi_pool, k=random.randint(3, 5))
    ji = random.sample(ji_pool, k=random.randint(2, 4))
    
    chong_animals = ["马", "羊", "猴", "鸡", "狗", "猪", "鼠", "牛", "虎", "兔", "龙", "蛇"]
    sha_directions = ["东", "南", "西", "北"]
    
    almanac = {
        "yi": yi,
        "ji": ji,
        "chong": f"冲{random.choice(chong_animals)}",
        "sha": f"煞{random.choice(sha_directions)}",
        "jishen": random.sample(["天德", "月德", "天恩", "母仓", "时德", "民日"], k=3),
        "xiongsha": random.sample(["五虚", "九空", "天吏", "致死"], k=2),
        "taishen": random.choice(["房床厕 外东北", "厨灶厕 外西南", "仓库栖 外正北", "占门碓 外东南"]),
        "zhishen": random.choice(["青龙", "明堂", "天刑", "朱雀", "金匮", "天德", "白虎", "玉堂", "天牢", "玄武", "司命", "勾陈"])
    }
    
    # 恢复随机种子以免影响其他随机逻辑
    random.seed()
    
    # 构造展示行
    display_line = f"宜 {'·'.join(yi[:3])}  忌 {'·'.join(ji[:3])}"

def get_ticker_items() -> List[Dict[str, Any]]:
    """获取顶部公告栏 Ticker 数据"""
    items = []
    
    # 1. 天气/环境 (Weather/Air)
    weather = get_weather_data()
    air = get_air_quality_data()
    
    # 体感提示
    temp_feel = weather['current']['feels_like']
    items.append({
        "id": "ticker-weather",
        "type": "weather",
        "level": "INFO",
        "priority": 40,
        "title": "今日天气",
        "summary": f"当前气温 {weather['current']['temp']}℃，体感 {temp_feel}℃，{weather['current']['condition']}，{air['health_tip']}",
        "link": "/park",
        "source": "气象中心"
    })
    
    # 天气预警 (如果有)
    if weather['warning'].get('active'):
        items.append({
            "id": "ticker-warning",
            "type": "weather",
            "level": weather['warning']['level'], # YELLOW/RED...
            "priority": 90,
            "title": "气象预警",
            "summary": f"【{weather['warning']['type']}】{weather['warning']['msg']}",
            "link": "/park",
            "source": "气象局"
        })

    # 2. 实时最高优先级告警 (Alerts)
    alerts = get_alerts_data()['alerts']
    # 找一个 HIGH 级别的最新的
    high_alerts = [a for a in alerts if a['level'] == 'HIGH']
    if high_alerts:
        top_alert = high_alerts[0]
        items.append({
            "id": f"ticker-alert-{top_alert['id']}",
            "type": "alert",
            "level": "RED",
            "priority": 100,
            "title": "紧急告警",
            "summary": f"{top_alert['source']} 发现 {top_alert['type']}，请立即处置！",
            "link": "/park",
            "source": "安防中心"
        })
    
    # 3. 黄历/日历 (Calendar)
    cal = get_calendar_data()
    items.append({
        "id": "ticker-almanac",
        "type": "almanac",
        "level": "INFO",
        "priority": 30,
        "title": "今日黄历",
        "summary": f"{cal['solar_date']} {cal['lunar']}，{cal['display_line']}",
        "link": "/park",
        "source": "历法服务"
    })
    
    items.append({
        "id": "ticker-holiday",
        "type": "calendar",
        "level": "INFO",
        "priority": 20,
        "title": "节日提醒",
        "summary": f"距离 {cal['next_holiday']['name']} 还有 {cal['next_holiday']['days_left']} 天，{cal['term']}节气已过。",
        "link": "/park",
        "source": "行政中心"
    })

    # 4. 今日一句话战报 (Briefing)
    overview = get_overview_stats()
    # 组装战报文案
    briefing_text = (
        f"今日战报：合规评分 {overview['risk_score']}｜"
        f"扫描 {overview['scans_today']:,}｜"
        f"敏感命中 {overview['hits_today']}｜"
        f"实时告警 {overview['alerts_active']}｜"
        f"AQI {air['level']}｜"
        f"体感 {temp_feel}℃"
    )
    
    items.append({
        "id": "ticker-briefing",
        "type": "briefing",
        "level": "INFO",
        "priority": 95, # 仅次于紧急告警
        "title": "园区日报",
        "summary": briefing_text,
        "link": "/park",
        "source": "运营指挥部"
    })
    
    # 按优先级降序排序
    items.sort(key=lambda x: x['priority'], reverse=True)
    return items
