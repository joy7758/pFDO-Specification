# product_api/record_model.py
# 统一 Record 数据结构：所有输入（csv/json/txt）最终都变成它

from typing import Any, Dict
from pydantic import BaseModel


class Record(BaseModel):
    # 数据来源类型：csv / json / txt
    source_type: str

    # 记录唯一 ID
    record_id: str

    # 记录内容：可以是 dict（csv/json）或 str（txt）
    content: Any

    # 额外元信息：行号、文件名、时间等
    metadata: Dict[str, Any] = {}
