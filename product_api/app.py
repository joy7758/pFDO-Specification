# product_api/app.py
# FastAPI 服务入口：health + 上传解析 + PII 统计占位

import os
import shutil
import json
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>pFDO 合规审计平台</title>
        <style>
            :root {
                --primary-color: #007bff;
                --hover-color: #0056b3;
                --bg-color: #f4f6f9;
                --text-color: #333;
                --secondary-text-color: #666;
            }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
                background-color: var(--bg-color);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 12px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
                text-align: center; 
                max-width: 600px; 
                width: 100%; 
            }
            header {
                margin-bottom: 40px;
            }
            h1 { 
                color: var(--text-color); 
                margin: 0 0 10px 0;
                font-size: 24px;
            }
            .version {
                display: inline-block;
                background: #e9ecef;
                color: #495057;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-bottom: 15px;
            }
            .description { 
                color: var(--secondary-text-color); 
                line-height: 1.6; 
                font-size: 16px;
                margin: 0;
            }
            .actions {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .btn { 
                display: block; 
                padding: 15px; 
                border-radius: 8px; 
                text-decoration: none; 
                font-weight: bold; 
                transition: all 0.2s; 
                text-align: center;
                font-size: 16px;
            }
            .btn-primary { 
                background-color: var(--primary-color); 
                color: white; 
                box-shadow: 0 4px 6px rgba(0,123,255,0.2);
            }
            .btn-primary:hover { 
                background-color: var(--hover-color); 
                transform: translateY(-1px);
                box-shadow: 0 6px 8px rgba(0,123,255,0.25);
            }
            .btn-secondary { 
                background-color: white; 
                color: var(--primary-color); 
                border: 2px solid var(--primary-color); 
            }
            .btn-secondary:hover { 
                background-color: #f8f9fa; 
            }
            .btn-outline {
                color: var(--secondary-text-color);
                border: 1px solid #dee2e6;
                background: white;
            }
            .btn-outline:hover {
                background-color: #f8f9fa;
                color: var(--text-color);
                border-color: #ccedff;
            }
            @media (min-width: 480px) {
                h1 { font-size: 28px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>pFDO 实时合规审计平台</h1>
                <span class="version">v0.1.0-demo</span>
                <p class="description">上传/粘贴数据 → 自动扫描手机号/邮箱/身份证 → 输出可审计结果</p>
            </header>
            
            <div class="actions">
                <a href="/demo" class="btn btn-primary">立即体验 (Demo)</a>
                <a href="/docs" class="btn btn-secondary" target="_blank">接口文档 (Swagger UI)</a>
                <a href="/health" class="btn btn-outline" target="_blank">系统健康检查</a>
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
            textarea { width: 100%; height: 200px; border: 1px solid #ddd; border-radius: 6px; padding: 15px; font-size: 14px; font-family: monospace; resize: vertical; box-sizing: border-box; margin-bottom: 10px; }
            textarea:focus { outline: none; border-color: #007bff; }
            .actions { margin-top: 20px; display: flex; justify-content: space-between; align-items: center; }
            button { background-color: #28a745; color: white; border: none; padding: 12px 30px; border-radius: 6px; font-size: 16px; cursor: pointer; transition: background 0.3s; }
            button:hover { background-color: #218838; }
            .btn-secondary { background-color: #6c757d; }
            .btn-secondary:hover { background-color: #5a6268; }
            .back-link { color: #666; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
        </style>
        <script>
            function fillExample() {
                const example = `这是一段包含敏感信息的示例文本：
1. 客户张三，手机号码是 13812345678，用于接收短信通知。
2. 运营总监李四，工作邮箱为 lisi.work@example-company.com，请勿外传。
3. 临时工王五，身份证号 110101199001011234，入职手续已办理。
4. 其他干扰项：订单号 202305010001，客服电话 400-800-8888（非手机号）。`;
                document.getElementById('text-input').value = example;
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h2>隐私数据扫描演示</h2>
            <form action="/demo/scan" method="post">
                <p>请粘贴包含敏感信息（手机号/邮箱/身份证）的文本内容：</p>
                <textarea id="text-input" name="text" placeholder="在此粘贴文本..."></textarea>
                <div class="actions">
                    <a href="/" class="back-link">← 返回首页</a>
                    <div>
                        <button type="button" class="btn-secondary" onclick="fillExample()" style="margin-right: 10px;">填充示例</button>
                        <button type="submit">开始扫描</button>
                    </div>
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
    highlighted = text
    # 简单高亮替换（注意：实际生产中应处理重叠，演示版直接替换）
    for p in hits["phone"]:
        highlighted = highlighted.replace(p, f"<mark class='phone'>{p}</mark>")
    for e in hits["email"]:
        highlighted = highlighted.replace(e, f"<mark class='email'>{e}</mark>")
    for i in hits["id18"]:
        highlighted = highlighted.replace(i, f"<mark class='idcard'>{i}</mark>")

    json_result = json.dumps(result, ensure_ascii=False, indent=2)
    
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>扫描结果 - pFDO</title>
        <style>
            body {{ font-family: "Microsoft YaHei", sans-serif; background-color: #f4f6f9; padding: 40px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            h2 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-top: 0; }}
            .summary-box {{ background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; }}
            .stat-item {{ text-align: center; border-right: 1px solid #e9ecef; }}
            .stat-item:last-child {{ border-right: none; }}
            .stat-num {{ display: block; font-size: 28px; font-weight: bold; color: #007bff; margin-bottom: 5px; }}
            .stat-label {{ color: #666; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
            
            .section-title {{ font-size: 18px; font-weight: bold; margin: 30px 0 15px; color: #444; border-left: 4px solid #007bff; padding-left: 10px; }}
            
            mark {{ border-radius: 3px; padding: 0 2px; }}
            mark.phone {{ background-color: #bbdefb; color: #000; }}
            mark.email {{ background-color: #c8e6c9; color: #000; }}
            mark.idcard {{ background-color: #ffe0b2; color: #000; }}
            
            .highlight-box {{ background: #fff; border: 1px solid #dee2e6; padding: 20px; border-radius: 6px; white-space: pre-wrap; font-family: monospace; line-height: 1.6; font-size: 14px; max-height: 300px; overflow-y: auto; }}
            
            .json-box {{ position: relative; background: #2d2d2d; color: #f8f8f2; padding: 20px; border-radius: 6px; overflow: auto; max-height: 300px; font-family: Consolas, Monaco, monospace; font-size: 13px; }}
            .copy-btn {{ position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.2); border: none; color: white; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
            .copy-btn:hover {{ background: rgba(255,255,255,0.3); }}

            .actions {{ margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; transition: all 0.2s; }}
            .btn:hover {{ background: #0056b3; transform: translateY(-1px); }}
        </style>
        <script>
            function copyJson() {{
                const text = document.getElementById('json-content').innerText;
                navigator.clipboard.writeText(text).then(() => {{
                    const btn = document.getElementById('copy-btn');
                    btn.innerText = '已复制!';
                    setTimeout(() => btn.innerText = '复制 JSON', 2000);
                }});
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <h2>扫描结果报告</h2>
            
            <div class="summary-box">
                <div class="stat-item">
                    <span class="stat-num">{summary['records']}</span>
                    <span class="stat-label">总记录数</span>
                </div>
                <div class="stat-item">
                    <span class="stat-num">{summary['records_with_pii']}</span>
                    <span class="stat-label">敏感记录</span>
                </div>
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

            <div class="section-title">原文高亮 (Hightlighted Text)</div>
            <div class="highlight-box">{highlighted}</div>

            <div class="section-title">结构化结果 (JSON Output)</div>
            <div class="json-box">
                <button id="copy-btn" class="copy-btn" onclick="copyJson()">复制 JSON</button>
                <pre id="json-content" style="margin:0;">{json_result}</pre>
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
