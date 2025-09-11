from datetime import timedelta, datetime
from typing import Optional
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status
from .passwordAuth import fake_users_db, User, UserInDB

jwtToken_router = APIRouter(
    tags=["jwtToken认证"],
    prefix="/auth",
)
# 生成key 命令 openssl rand -hex 32
SECRET_KEY = "78a16f701fc5eda770d95a615804184e37129b0f9b6879a889bf7b4f6359a5e3"
EXPIRED_TIMEDELTA = 30


""" 基于jwt token 的 Oauth2 认证 """
""" 模拟数据库用户, 更新用户hash密码 """
fake_users_db.update({
    "john sonw":{
        "username": "john sonw",
        "full_name": "john sonw",
        "email": "jsonsonw@example.com",
        "hashed_password": "$2b$12$c0hWVUwaIKNj9ZgZ0jE6HOd1wYZP336am1dQz6YrQAPIYVH1mIHde",  # 可以调用 get_password_hash 方法获取
        "is_active": True,  # 是否活跃用户
    },
    "alice":{
        "username": "alice",
        "full_name": "alice",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$K.SM0ROczdZ3JIYduHnX5emygoYCvDTUj8J6DmVEOkss3Qu2rq3ki",
        "is_active": False,
    }
})

# 定义jwtToken返回模型
class Token(BaseModel):
    access_token: str
    token_type: Optional[str] = "bearer"

# password 校验
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 收到客户端的username和password，返回token
auth_schema = OAuth2PasswordBearer(tokenUrl="/auth/jwt/token") # 指定客户端用户名密码登录的路径


""" 定义基础方法 """
# 生成hash
def get_password_hash(password):
    return pwd_context.hash(password)

# 校验hash密码
def verify_password(plan_password: str, hashed_password: str):
    return pwd_context.verify(plan_password, hashed_password)

# 获取用户
def jwt_get_user(db:fake_users_db, username: str):
    if username in db:
        return UserInDB(**db[username])
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid user")

# 校验用户名和密码,返回bool值和user模型
def jwt_authenticate_user(db:fake_users_db, username: str, password: str):
    user = jwt_get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 生成access_toke
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm="HS256",)
    return encoded_jwt

# 登录成功返回token
@jwtToken_router.post("/jwt/token", summary="登录成功获取token", response_model=Token)
async def login_for_jwt_token(form_data: OAuth2PasswordRequestForm = Depends())-> dict:
    user = jwt_authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    expire = timedelta(minutes=EXPIRED_TIMEDELTA)
    access_token = create_access_token({"sub": user.username}, expires_delta=expire)
    return {"access_token": access_token, "token_type": "bearer"}

# 获取当前用户, 解析token
async  def jwt_get_current_user(token: str = Depends(auth_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    user = jwt_get_user(fake_users_db, username)
    if not user:
        raise credentials_exception
    return user


# 获取活跃的用户
async def jwt_get_current_active_user(current_user: User =Depends(jwt_get_current_user)):
    if current_user.is_active:
        return current_user
    raise  HTTPException(status_code=400, detail="Inactive user")


@jwtToken_router.get("/jwt/user/me", summary="获取当前用户", response_model=User)
async def read_users_me(current_user: User = Depends(jwt_get_current_user)):
    return current_user

@jwtToken_router.post("/jwt/user/active", response_model=User, summary="获取活跃的用户")
async  def read_users_active(active_user: User = Depends(jwt_get_current_active_user)):
    return active_user


#
# if __name__ == "__main__":
#     hash_result = get_password_hash("secret2")
#     print(hash_result)