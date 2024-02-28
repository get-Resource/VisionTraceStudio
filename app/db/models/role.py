from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from .base import Base
# 用户权限关联表
role_permissions = Table('role_permissions', Base.metadata,
                         Column('role_id', Integer, ForeignKey('roles.id')),
                         Column('permission_id', Integer, ForeignKey('permissions.id'))
                        )

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # 角色权限关系
    permissions = relationship('Permission', secondary=role_permissions, backref='roles')
