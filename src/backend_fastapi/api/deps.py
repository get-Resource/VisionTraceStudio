from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from db import crud, models, schemas
from core import security
from core.config import settings
from db.session import SessionLocal,engine
from loguru import logger
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_engine() -> Generator:
    try:
        yield engine
    finally:
        pass


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.user.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_token_user(token: str = "")-> models.user.User:
    user = {}
    db = next(get_db())
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
        logger.info(f"token 可用")
    except (jwt.JWTError, ValidationError):
        return None
    User = crud.user.get(db, id=token_data.sub)
    if user is not None:
        # users_dict = [{column.name: getattr(user, column.name) for column in User.__table__.columns} for user in users]
        user = dict(
            username=User.username,
            full_name=User.full_name,
            is_superuser=User.is_superuser,
            Authorization=[],
        )
        if User.is_superuser:
            user["Authorization"] = [

            ]
    return user
