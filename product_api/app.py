# product_api/app.py
# FastAPI 服务入口：health + 上传解析 + PII 统计占位

import os
import shutil
from typing import Dict, List, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse

from .parser import parse_csv, parse_json, parse_txt
from .record_model import Record
from .pii import scan_records

app = FastAPI(
    title="pFDO 实时合规审计与敏感信息扫描平台（演示版）",
    description="上传/粘贴数据 → 自动扫描手机号/邮箱/身份证 → 输出可审计结果",
    version="0.1.0-demo"
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>pFDO 合规审计平台</title>
        <style>
            body { font-family: "Microsoft YaHei", sans-serif; background-color: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; max-width: 600px; width: 100%; }
            h1 { color: #333; margin-bottom: 10px; }
            p { color: #666; line-height: 1.6; margin-bottom: 30px; }
            .steps { text-align: left; background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
            .steps li { margin-bottom: 10px; color: #555; }
            .btn { display: inline-block; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; transition: all 0.3s; margin: 0 10px; cursor: pointer; }
            .btn-primary { background-color: #007bff; color: white; border: none; }
            .btn-primary:hover { background-color: #0056b3; }
            .btn-outline { background-color: white; color: #007bff; border: 2px solid #007bff; }
            .btn-outline:hover { background-color: #e9ecef; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>pFDO 实时合规审计平台</h1>
            <p>基于架构师主权模式 (Architect Sovereignty) 的企业级敏感数据扫描引擎</p>
            
            <div class="steps">
                <strong>使用说明：</strong>
                <ol>
                    <li>点击“在线文档”查看标准 API 定义</li>
                    <li>点击“隐私扫描测试”体验实时 PII 识别</li>
                    <li>支持手机号、邮箱、18位身份证自动脱敏检测</li>
                </ol>
            </div>

            <div>
                <a href="/docs" class="btn btn-outline" target="_blank">在线文档 / 接口调试</a>
                <a href="/demo" class="btn btn-primary">隐私扫描测试</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>隐私扫描演示 - pFDO</title>
        <style>
            body { font-family: "Microsoft YaHei", sans-serif; background-color: #f4f6f9; padding: 40px; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            h2 { border-bottom: 2px solid #eee; padding-bottom: 15px; color: #333; }
            textarea { width: 100%; height: 200px; border: 1px solid #ddd; border-radius: 6px; padding: 15px; font-size: 14px; font-family: monospace; resize: vertical; box-sizing: border-box; }
            textarea:focus { outline: none; border-color: #007bff; }
            .actions { margin-top: 20px; text-align: right; }
            button { background-color: #28a745; color: white; border: none; padding: 12px 30px; border-radius: 6px; font-size: 16px; cursor: pointer; transition: background 0.3s; }
            button:hover { background-color: #218838; }
            .back-link { float: left; margin-top: 15px; color: #666; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>隐私数据扫描演示</h2>
            <form action="/demo/scan" method="post">
                <p>请粘贴包含敏感信息（手机号/邮箱/身份证）的文本内容：</p>
                <textarea name="text" placeholder="例如：
用户张三，手机号 13800138000，
邮箱 zhangsan@example.com，
身份证号 110101199003071234..."></textarea>
                <div class="actions">
                    <a href="/" class="back-link">← 返回首页</a>
                    <button type="submit">开始扫描</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    """


@app.post("/demo/scan", response_class=HTMLResponse)
def demo_scan(text: str = Form(...)):
    # 构造 Record
    record = Record(
        source_type="demo_text",
        record_id="demo_001",
        content=text,
        metadata={"timestamp": "now"}
    )
    
    # 扫描
    result = scan_records([record.model_dump()])
    
    # 提取结果
    summary = result["summary"]
    hits = result["per_record"][0]["hits"]
    
    # 渲染 HTML 结果
    phones = "".join(f"<span class='badge phone'>{p}</span>" for p in hits["phone"]) or "无"
    emails = "".join(f"<span class='badge email'>{e}</span>" for e in hits["email"]) or "无"
    ids = "".join(f"<span class='badge idcard'>{i}</span>" for i in hits["id18"]) or "无"
    
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>扫描结果 - pFDO</title>
        <style>
            body {{ font-family: "Microsoft YaHei", sans-serif; background-color: #f4f6f9; padding: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            h2 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
            .summary-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; display: flex; gap: 20px; }}
            .stat-item {{ flex: 1; text-align: center; }}
            .stat-num {{ display: block; font-size: 24px; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; font-size: 14px; }}
            .result-section {{ margin-bottom: 25px; }}
            .result-label {{ font-weight: bold; margin-bottom: 10px; display: block; color: #444; }}
            .badge {{ display: inline-block; padding: 5px 10px; border-radius: 4px; font-size: 14px; margin-right: 8px; margin-bottom: 8px; }}
            .badge.phone {{ background-color: #e3f2fd; color: #0d47a1; border: 1px solid #bbdefb; }}
            .badge.email {{ background-color: #e8f5e9; color: #1b5e20; border: 1px solid #c8e6c9; }}
            .badge.idcard {{ background-color: #fff3e0; color: #e65100; border: 1px solid #ffe0b2; }}
            .raw-text {{ background: #f4f4f4; padding: 15px; border-radius: 6px; white-space: pre-wrap; color: #555; font-family: monospace; font-size: 13px; max-height: 200px; overflow-y: auto; }}
            .actions {{ margin-top: 30px; text-align: center; }}
            .btn {{ display: inline-block; padding: 10px 25px; background: #007bff; color: white; text-decoration: none; border-radius: 6px; }}
            .btn:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>扫描结果报告</h2>
            
            <div class="summary-box">
                <div class="stat-item">
                    <span class="stat-num">{summary['phones_found']}</span>
                    <span class="stat-label">手机号</span>
                </div>
                <div class="stat-item">
                    <span class="stat-num">{summary['emails_found']}</span>
                    <span class="stat-label">邮箱</span>
                </div>
                <div class="stat-item">
                    <span class="stat-num">{summary['id18_found']}</span>
                    <span class="stat-label">身份证</span>
                </div>
            </div>

            <div class="result-section">
                <span class="result-label">📱 发现的手机号：</span>
                <div>{phones}</div>
            </div>

            <div class="result-section">
                <span class="result-label">📧 发现的邮箱：</span>
                <div>{emails}</div>
            </div>

            <div class="result-section">
                <span class="result-label">🆔 发现的身份证：</span>
                <div>{ids}</div>
            </div>
            
            <div class="result-section">
                <span class="result-label">📄 原始文本片段：</span>
                <div class="raw-text">{text[:500]}{'...' if len(text)>500 else ''}</div>
            </div>

            <div class="actions">
                <a href="/demo" class="btn">再次扫描</a>
            </div>
        </div>
    </body>
    </html>
    """



@app.get("/health")
def health() -> Dict[str, str]:
    # 健康检查接口：用于部署验收
    return {"status": "ok"}


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
