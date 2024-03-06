from fastapi import FastAPI
from component.routers.router_component import Router
from views.datasets import datasets_ui
from views.task import tasks_ui
from utils.timers import init_timer
from views import index
from middleware.auth import app

from nicegui import ui
from core.config import settings
from views.login import show_login_form
from nicegui import Client, ui,context,app
from pathlib import Path
import store.action as action

# ui.button.default_props('rounded outline') 
# ui.label.default_classes('bg-blue-100 p-2')
# ui.label.default_style('color: tomato')

def init() -> None:
    
    action.service_client(app,f"http://{settings.API_URL}",)
    ui.image(Path("resources/background.webp")).style('width: 98%; height: 98%; object-fit: cover; opacity: 1; position: absolute;')

    @ui.page('/login')
    def view_logs(): show_login_form()

    @ui.page('/',title="")  # normal index page (e.g. the entry point of the app)
    @ui.page('/{path:path}',title="",favicon="")  # all other pages will be handled by the router but must be registered to also show the SPA index page
    async def main(path: str = "",client: Client = None):
        init_timer()
        router = Router()
        router.add('/',index,"主页")
        router.add('/datasets',datasets_ui,"数据集","dataset")
        # router.add('/datasets',datasets_ui,"数据集","dataset")
        router.add('/tasks',tasks_ui,"任务","task")
        router.frame().classes('w-full p-4 bg-gray-100')

    ui.run(
        port = settings.FRONTEND_PORT,
        uvicorn_reload_dirs="./",
        uvicorn_reload_includes="./*.py",
        # native=True,
        # window_size=(700,500),
        storage_secret=settings.SECRET_KEY
    )

if __name__ in {"__main__", "__mp_main__"}:
    init()