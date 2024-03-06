import time
from fastapi import FastAPI, WebSocket

from api.deps import get_current_token_user

# 定义 WebSocket 路由处理函数
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket connection endpoint.

    Args:
    - websocket: WebSocket connection

    Returns:
    - 200: Successful WebSocket connection
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            send_data = dict(taskname=data.get("taskname"),code=1,message="执行成功",data={})
            user = get_current_token_user(token = data.get("data").get("access_token"))
            if user:
                send_data["data"].update(user)
            await websocket.send_json(send_data)
    except Exception as e:
        print(e)

# 创建 WebSocket 路由对象

# 将 WebSocket 路由挂载到应用中
# app.router.routes.append(websocket_route)
