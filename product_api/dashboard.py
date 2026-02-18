# product_api/dashboard.py
# 园区合规大屏数据接口逻辑
# 提供给 /api/v1/* 使用

import os
import random
import time
import hashlib
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .config import (
    is_demo_mode, 
    get_demo_seed, 
    is_simulation_mode, 
    get_simulation_mode, 
    get_sim_start_date, 
    get_data_mode,
    get_simulation_label
)
from .context import get_simulation_mode_context
from .narrative import (
    generate_trend_series, 
    today_snapshot, 
    narrative_summary,
    get_narrative_status_data
)
from .ingest import get_status as get_ingest_status, get_ingest_level

# 获取上传目录路径（与 app.py 保持一致）
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
ENGINE_VERSION = "RRM-1.0"
NARRATIVE_VERSION = "NSE-2.0"
NARRATIVE_SCHEMA_VERSION = "NSE-1.0"


def _clamp_0_100(value: float) -> int:
    return int(max(0, min(100, round(value))))


def _build_narrative_inputs() -> Dict[str, Any]:
    data_mode = get_data_mode()
    source = "query_param" if get_simulation_mode_context() else "env_var"
    payload: Dict[str, Any] = {
        "data_mode": data_mode,
        "source": source,
        "sim": get_simulation_mode()
    }
    if data_mode in ("demo", "simulation"):
        payload["seed"] = get_demo_seed()
    return payload

def _rng(tag: str):
    """
    根据 DEMO_MODE 返回随机数生成器。
    - True: 返回基于 (SEED + DATE + TAG) 的稳定 Random 实例
    - False: 返回系统 random 模块
    """
    if is_demo_mode():
        seed_val = get_demo_seed()
        date_str = datetime.now().strftime("%Y%m%d")
        # Mix seed, date, and tag for unique but stable randomness per day/module
        raw = f"{seed_val}-{date_str}-{tag}"
        # Use SHA256 to get a good distribution
        h = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        # Take first 8 chars as int seed
        s = int(h[:8], 16)
        return random.Random(s)
    return random

def _get_file_count() -> int:
    """统计实际文件数"""
    if os.path.exists(UPLOAD_DIR):
        try:
            return len([f for f in os.listdir(UPLOAD_DIR) if not f.startswith('.')])
        except OSError:
            pass
    return 0

