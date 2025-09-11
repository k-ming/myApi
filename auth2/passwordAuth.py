from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status

auth_schema = OAuth2PasswordBearer(tokenUrl="/auth/token") # 指定客户端用户名密码登录的路径

password_router = APIRouter(
    tags=["用户名密码认证"],
    prefix="/auth",
)

# 收到客户端的username和password，返回token

@password_router.get("/oauth2_password_bearer", summary="返回当前用户的token")
def oauth2_password_bearer(token: str = Depends(auth_schema)):
    return {"token": token}

""" 基于password 和 bearer token 的 Oauth2 认证 """
""" 模拟数据库用户 """
fake_users_db = {
    "john sonw":{
        "username": "john sonw",
        "full_name": "john sonw",
        "email": "jsonsonw@example.com",
        "hashed_password": "fakehashedsecret",  # 模拟hash加密后的密码
        "is_active": True,  # 是否活跃用户
    },
    "alice":{
        "username": "alice",
        "full_name": "alice",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "is_active": False,
    }
}
# 定义基础user模型
class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


# 定义写入数据库包含密码的模型userindb

class UserInDB(User):
    hashed_password: str

""" 定义基础方法 """

# 模拟密码hash加密
def fake_hash_password(password: str) -> str:
    return "fakehashed" + password

# 获取用户
def get_user(db: fake_users_db, username: str) -> UserInDB:
    if username in db:
        return UserInDB(**db[username])
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

# 模拟解析token, 注意这里的token就是用户名username，所以可以直接调用 get_user方法获取【
def fake_decode_token(token: str) -> UserInDB:
    user = get_user(fake_users_db, token)
    return user

# 获取当前用户， 需要依赖auth_schema返回的token
def get_current_user(token: str = Depends(auth_schema)) -> User:
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, # OAuth的标记，非强制
        )
    else:
        return user

# 获取活跃的用户
def get_active_user(token: str = Depends(auth_schema)) -> User:
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect username or password")
    else:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
        return user

# 获取token接口
@password_router.post("/token", summary="用户名密码登录")
def get_token(form_data: OAuth2PasswordRequestForm =Depends()):
    if form_data.username in fake_users_db:
        user = UserInDB(**fake_users_db[form_data.username])
        hashed_password = fake_hash_password(form_data.password)
        if not hashed_password == user.hashed_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect username or password") # 密码不正确
        else:
            return {"access_token": user.username, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect username or password") # 用户名不存在

@password_router.get("/users/me", summary="获取活跃用户")
def read_users_me(current_user: User = Depends(get_active_user)):
    return  current_user