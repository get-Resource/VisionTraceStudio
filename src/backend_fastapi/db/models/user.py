from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

# 用户角色关联表
user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey('users.id')),
                   Column('role_id', Integer, ForeignKey('roles.id'))
                  )

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime)

    # 用户角色关系
    roles = relationship('Role', secondary=user_roles, backref='users')
