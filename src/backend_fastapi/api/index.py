from fastapi import APIRouter
from .websocket_route.index import websocket_endpoint
from .route.index import api_router



# 创建一个新的路由对象
router = APIRouter()
router.add_api_websocket_route("/ws", websocket_endpoint)
router.include_router(api_router, prefix="/v1")