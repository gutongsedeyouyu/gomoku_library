from datetime import datetime
import hashlib

from sqlalchemy import Column, Table, ForeignKey, BigInteger, String
from sqlalchemy.orm import relationship

from core.models import BaseModel, BaseModelMixin


x_user_permission = Table('x_user_permission',
                          BaseModel.metadata,
                          Column('user_id', BigInteger, ForeignKey('user.id')),
                          Column('permission_id', BigInteger, ForeignKey('permission.id')))


class User(BaseModel, BaseModelMixin):
    userName = Column('user_name', String(20), unique=True)
    password = Column('password', String(32))
    permissions = relationship('Permission', secondary=x_user_permission, back_populates='users')

    @staticmethod
    def add(db, user_name, password):
        now = datetime.fromtimestamp(int(datetime.now().timestamp()))
        password = User.__safe_password(password, now)
        user = User()
        user.createTime = now
        user.updateTime = now
        user.userName = user_name
        user.password = password
        db.add(user)
        db.commit()
        return user

    @staticmethod
    def auth_by_password(db, user_name, password):
        user = db.query(User).filter(User.userName == user_name).one()
        if not user or user.password != User.__safe_password(password, user.createTime):
            return None
        return user

    @staticmethod
    def change_password(db, user_name, new_password):
        user = db.query(User).filter(User.userName == user_name).one()
        user.updateTime = datetime.now()
        user.password = User.__safe_password(new_password, user.createTime)
        db.merge(user)
        db.commit()
        return user

    @staticmethod
    def __safe_password(password, create_time):
        password = hashlib.md5(password.encode('utf-8')).hexdigest()
        password = hashlib.md5('{1}{0}'.format(password, int(create_time.timestamp())).encode('utf-8')).hexdigest()
        password = hashlib.md5('{0}{1}'.format(password, int(create_time.timestamp())).encode('utf-8')).hexdigest()
        return password


class Permission(BaseModel, BaseModelMixin):
    name = Column('name', String(10), unique=True)
    users = relationship('User', secondary=x_user_permission, back_populates='permissions')

    @staticmethod
    def add(db, name):
        now = datetime.now()
        permission = Permission()
        permission.createTime = now
        permission.updateTime = now
        permission.name = name
        db.add(permission)
        db.commit()
        return permission

    @staticmethod
    def find_by_name(db, name):
        return db.query(Permission).filter(Permission.name == name).one()
