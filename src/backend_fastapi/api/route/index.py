from fastapi import APIRouter
from .users import auth
from . import datasets
api_router = APIRouter()

api_router.include_router(auth.auth_router, prefix="/auth",tags = ["登录认证"])


api_router.include_router(datasets.datasets_router, prefix="/datasets",tags = ["登录认证"])