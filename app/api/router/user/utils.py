from typing import Any

from fastapi import APIRouter, Depends

from app.db import models, schemas
from src.backend_fastapi.api import deps
from app.core.celery_app import celery_app
# from app.utils.user_validator import send_test_email

router = APIRouter()
