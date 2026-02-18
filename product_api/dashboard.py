# product_api/dashboard.py
# 园区合规大屏数据接口逻辑
# 提供给 /api/park/dashboard 使用

import os
import random
from datetime import datetime
from typing import Dict, Any, List

# 获取上传目录路径（与 app.py 保持一致）
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")


def get_dashboard_stats() -> Dict[str, Any]:
    """
    获取园区合规大屏的实时统计数据
    
    返回字段包含：
    - park_name: 园区名称
    - risk_score: 当前风险评分 (0-100)
    - total_files: 已扫描文件总数
    - total_records: 已处理数据条数（模拟）
    - recent_alerts: 最近告警列表
    """
    
    # 1. 统计实际文件数
    file_count = 0
    if os.path.exists(UPLOAD_DIR):
        try:
            # 排除隐藏文件
            files = [f for f in os.listdir(UPLOAD_DIR) if not f.startswith('.')]
            file_count = len(files)
        except OSError:
            file_count = 0

    # 2. 模拟/计算其他业务指标（演示用）
    # 假设每文件平均 100 条记录
    total_records = file_count * 125 + random.randint(0, 50)
    
    # 随机生成一些演示用的告警数据
    alerts = [
        {"time": "10:23:45", "level": "HIGH", "type": "未脱敏手机号", "msg": "发现明文手机号传输"},
        {"time": "09:15:30", "level": "MEDIUM", "type": "格式异常", "msg": "CSV 字段缺失"},
        {"time": "08:05:12", "level": "LOW", "type": "系统日志", "msg": "每日自动扫描完成"},
    ]

    return {
        "park_name": "红岩 · 数字化示范园区",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_score": 92,  # 分数越高越安全
        "status": "RUNNING",
        "statistics": {
            "total_files_scanned": file_count,
            "total_records_processed": total_records,
            "pending_tasks": 0,
            "risk_events_today": 3
        },
        "recent_alerts": alerts
    }
