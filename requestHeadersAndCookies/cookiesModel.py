from typing import Optional
from fastapi import APIRouter, Cookie
from pydantic import BaseModel

router2 = APIRouter(
    prefix="/cookies",
    tags=["cookie参数和模型"]
)

class CookieModel(BaseModel):
    domain: str
    name: str | None = None
    model_config = {"extra": "forbid"}


@router2.get("/cookie", name="cookie参数")
def get_cookie(Adid: Optional[str] = Cookie(None, alias="Adid")):
    return Adid

@router2.post("/create_cookie", name="cookie参数模型")
def create_cookie(my_cookie: CookieModel = Cookie()):
    return my_cookie