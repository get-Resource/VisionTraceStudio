from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table,Boolean,JSON
from sqlalchemy.orm import relationship
from .base import Base



class TaskAnnotation(Base):
    __tablename__ = 'task_annotations'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    file_id = Column(Integer, ForeignKey('files.id'))
    annotated = Column(Boolean, default=False, doc="是否已标注")
    reviewed = Column(Boolean, default=False, doc="是否已审核")
    annotation_data = Column(JSON, doc="注释数据")
    # 添加任务注释信息的关联
    task = relationship("Task", back_populates="annotations")
    file = relationship("File", back_populates="annotations")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, doc="任务名称")
    description = Column(Text, doc="任务说明")
    priority = Column(Enum('Low', 'Medium', 'High',name="priority_enum"), index=True, doc="优先级")
    dataset_id = Column(Integer, ForeignKey('datasets.id'), doc="数据集ID")
    dataset = relationship("Dataset", back_populates="tasks")
    status = Column(Enum('Started', 'Annotated', 'Reviewed', 'Delivered',name="status_enum"), index=True, doc="任务状态")
    projects = relationship("Project", secondary="task_project", back_populates="tasks")

    # 如果 Task 类具有 annotations 属性，需要在映射中关联到相应的数据库列或关系
    annotations = relationship("TaskAnnotation", back_populates="task")  # 假设有一个名为 Annotation 的映射类

    tags = relationship("Tag", back_populates="tasks")
    # 是任务进度的计算方法
    @property
    def progress(self):
        if not self.dataset:
            return 0
        annotated_files_count = sum(1 for file in self.dataset.files if file.annotations.annotated)
        total_files_count = len(self.dataset.files)
        return annotated_files_count / total_files_count if total_files_count > 0 else 0
    

task_project = Table(
    'task_project', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, doc="项目名称")

    tags = relationship("Tag", back_populates="project")
    tasks = relationship("Task", secondary="task_project", back_populates="projects")

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, doc="标签名称")
    color = Column(String, index=True, doc="颜色")
    hotkey = Column(String, doc="标签快捷键")

    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="tags")

    task_id = Column(Integer, ForeignKey('tasks.id'))
    tasks = relationship("Task", back_populates="tags")

class Dataset(Base):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True, doc="数据集ID")
    name = Column(String, index=True, doc="数据集名称")
    source = Column(String, index=True, doc="数据采集来源")
    data_type = Column(Enum('Image', 'Video', 'Audio',name="data_type_enum"), index=True, doc="数据类型")
    description = Column(Text, doc="数据说明")
    created_at = Column(DateTime, index=True, doc="新建时间")
    tasks = relationship("Task", back_populates="dataset")
    files = relationship("File", back_populates="dataset")

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(String, doc="文件路径")
    hash_value = Column(String, index=True, unique=True, doc="哈希值")

    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    dataset = relationship("Dataset", back_populates="files")
    # 添加与任务标注关联的属性
    annotations = relationship("TaskAnnotation", back_populates="file")
