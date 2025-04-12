from fastapi import APIRouter, Form
from pydantic import BaseModel
from typing import Annotated

router = APIRouter()


class UserForm(BaseModel):
    name: str
    password: str


class UserPub(BaseModel):
    name: str


@router.post("/login", response_model=UserPub)
def login(data: Annotated[UserForm, Form()]):
    return data