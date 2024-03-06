from sqlalchemy.orm import Session
from db.crud.base import CRUDBase
from db.models.datasets import Dataset, File
from db.schemas.datasets import FileCreate, FileUpdate,DatasetCreate, DatasetUpdate
from typing import List, Type
from sqlalchemy.future import Engine


from sqlalchemy import create_engine, Column, String, MetaData, Table, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class DatasetCRUD(CRUDBase[Dataset, DatasetCreate, DatasetUpdate]):
    def __init__(self, model: Type[Dataset]):
        super().__init__(model)

    def get_by_dataset(
        self, db: Session, dataset_id: int = None, skip: int = 0, limit: int = 100
    ) -> List[File]:
        if dataset_id is None:
            return (
                db.query(self.model)
                # .offset(skip)
                # .limit(limit)
                .all()
            )
        
        return (
            db.query(self.model)
            .filter(self.model.id == dataset_id)
            # .offset(skip)
            # .limit(limit)
            .all()
        )
    
    # def create(self, db: Session, *, obj_in: DatasetCreate) -> Dataset:
    #     db_obj = Dataset(**obj_in)
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

dataset = DatasetCRUD(Dataset)

class FileCRUD(CRUDBase[File, FileCreate, FileUpdate]):
    def __init__(self, model: Type[File]):
        super().__init__(model)

    def get_by_dataset(
        self, db: Session, dataset_id: int, skip: int = 0, limit: int = 100
    ) -> List[File]:
        return (
            db.query(self.model)
            .filter(self.model.dataset_id == dataset_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    async def query_files_hash_value(
        self, db: Session, engine:Engine, file_data: list = [], 
    ) -> tuple[List[File],List[File]]:
        try:
            # 创建临时表
            connection = engine.connect()
            connection.execute("CREATE TEMP TABLE temp_table (id INT PRIMARY KEY, path VARCHAR(255), hash_value VARCHAR(255));")
            connection.execute("INSERT INTO temp_table (id, path,hash_value) VALUES (%(id)s, %(path)s, %(hash_value)s);", file_data)
            # 查询哈希值一致的文件，数据库中已经存在的文件
            hash_matched_files = connection.execute("""
SELECT temp_table.* FROM temp_table
LEFT JOIN files ON temp_table.hash_value = files.hash_value 
WHERE files.hash_value IS not NULL;""").fetchall()
            # 查询哈希值不一致的文件,也就是数据库中没有记录的文件
            hash_mismatched_files = connection.execute("""
SELECT temp_table.* FROM temp_table
LEFT JOIN files ON temp_table.hash_value = files.hash_value 
WHERE files.hash_value IS NULL;""").fetchall()
            connection.execute("DROP TABLE IF EXISTS temp_table;")
            connection.close()
            # 返回查询结果
            return hash_matched_files, hash_mismatched_files
        finally: pass
            # 删除临时表
        return hash_matched_files, hash_mismatched_files


file = FileCRUD(File)
