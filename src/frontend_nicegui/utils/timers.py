from datetime import datetime
from nicegui import app, ui,background_tasks
import asyncio
import json
import websockets
from core.config import settings



# 更新心跳函数
async def update_heartbeat():
    access_token = app.storage.user.get('access_token', None)
    if access_token is not None:
        try:
            async with websockets.connect(f"ws://{settings.API_URL}/api/ws", timeout=0.1) as websocket:  # 替换为你的 FastAPI WebSocket 服务器地址
                try:
                    heartbeat_data = {
                        "taskname": "heartbeat",
                        "message": "检查会话",
                        "data": {
                            "access_token": access_token,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    heartbeat_json = json.dumps(heartbeat_data)
                    await websocket.send(heartbeat_json)
                    result = await websocket.recv()
                    result_json = json.loads(result)
                    if result_json.get("code",-1)== 1:
                        app.storage.user["UserData"] = result_json.get("data")
                    else:
                        del app.storage.user["access_token"]
                    await asyncio.sleep(5)  # 每隔 5 秒发送一次心跳
                except TimeoutError:
                    pass
        except:
            pass
def init_timer():
    background_tasks.create(update_heartbeat())
    # update_heartbeat()
    # ui.timer(1.0, update_heartbeat)
