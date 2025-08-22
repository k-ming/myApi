from fastapi import APIRouter, Form
from typing import Annotated, Union
from pydantic import BaseModel

router2 = APIRouter(
    prefix="/formData",
    tags=["表单数据和表单模型"]
)

class FormData(BaseModel):
    username: str
    password: str
    model_config = {'extra':'forbid'} # 禁止额外的字段数据

class ResponseForm(BaseModel):
    username: str # 响应结果只返回隐藏密码

@router2.post("/register", name="form表单")
async def register_form(name: Annotated[str, Form()], age: str = Form(), password: str = Form(), sex: Union[str, None] = None):
    return name, age

@router2.post("/login", name='form表单模型', response_model=ResponseForm)
def login(data: Annotated[FormData, Form()]):
    return data