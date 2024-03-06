from datetime import timedelta,datetime
import hashlib
import os
from pathlib import Path
import re
from typing import Any, Union
import zipfile
import aiofiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, File,Query, Request,UploadFile,Response
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
import pytz
from sqlalchemy.orm import Session
from sqlalchemy.future import Engine
from typing import Annotated
from db.schemas.datasets import DatasetCreate
from utils.utils import convertFileSize
from db import crud, models, schemas
from api import deps
from core import security
from core.config import settings
from core.security import get_password_hash
from utils.user_validator import (
    # send_reset_password_email,
    verify_password_reset_token,
)

datasets_router = APIRouter()

executor = ThreadPoolExecutor(max_workers=10)

async def process_upload(file: UploadFile,index,file_path ):
    # 模拟上传文件的处理过程

    async with aiofiles.open(file_path, "wb") as buffer:
        if isinstance(file,UploadFile):
            content = await file.read()
        else:
            content = file["zipfile"].read(file["filename"])

        await buffer.write(content)
        file_hash = hashlib.sha256(content).hexdigest()
    # logger.info(f"{file_path} 保存完成 ：{file_hash}")
    return {'id': index, 'path': file_path, 'hash_value': file_hash}

@datasets_router.post("/upload_files")
async def upload_files(
    # request: Request,
    # response: Response,
    token: str = Body(...),
    data_nmae: str = Body(...),
    data_source: str = Body(...),
    data_type: str = Body(...),
    data_description: str = Body(...),
    is_client_file: bool = Body(...),
    start_time: datetime = Body(...),
    files: list[UploadFile] = File(
        title="文件",
        description="可以多个图像或视频类型文件; 记录打包成一个zip上传,目前只支持 jpg和mp4",
    ),
    db: Session = Depends(deps.get_db),
    engine:Engine = Depends(deps.get_engine),
) -> Any:
    """
    
    """
    username = verify_password_reset_token(token) # 检查用户权限等
    # 待补充检查用户权限等
    start_time = start_time.astimezone(pytz.timezone('Asia/Shanghai')).replace(tzinfo=None)
    up_duration = (datetime.now() - start_time).total_seconds()  # 完成数据接受时间
    file_size_bytes = sum([file.size for file in files])  # 全部文件总大小
    file_size, unit = convertFileSize(int(file_size_bytes))
    internet_speed_bytes = file_size_bytes / up_duration
    internet_speed, internet_speed_unit = convertFileSize(internet_speed_bytes)
    logger.info(f"耗时 {'{:.2f}'.format(up_duration)} 秒成功接收到{len(files)}个文件总大小{'{:.2f} {}'.format(file_size, unit)},"
                f"接收速率为{'{:.2f} {}'.format(internet_speed, internet_speed_unit)}/s ")
    pat2 = re.compile(r"[*?:\"<>/|\\]")
    upload_time = datetime.now()  # 转为iso 格式字符串
    upload_time_iso = pat2.sub("-", upload_time.isoformat())  # 转为iso 格式字符串
    storage_dir = os.path.join(settings.LOCAL_STORAGE_DIRECTORY, data_nmae, upload_time_iso)  # 文件保存目录
    try:
        os.makedirs(storage_dir,exist_ok=True)
    except:
        logger.exception(f"{storage_dir} 目录创建失败")
        return dict(code=-1,message=f"目录不可以创建，请检查数据名称是否存在异常字符导致不能创建")
    try:
        client_file_ = "客户端" if is_client_file else "共享目录"
        logger.info(f"开始处理上传的文件，文件从 {client_file_} 上传")
        if is_client_file and len(files) > 0: # 客户端上传的文件
            async def upload_file(file,index,file_path):
                # loop = asyncio.get_event_loop()  # 获取当前线程的事件循环
                return await process_upload(file, index, file_path)
                # return await loop.run_in_executor(executor, process_upload, file,index,file_path)  # 在线程池中执行上传文件的处理
            
            if files[0].filename.endswith(".zip"):
                zf = zipfile.ZipFile(files[0].file)
                results = await asyncio.gather(*[upload_file({"zipfile":zf,"filename":filename},index,os.path.join(storage_dir, os.path.basename(filename))) for index,filename in enumerate(zf.namelist()) if not filename.endswith("/")])
            else:
                # 并行执行多个上传文件的异步任务，并等待它们全部完成
                results = await asyncio.gather(*[upload_file(file,index,os.path.join(storage_dir, file.filename)) for index,file in enumerate(files)])
            logger.info("正在保存到数据库", )
            hash_matched_files, hash_mismatched_files = await crud.file.query_files_hash_value(db,engine,results)
            # logger.info("数据库上具有重复文件", hash_matched_files)
            if len(hash_mismatched_files) > 0:
                logger.info(f"开始保存新数据：{hash_mismatched_files}")
                datasets = DatasetCreate(name=data_nmae,data_type=data_type.capitalize(),description=data_description,source=data_source)
                datasets = crud.dataset.create(db,obj_in=datasets)
                
                hash_mismatched_files = [dict(path=row[1],hash_value=row[2],dataset_id=datasets.id) for row in hash_mismatched_files]
                # connection = db.connection()
                db.execute(models.datasets.File.__table__.insert(),hash_mismatched_files)
                db.commit()
            if len(hash_matched_files) > 0:
                logger.info(f"清理删除 {len(hash_matched_files)} 个重复数据")
                for file_info in hash_matched_files:
                    try:
                        filename = file_info[1]

                        if os.path.exists(filename):
                            os.remove(filename)
                    except: pass
                directory_path = Path(hash_matched_files[0]).parent
                if len(os.listdir(str(directory_path))) == 0:
                    os.rmdir(str(directory_path))
                    directory_path.rmdir()

                
            # async with aiofiles.open(upload_file_name, "wb") as buffer:
            #     await buffer.write(await file.read())
        else: # 通过共享文件夹上传的文件，直接读取文件路径保存到数据库
            pass

    except Exception as e:
        logger.exception(f"数据存储操作异常")
        return dict(code=-1,message=f"图片数据保存异常：{e}")

@datasets_router.get("/get_datasets/")
def get_datasets(
    db: Session = Depends(deps.get_db), 
    page: int = Query(default=1), page_size: int = Query(default=10),datasetid: Union[int,None] = Query(default=10),
    name: Union[str,None] = Query(default=None), source: Union[str,None] = Query(default=None),
    data_type: Union[str,None] = Query(default=None), description: Union[str,None] = Query(default=None),
    created_at: Union[list,None] = Query(default=None), 
    ):
    # 计算起始索引位置
    start_index = (page - 1) * page_size
    datasets = crud.dataset.get_by_dataset(db,skip=start_index,limit=page_size)
    for dataset in datasets:
        dataset.files = dataset.files[:3]
    return datasets

@datasets_router.post("/get_dataset/{dataset_id}")
def get_dataset(dataset_id):
    pass