def calculate_dynamic_risk_score() -> Dict[str, Any]:
    """计算动态合规指数 (核心算法)"""
    if is_simulation_mode():
        # 叙事模拟模式托底
        snap = today_snapshot()
        compliance_score = _clamp_0_100(snap["risk_score"])
        risk_score = _clamp_0_100(100 - compliance_score)
        return {
            "score": compliance_score,
            "compliance_score": compliance_score,
            "risk_score": risk_score,
            "file_count": 120, # Mock
            "hits_today": snap["hits_today"],
            "alerts_active": snap["alerts_active"],
            "factors": {}
        }

    # 基础分
    base_score = 100
    
    # 因子 1: 文件存量 (每10个文件扣1分，上限15分)
    file_count = _get_file_count()
    file_penalty = min(15, file_count // 10)
    
    # 因子 2: 模拟的敏感数据命中 (随机波动)
    hits_today = 12 + random.randint(0, 5)
    hits_penalty = min(20, hits_today // 2)
    
    # 因子 3: 活跃告警 (每个扣5分)
    alerts_active = 3
    alert_penalty = min(30, alerts_active * 5)
    
    # 计算总分
    final_score = base_score - file_penalty - hits_penalty - alert_penalty
    
    # 修正范围
    compliance_score = _clamp_0_100(final_score)
    risk_score = _clamp_0_100(100 - compliance_score)
    
    return {
        "score": compliance_score,
        "compliance_score": compliance_score,
        "risk_score": risk_score,
        "file_count": file_count,
        "hits_today": hits_today,
        "alerts_active": alerts_active,
        "factors": {
            "base": base_score,
            "file_penalty": file_penalty,
            "hits_penalty": hits_penalty,
            "alert_penalty": alert_penalty
        }
    }

def get_risk_model() -> Dict[str, Any]:
    """获取风险模型元数据"""
    return {
        "engine": "RedRock Risk Engine",
        "version": ENGINE_VERSION,
        "algorithm": "Weighted Decay (WD-26)",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "factors": [
            {"name": "Data Volume", "weight": "15%", "desc": "Based on file storage count"},
            {"name": "PII Hits", "weight": "35%", "desc": "Sensitive data patterns found"},
            {"name": "Active Alerts", "weight": "50%", "desc": "Unresolved security incidents"}
        ]
    }

def get_overview_stats() -> Dict[str, Any]:
    """获取概览数据 (Overview)"""
    risk_data = calculate_dynamic_risk_score()
    
    # 模拟数据
    total_records = risk_data['file_count'] * 128 + 3456
    
    ver = NARRATIVE_VERSION if is_simulation_mode() else ENGINE_VERSION

    ingest_summary = get_ingest_status()
    ingest_counters = ingest_summary.get("counters", {})
    ingest_level = get_ingest_level()

    return {
        "park_name": "红岩 · 数字化示范园区",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engine_version": ver,
        "risk_score": risk_data['risk_score'],
        "compliance_score": risk_data['compliance_score'],
        "total_files": risk_data['file_count'],
        "total_records": total_records,
        "risk_events_today": 3 + (risk_data['file_count'] % 3),
        "handled_rate": "98.5%",
        "scans_today": risk_data.get('scans_today', 128 + random.randint(0, 50)),
        "hits_today": risk_data['hits_today'],
        "alerts_active": risk_data['alerts_active'],
        "ingest": {
            "watch_dir": ingest_summary.get("watch_dir", ""),
            "running": ingest_summary.get("runtime", {}).get("running", False),
            "today_seen": ingest_counters.get("today_seen", 0),
            "today_processed": ingest_counters.get("today_processed", 0),
            "today_failed": ingest_counters.get("today_failed", 0),
            "today_pii_hits": ingest_counters.get("today_pii_hits", 0),
            "ingest_level": ingest_level,
        },
        "ingest_level": ingest_level
    }


def get_trends_data() -> Dict[str, Any]:
    """获取趋势数据 (Trends) - 升级为 30 天"""
    if is_simulation_mode():
        trends = generate_trend_series(30)
        trends["engine_version"] = NARRATIVE_VERSION
        return trends
        
    # Demo/Random Mode - generate 30 days mock
    days = 30
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(days-1, -1, -1)]
    
    return {
        "engine_version": ENGINE_VERSION,
        "dates": dates,
        "risk_scores": [random.randint(85, 95) for _ in range(days)],
        "alerts_count": [random.randint(2, 10) for _ in range(days)],
        "pii_hits": [random.randint(10, 50) for _ in range(days)],
        "scan_volume": [random.randint(100, 300) for _ in range(days)]
    }


def get_alerts_data() -> Dict[str, Any]:
    """获取实时告警数据 (Alerts)"""
    # 模拟告警库
    alert_types = ["未脱敏手机号", "明文身份证", "高密级文件传输", "异常IP访问", "API滥用", "敏感词命中"]
    levels = ["HIGH", "MEDIUM", "LOW"]
    sources = ["财务系统", "OA系统", "CRM客户管理", "园区门禁", "访客WIFI"]
    
    count = 20
    if is_simulation_mode():
        snap = today_snapshot()
        # Make alerts consistent with snapshot count if possible, but here we just mock list
        # If crisis, more HIGH alerts
        mode = get_simulation_mode()
        if mode == "crisis":
             levels = ["HIGH", "HIGH", "MEDIUM"]
             count = 30
        elif mode == "improving":
             levels = ["LOW", "MEDIUM"]
             count = 5
    
    alerts = []
    for i in range(count):
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
    return {
        "engine_version": ENGINE_VERSION,
        "alerts": alerts
    }


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
        "engine_version": ENGINE_VERSION,
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
            "precip_prob": "10%",
            "icon": "cloud"
        },
        "hourly": [
            {"time": f"{(datetime.now() + timedelta(hours=i)).hour}:00", 
             "temp": 24 - (i if i < 5 else 10-i), 
             "icon": random.choice(["sun", "cloud", "rain"]), 
             "precip": f"{random.randint(0, 30)}%"} 
            for i in range(24)
        ],
        "daily": [
            {"date": (datetime.now() + timedelta(days=i)).strftime("%m/%d"),
             "day_name": (datetime.now() + timedelta(days=i)).strftime("%A"),
             "high": 28 - random.randint(0, 5),
             "low": 18 + random.randint(0, 3),
             "cond": random.choice(["晴", "多云", "小雨", "雷阵雨"]),
             "icon": random.choice(["sun", "cloud", "rain", "bolt"]),
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
        "trend": "stable", # stable, rising, falling
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
    weekday_str = weekdays[now.weekday()]
    
    # 模拟下一个节日倒计时
    holidays = [
        {"name": "清明节", "date": "2026-04-05"},
        {"name": "劳动节", "date": "2026-05-01"},
        {"name": "端午节", "date": "2026-06-19"}, 
    ]
    
    next_holiday = holidays[0]
    days_left = (datetime.strptime(next_holiday["date"], "%Y-%m-%d") - now).days
    
    # 园区自定义倒计时
    custom_event = {"name": "园区周年庆", "date": "2026-10-01"}
    custom_days_left = (datetime.strptime(custom_event["date"], "%Y-%m-%d") - now).days

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
    
    display_line = f"宜 {'·'.join(yi[:3])}  忌 {'·'.join(ji[:3])}"

    return {
        "solar_date": now.strftime("%Y年%m月%d日"),
        "weekday": weekday_str,
        "lunar": "丙午年 二月 初一", # 模拟
        "term": "惊蛰", # 模拟
        "next_holiday": {"name": next_holiday["name"], "days_left": days_left},
        "custom_countdown": {"name": custom_event["name"], "days_left": custom_days_left},
        "almanac": almanac,
        "display_line": display_line
    }

def get_risk_map() -> List[Dict[str, Any]]:
    """获取企业风险地图"""
    risks = [
        {"name": "供应链数据泄露风险", "level": "high", "reason": "监测到上游供应商接口存在明文传输"},
        {"name": "员工账号异常登录", "level": "high", "reason": "短时间内跨省登录 IP 异常"},
        {"name": "财务报表敏感词命中", "level": "mid", "reason": "年度财报草稿中包含未脱敏薪资数据"},
        {"name": "访客系统权限过大", "level": "low", "reason": "临时访客账号具备部分内网访问权限"},
        {"name": "过期文档未清理", "level": "low", "reason": "共享盘存在超过 3 年的废弃合同扫描件"}
    ]
    return risks

def get_actions_list() -> List[Dict[str, Any]]:
    """获取可执行操作列表"""
    # 叙事模式下，动作由引擎决定
    if is_simulation_mode():
        nar = narrative_summary()
        # Transform simple label to name/description if needed or use as is
        # The prompt says: buttons reuse existing actions/run.
        # narrative.py returns actions with id/label. We map it to id/name/desc.
        res = []
        for a in nar.get("actions", []):
            res.append({
                "id": a["id"],
                "name": a["label"],
                "description": "建议立即执行该操作",
                "status": "ready"
            })
        return res

    return [
        {"id": "act_001", "name": "全园扫描", "description": "立即启动全量数据合规扫描", "status": "ready"},
        {"id": "act_002", "name": "一键阻断", "description": "阻断所有高风险外部连接", "status": "ready"},
        {"id": "act_003", "name": "生成报表", "description": "生成并发送今日合规日报", "status": "processing"},
        {"id": "act_004", "name": "清除缓存", "description": "清理系统临时文件与缓存", "status": "ready"}
    ]

def simulate_action_run(action_id: str) -> Dict[str, Any]:
    """模拟执行操作"""
    # 模拟耗时
    time.sleep(0.5) 
    actions = get_actions_list()
    action = next((a for a in actions if a["id"] == action_id), None)
    
    if not action:
         return {
            "success": False,
            "id": action_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "操作不存在"
        }
        
    return {
        "success": True,
        "id": action_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"操作「{action['name']}」已成功加入执行队列"
    }

def get_briefing_data() -> Dict[str, Any]:
    """获取每日运营简报 (Briefing)"""
    try:
        # 1. 获取基础数据
        overview = get_overview_stats()
        
        # 叙事模式
        if is_simulation_mode():
            nar = narrative_summary()
            snap = today_snapshot()
            
            summary = nar["summary"]
            # Generate suggestion from summary or add custom logic
            suggestion = "请根据上方叙事指引执行对应操作。"
            
            return {
                "title": "每日运营简报",
                "date": datetime.now().strftime("%Y年%m月%d日"),
                "engine_version": NARRATIVE_VERSION,
                "summary": summary,
                "suggestion": suggestion,
                "status_level": nar["level"],
                "kpis": [
                    {"label": "今日扫描", "value": f"{overview.get('scans_today', 0):,}", "unit": "次", "color": "blue"},
                    {"label": "敏感命中", "value": f"{overview.get('hits_today', 0):,}", "unit": "条", "color": "orange"},
                    {"label": "实时告警", "value": overview.get('alerts_active', 0), "unit": "个", "color": "red"},
                    {"label": "合规指数", "value": overview.get('compliance_score', 0), "unit": "分", "color": "green"},
                ],
                "links": [],
                "must_focus_count": snap.get("must_focus_count", 0)
            }
        
        # 原逻辑
        trends = get_trends_data()
        alerts_data = get_alerts_data()
        risk_map = get_risk_map()
        
        # 计算 high risks
        high_risks = len([r for r in risk_map if r['level'] == 'high'])
        
        # 2. 计算 KPIs
        kpis = [
            {"label": "今日扫描", "value": f"{overview.get('scans_today', 0):,}", "unit": "次", "color": "blue"},
            {"label": "敏感命中", "value": f"{overview.get('hits_today', 0):,}", "unit": "条", "color": "orange"},
            {"label": "实时告警", "value": overview.get('alerts_active', 0), "unit": "个", "color": "red"},
            {"label": "合规指数", "value": overview.get('compliance_score', 0), "unit": "分", "color": "green"},
            {"label": "自动处理", "value": overview.get('handled_rate', '0%'), "unit": "", "color": "grey"}
        ]
        
        # 3. 生成 Summary
        score = overview.get('compliance_score', 0)
        scan_vol = overview.get('scans_today', 0)
        hits = overview.get('hits_today', 0)
        active_alerts = overview.get('alerts_active', 0)
        
        summary = f"今日合规指数 {score}，累计扫描 {scan_vol} 次。发现 {hits} 条敏感数据，当前 {active_alerts} 个待处理告警，系统整体运行平稳。"
        
        # 4. 生成 Suggestion
        if score >= 90:
            suggestion = "✅ 园区数据安全状况良好，请继续保持常态化监控，建议定期复查自动处置策略的有效性。"
            status_level = "low"
        elif score >= 80:
            suggestion = "⚠️ 存在少量合规风险，建议重点关注财务与客户管理系统的敏感数据传输，及时清理未脱敏文档。"
            status_level = "medium"
        else:
            suggestion = "🚨 风险指数较高！请立即检查高频告警源，建议启动应急响应流程并对关键系统进行全面审计。"
            status_level = "high"
            
        # 5. Links
        links = [
            {"text": "查看告警", "url": "/park#alert-list", "type": "danger" if active_alerts > 0 else "default"},
            {"text": "查看趋势", "url": "/park#chart-scan", "type": "primary"},
            {"text": "系统接入", "url": "/park#sys-list", "type": "default"}
        ]

        return {
            "title": "每日运营简报",
            "date": datetime.now().strftime("%Y年%m月%d日"),
            "engine_version": ENGINE_VERSION,
            "summary": summary,
            "suggestion": suggestion,
            "status_level": status_level,
            "kpis": kpis,
            "links": links,
            "must_focus_count": high_risks
        }
    except Exception as e:
        # Fallback
        traceback.print_exc()
        return {
            "title": "每日运营简报",
            "date": datetime.now().strftime("%Y年%m月%d日"),
            "summary": "数据同步中，请稍后查看...",
            "suggestion": "系统正在初始化，请保持网络连接畅通。",
            "status_level": "low",
            "kpis": [],
            "links": [],
            "must_focus_count": 0
        }

def get_ticker_items() -> List[Dict[str, Any]]:
    """获取顶部公告栏 Ticker 数据 (多源聚合/异常容错)"""
    items = []
    
    # 辅助函数：构造标准 Item
    def make_item(priority, level, tag, title, summary, link, source="红岩"):
        return {
            "id": f"tick-{int(time.time()*1000)}-{random.randint(100,999)}",
            "priority": priority, # 0=Red, 1=Orange, 2=Blue, 3=Green, 4=Grey
            "level": level,       # "红", "橙", "蓝", "绿", "灰"
            "tag": tag,
            "title": title,
            "summary": summary,
            "time": datetime.now().strftime("%H:%M"),
            "link": link,
            "source": source
        }

    # 1. 天气/环境 (Weather/Air)
    try:
        weather = get_weather_data()
        air = get_air_quality_data()
        
        # 气象预警 (Priority 1 - Orange/Red)
        warning = weather.get('warning', {})
        if warning.get('active'):
            w_level = "红" if "RED" in warning.get('level', '') else "橙"
            prio = 0 if w_level == "红" else 1
            items.append(make_item(
                prio, w_level, "天气预警", 
                f"{warning.get('type')}预警", 
                warning.get('msg', ''), 
                "/park#weather", "气象局"
            ))
            
        # 正常天气 (Priority 2 - Blue)
        cur = weather.get('current', {})
        items.append(make_item(
            2, "蓝", "今日天气", 
            f"{cur.get('condition')} {cur.get('temp')}℃",
            f"体感 {cur.get('feels_like')}℃，{air.get('health_tip', '')}",
            "/park#weather", "气象中心"
        ))
        
        # 空气质量 (Priority 2 or 1 if bad)
        aqi = air.get('aqi', 0)
        aqi_level = "橙" if aqi > 100 else "绿" # 简单判断
        prio_aqi = 1 if aqi > 100 else 3
        items.append(make_item(
            prio_aqi, aqi_level, "空气质量",
            f"AQI {aqi} {air.get('level')}",
            air.get('health_tip'),
            "/park#air", "环保局"
        ))

    except Exception:
        # Fallback for weather
        items.append(make_item(4, "灰", "天气提示", "天气数据暂不可用", "请稍后重试", "/park#weather"))

    # 2. 实时告警 (Alerts)
    try:
        alerts_data = get_alerts_data()
        alerts = alerts_data.get('alerts', [])
        # 筛选 High/Medium
        high_alerts = [a for a in alerts if a['level'] == 'HIGH']
        
        # 只取最新的1条 HIGH 告警作为 ticker (避免刷屏)
        if high_alerts:
            top = high_alerts[0]
            items.append(make_item(
                0, "红", "系统告警",
                "发现高风险异常",
                f"{top.get('source')}：{top.get('msg')}",
                "/park#alerts", "安防中心"
            ))
        else:
            # 如果没有 High，看看 Medium
            med_alerts = [a for a in alerts if a['level'] == 'MEDIUM']
            if med_alerts:
                top = med_alerts[0]
                items.append(make_item(
                    1, "橙", "风险提示",
                    "发现潜在风险",
                    f"{top.get('source')}：{top.get('msg')}",
                    "/park#alerts", "安防中心"
                ))
    except Exception:
        pass

    # 3. 黄历/日历 (Calendar)
    try:
        cal = get_calendar_data()
        
        # 节日倒计时 (Priority 3 - Green)
        next_h = cal.get('next_holiday', {})
        if next_h:
            days = next_h.get('days_left', 0)
            items.append(make_item(
                3, "绿", "节日提醒",
                f"距离 {next_h.get('name')} 还有 {days} 天",
                f"今日节气：{cal.get('term')}",
                "/park#calendar", "行政中心"
            ))
            
        # 黄历 (Priority 3 - Green)
        display = cal.get('display_line', '')
        items.append(make_item(
            3, "绿", "今日黄历",
            f"{cal.get('lunar')}",
            display,
            "/park#calendar", "历法服务"
        ))
    except Exception:
        pass

    # 4. 运营简报 (Briefing)
    try:
        # 简报摘要 (Priority 4 - Gray)
        # 复用 get_briefing_data 可能会递归调用导致慢，这里直接取 overview
        overview = get_overview_stats()
        briefing_text = (
            f"扫描 {overview.get('scans_today', 0):,} 次｜"
            f"敏感命中 {overview.get('hits_today', 0)}｜"
            f"合规指数 {overview.get('compliance_score', 0)}"
        )
        items.append(make_item(
            4, "灰", "运营简报",
            "今日合规日报",
            briefing_text,
            "/park#briefing", "运营指挥部"
        ))
    except Exception:
        pass

    # 5. 系统接入 (Integrations)
    try:
        integ = get_integrations_status()
        systems = integ.get('systems', [])
        sys_names = [s['name'] for s in systems[:3]]
        items.append(make_item(
            4, "灰", "系统接入",
            "已接入子系统",
            f"{' / '.join(sys_names)} 运行正常",
            "/park#integrations", "系统监控"
        ))
    except Exception:
        pass

    # 排序：priority ASC (0最重要)
    items.sort(key=lambda x: x['priority'])
    
    # 兜底：如果items为空
    if not items:
        items.append(make_item(4, "灰", "系统提示", "系统运行正常", "暂无更多通知", "/park"))

    return items

def get_must_focus() -> Dict[str, Any]:
    """获取必须关注事项 (Must Focus)"""
    if is_simulation_mode():
        snap = today_snapshot()
        count = snap.get("must_focus_count", 0)
        level = "high" if count > 0 else "low"
        
        # Mock some items if count > 0
        items = []
        if count > 0:
            for i in range(min(count, 5)):
                 items.append({"type": "risk", "desc": "模拟高风险项", "reason": "叙事引擎生成的风险事件"})
                 
        return {
            "count": count,
            "level": level,
            "items": items,
            "suggestion": "请根据叙事引擎指示处理风险。"
        }

    # 聚合 High Risks 和 Alerts
    risk_map = get_risk_map()
    high_risks = [r for r in risk_map if r['level'] == 'high']
    
    alerts_data = get_alerts_data()
    high_alerts = [a for a in alerts_data.get('alerts', []) if a['level'] == 'HIGH']
    
    total = len(high_risks) + len(high_alerts)
    level = "high" if total > 0 else "low"
    
    items = []
    for r in high_risks:
        items.append({"type": "risk", "desc": r['name'], "reason": r['reason']})
    for a in high_alerts:
        items.append({"type": "alert", "desc": a['type'], "reason": a['msg']})
        
    return {
        "count": total,
        "level": level,
        "items": items[:5], # Limit
        "suggestion": "请立即处理以上高风险项，避免合规事故扩散。" if total > 0 else "当前无必须关注的高风险项。"
    }

def get_behavior_stats() -> Dict[str, Any]:
    """获取行为数据统计 (Behavior Stats)"""
    # 模拟用户行为数据
    return {
        "active_users": random.randint(50, 200),
        "actions_today": random.randint(500, 2000),
        "avg_response_time": f"{random.randint(100, 500)}ms",
        "most_active_module": random.choice(["数据扫描", "报表下载", "告警处置", "日志查询"]),
        "compliance_trend": "rising" # rising, falling, flat
    }

def get_time_pressure() -> Dict[str, Any]:
    """获取时间压力数据 (Time Pressure)"""
    # 模拟任务截止压力
    pending_tasks = random.randint(3, 15)
    urgent_tasks = random.randint(0, 5)
    
    level = "high" if urgent_tasks > 3 else ("medium" if urgent_tasks > 0 else "low")
    
    return {
        "pending_tasks": pending_tasks,
        "urgent_tasks": urgent_tasks,
        "next_deadline": (datetime.now() + timedelta(hours=random.randint(1, 48))).strftime("%m-%d %H:%M"),
        "level": level,
        "pressure_score": random.randint(40, 90) # 0-100
    }

def get_leader_summary() -> Dict[str, Any]:
    """获取领导视角的摘要信息"""
    return {
        "efficiency": f"{random.randint(85, 98)}%",
        "team_status": "高效协同",
        "budget_usage": f"{random.randint(40, 70)}%",
        "core_metric": "平稳"
    }

def get_risk_thermometer() -> Dict[str, Any]:
    """获取风险温度计数据 (基于动态模型)"""
    if is_simulation_mode():
        snap = today_snapshot()
        return {
            "temperature": snap["temperature"],
            "level": "high" if snap["temperature"] > 80 else ("medium" if snap["temperature"] > 50 else "low"),
            "max": 100,
            "source_score": _clamp_0_100(100 - snap["temperature"]),
            "engine_version": NARRATIVE_VERSION
        }

    # 使用动态评分模型计算
    risk_data = calculate_dynamic_risk_score()
    score = risk_data['compliance_score']
    
    # 评分 (0-100, 100=安全) 转换为 温度 (0-100, 100=危险)
    # 反向映射：Score 100 -> Temp 0; Score 0 -> Temp 100
    base_temp = 100 - score
    
    # 加上一点随机波动模拟实时感
    final_temp = base_temp + random.randint(-5, 5)
    final_temp = max(10, min(100, final_temp)) # 限制在 10-100 之间显示
    
    level = "low"
    if final_temp > 80:
        level = "high"
    elif final_temp > 50:
        level = "medium"
        
    return {
        "temperature": final_temp,
        "level": level,
        "max": 100,
        "source_score": score,
        "engine_version": ENGINE_VERSION
    }

def get_streak_stats() -> Dict[str, Any]:
    """获取连续安全天数统计"""
    streak = random.randint(5, 120)
    return {
        "safe_days": streak,
        "record_days": 365,
        "last_incident": (datetime.now() - timedelta(days=streak)).strftime("%Y-%m-%d")
    }

# --- Narrative Extensions ---

def get_narrative_status() -> Dict[str, Any]:
    """获取叙事引擎状态"""
    status = get_narrative_status_data()
    # Add label for display
    status["effective_mode_label"] = get_simulation_label(status["effective_mode"])
    status["schema_version"] = NARRATIVE_SCHEMA_VERSION
    status["generated_at"] = datetime.now().isoformat()
    status["inputs"] = _build_narrative_inputs()
    return status

def get_narrative_series() -> Dict[str, Any]:
    """获取叙事趋势序列"""
    return generate_trend_series(30)

def get_narrative_summary() -> Dict[str, Any]:
    """获取叙事摘要"""
    payload = narrative_summary()
    payload["schema_version"] = NARRATIVE_SCHEMA_VERSION
    payload["generated_at"] = datetime.now().isoformat()
    payload["inputs"] = _build_narrative_inputs()
    return payload
