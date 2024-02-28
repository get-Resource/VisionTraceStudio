import copy
from copy import _deepcopy_dict as copy_deepcopy_dict
from functools import lru_cache
import os
import secrets
import sys
from typing import Any, Dict, List, Optional, Union
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from pydantic import AnyHttpUrl, ConfigDict, Field, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings
from loguru import logger
# 修复复制问题
# def _deepcopy_dict(x, memo, deepcopy=copy.deepcopy):
#     y = {}
#     memo[id(x)] = y
#     # from icecream import ic
#     for key, value in x.items():
#         # y[deepcopy(key, memo)] = deepcopy(value, memo)
#         if key not in ['_fork_lock', '_lock']:
#             y[deepcopy(key, memo)] = deepcopy(value, memo)
#     return y
# copy._deepcopy_dict = _deepcopy_dict
# copy_deepcopy_dict = _deepcopy_dict
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "secrets.token_urlsafe(32)" # 开发阶段建议是由固定值，随机的URL安全文本字符串
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 令牌有效文件
    SERVER_NAME: str = 'Vision Trace Studio'
    SERVER_HOST: Union[AnyHttpUrl,None] = None
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    # 自定义 BACKEND_CORS_ORIGINS 验证读取
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # process_pool = ProcessPoolExecutor()
    # thread_pool = ThreadPoolExecutor()

    # 日志参数定义
    level: str = Field("DEBUG",title= """日志级别""")
    filename: str = Field("./logs/data_visualization",title= "服务从日志存储目录")
    rotation: str = Field("20 MB",title= '滚动记录的机制',
        description='分割日志条件;例如，"500 MB"、"0.5 GB"、"1 month 2 weeks"、"10h"、"monthly"、"18:00"、"sunday"、"monday at 18:00"、"06:15"',
    )
    retention: Union[int, str] = Field(7,title= '日志保留机制',
        description='日志保留条件;例如，周:1 week, 天:3 days, 月:2 months, 文件数量: 7',
    )
    log_format: str = Field("{time:YYYY-MM-DD HH:mm:ss,SSS} {process.name}: {thread.name} {file}.{module}.{function}[line:{line}] {level}: {message}",title= '日志格式',
    )
    PROJECT_NAME: str = "Data Preview"
    SENTRY_DSN: Optional[HttpUrl] = None
    # 自定义 SENTRY_DSN 验证读取
    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if v is None:
            return None
        if len(v) == 0:
            return None
        return v
    # Postgres 数据库参数
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI:  Union[Optional[PostgresDsn], Optional[str]] = None
    PGADMIN_LISTEN_PORT: str
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        Dsn = PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )
        print(Dsn,values)
        return Dsn


    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    # EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False
    model_config = ConfigDict(extra='forbid',env_file=".env")
    # class Config:
    #     case_sensitive = True
    #     env_file = ".env" 
    #     extra = "forbid"



@lru_cache
def get_settings():
    setting = Settings()
    os.makedirs(os.path.dirname(setting.filename), exist_ok=True)
    logger.remove()
    logger.add(setting.filename, format=setting.log_format,level=setting.level, 
            rotation=setting.rotation, retention=setting.retention, 
            diagnose=True, # 异常跟踪是否应显示变量值以简化调试
            colorize=False, enqueue=True # 多进程安全队列，这在通过多个进程记录到文件时很有用
    )
    logger.add(sys.stderr, format=setting.log_format,level=setting.level, 
            colorize=True, 
    )
    return setting

settings = get_settings()