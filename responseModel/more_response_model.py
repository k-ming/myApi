import hashlib
from typing import Union

from fastapi import APIRouter, Form, status
from pydantic import BaseModel


router2 = APIRouter(
    prefix="/MoreModel",
    tags=["多个模型和模型的继承"]
)


class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

class UserPassword(UserBase):
    password: str

class UserOut(UserBase):
    pass

class UserOut1(UserBase):
    msg: str | None = "user info saved successfully!"

class UserInDb(UserBase):
    hashed_password: str

def fake_password_hash(password):
    return hashlib.sha512(password.encode("UTF-8")).hexdigest()

def fake_save_user(user:UserPassword):
    password_hashed = fake_password_hash(user.password)
    # 此处先把 UserPassword 转成json user.model_dump(), 然后再对其解包，传入UserInDb ，相当于 UserInDb 拥有了username、email、full_name、hashed_password 字段
    user_in_db = UserInDb(**user.model_dump(), hashed_password =password_hashed)
    print("user info saved  !")
    return user_in_db

@router2.post("/create_user", response_model=UserOut, name="多个模型和模型的继承")
def create_user(user: UserPassword = Form()):
    return fake_save_user(user)

@router2.post("/register_user", response_model=Union[UserOut, UserOut1] , name="联合响应模型")
def create_user(user: UserPassword = Form()):
    saved = fake_save_user(user).model_dump()
    saved.update(dict(msg="user info saved successfully!"))
    return saved

@router2.post("/get_user", response_model=dict[str, str | None], name="响应模型定义为字典")
async def get_user(user: UserPassword = Form()):
    return {"username": user.username, "email": user.email, "full_name": user.full_name}

@router2.post("/create", name="响应状态码", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create(user: UserPassword = Form()):
    saved = fake_save_user(user).model_dump()
    return saved