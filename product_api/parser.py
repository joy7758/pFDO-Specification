# product_api/parser.py
# 把 CSV / JSON / TXT 解析为统一 Record 列表

import json
import uuid
from typing import List

import pandas as pd

from .record_model import Record


def parse_csv(file_path: str, filename: str) -> List[Record]:
    # 读取 CSV
    df = pd.read_csv(file_path)

    records: List[Record] = []

    # 每行转为 Record
    for idx, row in df.iterrows():
        records.append(
            Record(
                source_type="csv",
                record_id=str(uuid.uuid4()),
                content=row.to_dict(),
                metadata={"filename": filename, "row_number": int(idx) + 1},
            )
        )

    return records


def parse_json(file_path: str, filename: str) -> List[Record]:
    # 读取 JSON 文件
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records: List[Record] = []

    # 支持两种常见 JSON：
    # 1) 列表：[{...},{...}]
    # 2) 单对象：{...}
    if isinstance(data, list):
        for idx, item in enumerate(data):
            records.append(
                Record(
                    source_type="json",
                    record_id=str(uuid.uuid4()),
                    content=item,
                    metadata={"filename": filename, "item_index": idx},
                )
            )
    else:
        records.append(
            Record(
                source_type="json",
                record_id=str(uuid.uuid4()),
                content=data,
                metadata={"filename": filename},
            )
        )

    return records


def parse_txt(file_path: str, filename: str) -> List[Record]:
    # 读取文本内容（按行拆分为多条记录）
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    records: List[Record] = []

    for idx, line in enumerate(lines):
        # 空行跳过
        if not line.strip():
            continue

        records.append(
            Record(
                source_type="txt",
                record_id=str(uuid.uuid4()),
                content=line,
                metadata={"filename": filename, "line_number": idx + 1},
            )
        )

    return records
