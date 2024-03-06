from datetime import datetime
from pydantic import BaseModel,Field
from typing import Optional


# 数据集模型
class DatasetBase(BaseModel):
    name: str
    source: str
    data_type: str
    description: Optional[str] = None


class DatasetCreate(DatasetBase):
    pass
    created_at: Optional[datetime] = Field(datetime.now())


class DatasetUpdate(DatasetBase):
    pass


class DatasetInDBBase(DatasetBase):
    id: int

    class Config:
        orm_mode = True


# 数据集在数据库中的模型（带有ORM模式）
class Dataset(DatasetInDBBase):
    pass


# 文件模型
class FileBase(BaseModel):
    path: str
    hash_value: str


class FileCreate(FileBase):
    dataset_id: int


class FileUpdate(FileBase):
    pass


class FileInDBBase(FileBase):
    id: int
    dataset_id: int

    class Config:
        orm_mode = True


# 文件在数据库中的模型（带有ORM模式）
class File(FileInDBBase):
    pass
