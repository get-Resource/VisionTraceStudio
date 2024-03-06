
from nicegui import ui
from ..core.config import settings



def gui_run():
    ui.run(
        port = settings.SERVICE_PORT,
        uvicorn_reload_dirs="../",
        uvicorn_reload_includes="../*.py",
        # native=True,
        # window_size=(700,500),
        storage_secret=settings.SECRET_KEY
    )