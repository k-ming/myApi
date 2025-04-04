from dataclasses import Field

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime, timedelta, timezone, time, date
from uuid import UUID

router = APIRouter()


class Schema(BaseModel):
    """
    额外的请求体参数, 指定示例schema
    """
    name: str = Field(examples=['Field 提供的参数说明'])
    description: str | None = Field(examples=['Field 提供的参数说明'])
    model_config = {  # schema 可以直接填充在请求体中
        "json_schema_extra": {
            "example": {
                "name": "polly",
                "description": "a pretty dog",
            }
        }
    }


@router.put("/schema/{sch_id}")
async def update_schema(
        sch_id: int,
        schema: Annotated[
            Schema,
            Body(examples=[
                {"name": "tiky",
                 "description": "a pretty cat", }
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


@router.post("/schema")
async def create_schema(
        uuid: Annotated[UUID, Body(examples=["550e8400-e29b-41d4-a716-446655440000"])],
        start_time: Annotated[datetime, Body()],
        end_time: Annotated[datetime, Body()],
        process_after: Annotated[timedelta, Body()],
        repeat_time: Annotated[time | None, Body()] = None,
) -> dict:
    """
    :额外的数据类型
    :param uuid: "通用唯一标识符" ，在许多数据库和系统中用作ID \n
    :param start_time: 一个 Python datetime.datetime 比如: 2008-09-15T15:53:00+05:00 \n
    :param end_time: 一个 Python datetime.datetime \n
    :param process_after: 一个 Python datetime.timedelta, 总秒数 \n
    :param repeat_time: 一个 Python datetime.time 比如: 14:23:55.003 \n
    :return: dict
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