from nicegui import ui
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from fastapi import Request
from starlette.datastructures import UploadFile

from nicegui.events import UiEventArguments, UploadEventArguments, handle_event
from nicegui.nicegui import app
from uuid import uuid4
from nicegui import events, ui


def on_upload(e,page_id):
    ui.notify(f'Uploaded {page_id}:{e}')

def index() -> None:
    ui.label('Hello, FastAPI!')
    page_id = uuid4()
    # upload.props('''accept=".jpg, image/*, video/*"''')

    