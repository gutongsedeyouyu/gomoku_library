import math
import json
from datetime import datetime

from tornado.options import options
from sqlalchemy import create_engine, Column, BigInteger, DateTime, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker


_engine = create_engine('mysql+pymysql://{3}:{4}@{0}:{1}/{2}?charset=utf8mb4'
                        .format(options.mysql_host, options.mysql_port, options.mysql_database,
                                options.mysql_user, options.mysql_password),
                        echo=options.debug)
_read_write_database = sessionmaker(bind=_engine)()
BaseModel = declarative_base()


def read_write_database():
    return _read_write_database


def paginate(items, page_index, page_size):
    if not items:
        return items, 0, page_size
    total_count = len(items)
    page_count = max(math.ceil(total_count / page_size), 1)
    if page_index > page_count - 1 or page_index < 0:
        page_index = page_count - 1
    return items[page_size * page_index: page_size * page_index + page_size], page_index, page_count


class BaseModelMixin(object):
    id = Column('id', BigInteger, primary_key=True)
    createTime = Column('create_time', DateTime, index=True)
    updateTime = Column('update_time', DateTime, index=True)

    @declared_attr
    def __tablename__(cls):
        trans = str.maketrans({c: f'_{chr(c).lower()}' for c in range(65, 91)})
        return cls.__name__.translate(trans).strip('_')


class Session(BaseModel, BaseModelMixin):
    sessionId = Column('session_id', String(32), unique=True)
    data = Column('data', String(10000))
    expireTime = Column('expire_time', DateTime)

    @staticmethod
    def add(db, session_id, session_data):
        if db.query(Session).filter(Session.sessionId == session_id).first():
            return None
        data = json.dumps(session_data, separators=(',', ':'))
        now = datetime.now()
        expire_time = datetime.utcfromtimestamp(now.timestamp() + options.session_expire_after)
        session = Session()
        session.createTime = now
        session.updateTime = now
        session.sessionId = session_id
        session.data = data
        session.expireTime = expire_time
        db.add(session)
        db.commit()
        return session

    @staticmethod
    def update(db, session_id, session_data):
        session = Session.find_by_session_id(db, session_id)
        session.updateTime = datetime.now()
        session.data = json.dumps(session_data, separators=(',', ':'))
        db.merge(session)
        db.commit()
        return session

    @staticmethod
    def find_by_session_id(db, session_id):
        return db.query(Session).filter(Session.sessionId == session_id, Session.expireTime > datetime.now()).first()

    @staticmethod
    def expire_by_session_id(db, session_id):
        db.query(Session).filter(Session.sessionId == session_id).delete()
        db.commit()
