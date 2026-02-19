# product_api/app.py
# FastAPI 服务入口：health + 上传解析 + PII 统计 + 园区大屏接口

import os
import shutil
import json
import traceback
from typing import Any, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .parser import parse_csv, parse_json, parse_txt
from .record_model import Record
from .pii import scan_records
from .context import set_simulation_mode_context
from .dashboard import (
    get_overview_stats,
    get_trends_data,
    get_alerts_data,
    get_weather_data,
    get_air_quality_data,
    get_integrations_status,
    get_calendar_data,
    get_ticker_items,
    get_briefing_data,
    get_actions_list,
    simulate_action_run,
    get_risk_map,
    get_must_focus,
    get_behavior_stats,
    get_time_pressure,
    get_leader_summary,
    get_risk_thermometer,
    get_streak_stats,
    get_risk_model,
    get_narrative_status,
    get_narrative_series,
    get_narrative_summary
)
from .ui import (
    render_home,
    render_demo_page,
    render_demo_result,
    render_park_dashboard,
    render_docs_cn
)
from .risk_api import router as risk_router
from .metabolism.api import router as entropy_router

# 禁用默认文档
app = FastAPI(
    title="红岩 · 园区数字合规共建平台",
    description="园区级数字合规基础设施｜实时审计｜数据治理中枢｜风险控制枢纽",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

app.include_router(risk_router)
app.include_router(entropy_router)

# 挂载模板目录 (虽然我们主要用内联 HTML，但为了兼容性保留)
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --- Middleware / Dependency ---

async def set_sim_context(request: Request):
    """
    Middleware-like dependency to set simulation mode from query param.
    Priority: query param 'sim' > env var (handled in config.py)
    """
    sim_mode = request.query_params.get("sim")
    # Only allow valid modes
    if sim_mode and sim_mode in ("improving", "stable", "crisis"):
        set_simulation_mode_context(sim_mode)
    else:
        set_simulation_mode_context(None)

# Apply dependency to all routes that use dashboard logic
# But standard FastAPI Depends only works on path operations.
# We will use a global dependency or decorate specific routes.
# Global dependency is easiest for this use case.
# Note: This will run for all requests.
app.router.dependencies.append(Depends(set_sim_context))


@app.get("/health")
def health() -> dict[str, str]:
    # 健康检查接口：用于部署验收
    return {"status": "ok"}


# --- V1 Dashboard APIs ---

@app.get("/api/v1/overview")
def api_v1_overview() -> dict[str, Any]:
    """获取大屏概览数据"""
    return get_overview_stats()

@app.get("/api/v1/trends")
def api_v1_trends() -> dict[str, Any]:
    """获取趋势分析数据"""
    return get_trends_data()

@app.get("/api/v1/alerts")
def api_v1_alerts() -> dict[str, Any]:
    """获取实时告警数据"""
    return get_alerts_data()

@app.get("/api/v1/integrations")
def api_v1_integrations() -> dict[str, Any]:
    """获取系统集成状态"""
    return get_integrations_status()

@app.get("/api/v1/weather")
def api_v1_weather() -> dict[str, Any]:
    """获取天气数据 (模拟)"""
    return get_weather_data()

@app.get("/api/v1/air")
def api_v1_air() -> dict[str, Any]:
    """获取空气质量数据 (模拟)"""
    return get_air_quality_data()

@app.get("/api/v1/calendar")
def api_v1_calendar() -> dict[str, Any]:
    """获取日历与节气数据 (包含黄历宜忌/冲煞等)"""
    return get_calendar_data()

@app.get("/api/v1/ticker")
def api_v1_ticker() -> dict[str, Any]:
    """获取顶部 Ticker 滚动条目 (战报/告警/天气等)"""
    try:
        # 防御式编程：确保 always 200 OK + items
        items = get_ticker_items()
        return {"items": items}
    except Exception as e:
        # Fallback to prevent 500
        print(f"[Error] Ticker failed: {e}")
        return {"items": [], "warning": "Ticker 数据暂不可用，请稍后重试"}

@app.get("/api/v1/briefing")
def api_v1_briefing() -> dict[str, Any]:
    """获取每日运营简报"""
    return get_briefing_data()

@app.get("/api/v1/actions")
def api_v1_actions() -> dict[str, Any]:
    """获取可执行操作列表"""
    return {"actions": get_actions_list()}

@app.post("/api/v1/actions/{action_id}/run")
def api_v1_run_action(action_id: str) -> dict[str, Any]:
    """执行操作"""
    return simulate_action_run(action_id)

@app.get("/api/v1/risk-map")
def api_v1_risk_map() -> dict[str, Any]:
    """获取企业风险地图"""
    return {"risks": get_risk_map()}

@app.get("/api/v1/layout")
def api_v1_get_layout():
    """获取用户布局 (TODO: 暂未启用后端存储，返回默认标识)"""
    return {"layout": "default", "msg": "Layout persistence is client-side only for now."}

@app.post("/api/v1/layout")
def api_v1_save_layout(layout: dict[str, Any] = Body(...)):
    """保存用户布局 (TODO: 暂未启用后端存储)"""
    return {"success": True, "msg": "Layout saved (mock)."}

@app.get("/api/v1/must-focus")
def api_v1_must_focus() -> dict[str, Any]:
    """获取必须关注事项"""
    return get_must_focus()

@app.get("/api/v1/behavior-stats")
def api_v1_behavior_stats() -> dict[str, Any]:
    """获取行为数据统计"""
    return get_behavior_stats()

@app.get("/api/v1/time-pressure")
def api_v1_time_pressure() -> dict[str, Any]:
    """获取时间压力数据"""
    return get_time_pressure()

@app.get("/api/v1/leader-summary")
def api_v1_leader_summary() -> dict[str, Any]:
    """获取领导视角的摘要信息"""
    return get_leader_summary()

@app.get("/api/v1/risk-thermometer")
def api_v1_risk_thermometer() -> dict[str, Any]:
    """获取风险温度计数据"""
    return get_risk_thermometer()

@app.get("/api/v1/streak")
def api_v1_streak() -> dict[str, Any]:
    """获取连续安全天数统计"""
    return get_streak_stats()

@app.get("/api/v1/risk-model")
def api_v1_risk_model() -> dict[str, Any]:
    """获取当前生效的风险评分模型元数据"""
    return get_risk_model()


# --- Narrative Engine APIs (New) ---

@app.get("/api/v1/narrative/status")
def api_v1_narrative_status() -> dict[str, Any]:
    """获取叙事引擎状态"""
    try:
        return get_narrative_status()
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e), "fallback": True}

@app.get("/api/v1/narrative/series")
def api_v1_narrative_series() -> dict[str, Any]:
    """获取叙事趋势序列"""
    try:
        return get_narrative_series()
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e), "fallback": True, "dates": [], "risk_scores": []}

@app.get("/api/v1/narrative/summary")
def api_v1_narrative_summary() -> dict[str, Any]:
    """获取叙事摘要"""
    try:
        return get_narrative_summary()
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e), "fallback": True, "title": "Error", "summary": "Engine Error", "actions": []}


# 保留旧接口兼容 (Deprecated)
@app.get("/api/park/dashboard")
def api_park_dashboard_legacy() -> dict[str, Any]:
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
async def upload(file: UploadFile = File(...)) -> dict:
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
def scan_pii(records: list[Record]) -> dict:
    # Use real PII scanning implementation
    payload = [r.model_dump() for r in records]
    return scan_records(payload)
