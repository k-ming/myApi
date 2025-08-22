from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query
from dependencies import get_token_header
from pydantic import BaseModel, Field
"""
查询参数模型
"""

router4 = APIRouter(
    prefix="/search_model",
    tags=["查询参数模型"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(get_token_header)],
)

class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, gt=0)
    order_by: Literal["created_at", "updated_at"] = "created_at" # 检查特殊类型注解
    tags: list[str] = []
    model_config = {"extra": "forbid"} # 禁止额外的参数

@router4.get('/items')
async def read_items(filter_query: Annotated[FilterParams, Query()] ):
    """
    :param filter_query: 特殊类型注解 Annotated [T, x]
    :return:
    """
    return filter_query