import traceback
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from app.db.initial_data import init as initial_data
from .api.router import api_router
from .core.config import settings
from fastapi import Depends, HTTPException, status

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.exception_handler(Exception)
@app.exception_handler(HTTPException)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    捕获请求参数 验证错误
    :param request:
    :param exc:
    :return:
    """
    logger.exception(f"参数错误\nURL:{request.url}\nHeaders:{request.headers}")
    # print(traceback.format_exc())
    if  isinstance(exc,RequestValidationError):
        body = exc.body
        code = status.status_code
        errors = exc.errors()
        message = "参数不全或参数错误"
    else:
        body = exc.detail
        code = exc.status_code
        errors = traceback.format_exc()
        errors = body
        message = body
        print(message)
        
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({"code": code, "message": message,
                                  "data": {"tip": errors}, "body": body,
                                  }),
    )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
initial_data()