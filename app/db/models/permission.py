from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from .base import Base


    
class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
