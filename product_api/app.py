# product_api/app.py
# FastAPI 服务入口：health + 上传解析 + PII 统计 + 园区大屏接口

import os
import shutil
import json
from typing import Dict, List, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .parser import parse_csv, parse_json, parse_txt
from .record_model import Record
from .pii import scan_records
from .dashboard import (
    get_overview_stats,
    get_trends_data,
    get_alerts_data,
    get_weather_data,
    get_air_quality_data,
    get_integrations_status,
    get_calendar_data
)
from .ui import (
    render_home,
    render_demo_page,
    render_demo_result,
    render_park_dashboard,
    render_docs_cn
)

# 禁用默认文档
app = FastAPI(
    title="红岩 · 园区数字合规共建平台",
    description="园区级数字合规基础设施｜实时审计｜数据治理中枢｜风险控制枢纽",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# 挂载模板目录 (虽然我们主要用内联 HTML，但为了兼容性保留)
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health() -> Dict[str, str]:
    # 健康检查接口：用于部署验收
    return {"status": "ok"}


# --- V1 Dashboard APIs ---

@app.get("/api/v1/overview")
def api_v1_overview() -> Dict[str, Any]:
    """获取大屏概览数据"""
    return get_overview_stats()

@app.get("/api/v1/trends")
def api_v1_trends() -> Dict[str, Any]:
    """获取趋势分析数据"""
    return get_trends_data()

@app.get("/api/v1/alerts")
def api_v1_alerts() -> Dict[str, Any]:
    """获取实时告警数据"""
    return get_alerts_data()

@app.get("/api/v1/integrations")
def api_v1_integrations() -> Dict[str, Any]:
    """获取系统集成状态"""
    return get_integrations_status()

@app.get("/api/v1/weather")
def api_v1_weather() -> Dict[str, Any]:
    """获取天气数据 (模拟)"""
    return get_weather_data()

@app.get("/api/v1/air")
def api_v1_air() -> Dict[str, Any]:
    """获取空气质量数据 (模拟)"""
    return get_air_quality_data()

@app.get("/api/v1/calendar")
def api_v1_calendar() -> Dict[str, Any]:
    """获取日历与节气数据 (模拟)"""
    return get_calendar_data()

# 保留旧接口兼容 (Deprecated)
@app.get("/api/park/dashboard")
def api_park_dashboard_legacy() -> Dict[str, Any]:
    """(已废弃) 请使用 /api/v1/overview"""
    return get_overview_stats()


# --- Pages ---

@app.get("/", response_class=HTMLResponse)
def index():
    """产品首页"""
    return render_home()


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    """企业数据合规检测页"""
    return render_demo_page()


@app.post("/demo/scan", response_class=HTMLResponse)
def demo_scan(text: str = Form(...)):
    """处理合规检测提交"""
    # 构造 Record
    record = Record(
        source_type="demo_text",
        record_id="demo_001",
        content=text,
        metadata={"timestamp": "now"}
    )
    
    # 扫描
    result = scan_records([record.model_dump()])
    
    # 渲染结果
    return render_demo_result(text, result)


@app.get("/park", response_class=HTMLResponse)
def park_page():
    """园区合规大屏展示页"""
    return render_park_dashboard()


@app.get("/docs-cn", response_class=HTMLResponse)
def docs_cn():
    """自定义中文接口文档"""
    return render_docs_cn()


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    """获取原始 OpenAPI 定义"""
    return JSONResponse(app.openapi())


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> Dict:
    # 1) 保存上传文件
    filename = file.filename or "uploaded"
    ext = (filename.split(".")[-1] or "").lower()

    saved_path = os.path.join(UPLOAD_DIR, filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2) 按文件类型解析为统一 Record
    try:
        if ext == "csv":
            records = parse_csv(saved_path, filename)
        elif ext == "json":
            records = parse_json(saved_path, filename)
        elif ext in ("txt", "log"):
            records = parse_txt(saved_path, filename)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload csv/json/txt/log",
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse failed: {e}")

    # 3) 返回样例（避免回包过大，只返回前 1 条）
    return {
        "message": "uploaded and parsed",
        "record_count": len(records),
        "sample_record": records[0].model_dump() if records else None,
    }


@app.post("/scan/pii")
def scan_pii(records: List[Record]) -> Dict:
    # Use real PII scanning implementation
    payload = [r.model_dump() for r in records]
    return scan_records(payload)
