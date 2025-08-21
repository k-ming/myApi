from dataclasses import Field
from decimal import Decimal

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime, timedelta, timezone, time, date
from uuid import UUID

router3 = APIRouter(
    prefix="/requestExtra",
    tags=["请求体额外信息-示例-数据类型"]
)

class Schema(BaseModel):
    name: str
    description: str | None = None
    price: int | None = None

class ModelSchema(BaseModel):
    name: str
    description: str | None = None
    price: int | None = None
    model_config = {  # schema 可以直接填充在请求体中
        "json_schema_extra": {
            "example": {
                "name": "polly",
                "description": "在model中添加的示例",
                "price": 109
            }
        }
    }

class FieldSchema(BaseModel):
    name: str = Field(examples=['Field 提供的参数说明'])
    description: str | None = Field(examples=['Field 提供的参数说明'])
    price: int | None = None

@router3.post("/ModelSchema", name="给模型添加示例")
async def create_model_schema(model_schema: ModelSchema):
    return model_schema

@router3.put("/FiledSchema", name="给字段添加示例")
async def update_filed_schema(filed_schema: FieldSchema):
    return filed_schema

@router3.put("/BodySchema/{sch_id}", name="给请求体添加额外示例")
async def update_schema(
        sch_id: int,
        schema: Annotated[
            Schema,
            Body(examples=[
                {"name": "tiky",
                 "description": "给请求体中添加示例", }
                ]
            )
        ]
) -> dict[str, int | Schema]:
    """
    :param sch_id: 请求Id \n
    :param schema: 结合typing.Annotated[] 和 fastapi.Body 实现参数化提示 \n
    :return:
    """
    return {"sch_id": sch_id, "schema": schema}


@router3.post("/extractDataType", name="额外的数据类型")
async def create_schema(
        uuid: Annotated[UUID, Body(examples=["550e8400-e29b-41d4-a716-446655440000"])],
        start_time: Annotated[datetime, Body()],
        end_time: Annotated[datetime, Body()],
        process_after: Annotated[timedelta, Body()],
        repeat_time: Annotated[time | None, Body()] = None,
) -> dict:
    """
    :额外的数据类型
    - uuid: "通用唯一标识符" ，在许多数据库和系统中用作ID \n
    - start_time: 一个 Python datetime.datetime 比如: 2008-09-15T15:53:00+05:00 \n
    - end_time: 一个 Python datetime.datetime \n
    - process_after: 一个 Python datetime.timedelta, 总秒数 \n
    - repeat_time: 一个 Python datetime.time 比如: 14:23:55.003 \n
    """
    start_process = start_time + process_after
    duration = end_time - start_process
    return {
        "uuid": uuid,
        "start_time": start_time,
        "end_time": end_time,
        "process_after": process_after,
        "repeat_time": repeat_time,
        "duration": duration,
        "start_process": start_process,
    }

class ExtractDataModel(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    tags: frozenset[int] | None = None

@router3.post("/extractDataType/{{id}}", name="decimal类型")
async def create_schema(id: int,
                        item: Annotated[ExtractDataModel,
                            Body( examples=[{
                                "name": "decimal",
                                "description":"额外的数据类型",
                                "price": Decimal("109"),
                                "tags": [1,2,2,3]
                                }]
                            )
                        ]):
    result = {"id": id, "item": item}
    return result