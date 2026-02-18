# product_api/app.py
# FastAPI 服务入口：health + 上传解析 + PII 统计占位

import os
import shutil
from typing import Dict, List, Any

from fastapi import FastAPI, File, UploadFile, HTTPException

from .parser import parse_csv, parse_json, parse_txt
from .record_model import Record
from .pii import scan_records

app = FastAPI(title="pFDO Compliance Engine (P0)", version="0.1.0")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
