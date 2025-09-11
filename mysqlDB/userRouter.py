from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import APIRouter, Query
from .db_init import create_db_and_tables, SessionDep
from .model import UserPub, User, UserCreate, UserUpdate
from fastapi.exceptions import HTTPException
from sqlmodel import select

@asynccontextmanager
async def lifespan(app:APIRouter):
    create_db_and_tables()
    yield

router = APIRouter(
    prefix="/users",
    tags=["mysql数据库"],
    lifespan=lifespan
)


@router.post("/user/", tags=["users"], response_model=UserPub)
def create_user(user: UserCreate, session: SessionDep) -> User:
    """
    response_model=UserPub 用于返回给客户端数据模型，会隐藏secret_name字段
    user: UserCreate 创建数据模型，拥有name,age,secret_name字段
    :param user: 用户model
    :param session: 获取数据库回话
    :return: 用户model
    """
    db_user = User.model_validate(user)
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except Exception as e: # 增加try, 捕获丢失链接异常，重试
        if 'Lost connection ' in str(e):
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user
        raise e



@router.get("/users/", tags=["users"], response_model=list[UserPub])
async def read_users(session: SessionDep, offset=0, limit: Annotated[int, Query(le=100)] = 100, ) -> list[UserPub]:
    """
    response_model=list[UserPub] 返回值隐藏了secret_name
    :param session:
    :param offset:
    :param limit:
    :return:
    """
    user_list = session.exec(select(User).offset(offset).limit(limit)).all()
    return user_list


@router.get("/users/{user_id}", tags=["users"], response_model=UserPub)
async def read_user(user_id: int, session: SessionDep) -> UserPub:
    """
    查询单个用户
    :param user_id:
    :param session:
    :return:
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", tags=["users"], response_model=UserPub)
def update_user(user_id: int, user: UserUpdate, session: SessionDep) -> UserPub:
    """
    更新单个用户
    :param user_id:
    :param user:
    :param session:
    :return:
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@router.delete("/users/{user_id}", tags=["users"])
def delete_user(user_id: int, session: SessionDep):
    """
    删除单个用户, 无响应model
    :param user_id:
    :param session:
    :return:
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user_db)
    session.commit()
    return {"ok": True}
