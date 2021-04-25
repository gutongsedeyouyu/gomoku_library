"""create database {db_name} character set utf8mb4 collate utf8mb4_0900_ai_ci;
"""
from datetime import datetime

import config
from core.models import _engine, BaseModel, Session, read_write_database, paginate
from account.models import User, Permission
from library.models import Library, HotKeyword


BaseModel.metadata.create_all(_engine)
db = read_write_database()
