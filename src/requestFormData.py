from fastapi import APIRouter, Form
from typing import Annotated
from pydantic import BaseModel

router = APIRouter()

class FormData(BaseModel):
    username: str
    password: str
    model_config = {'extra':'forbid'} # 禁止额外的字段数据

class ResponseForm(BaseModel):
    username: str # 响应结果只返回隐藏密码

@router.post("/login", response_model=ResponseForm)
def login(data: Annotated[FormData, Form()]):
    return data