import re
import json
import time
import hashlib
from random import random

from tornado.options import options
import tornado.web

from core.models import read_write_database, Session


_int_pattern = re.compile('^-?[0-9]+$')
_float_pattern = re.compile('^-?[0-9]+(\.[0-9]+)?$')


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, db=None):
        #
        # https://www.tornadoweb.org/en/stable/web.html
        #
        # class tornado.web.RequestHandler(...)
        # subclasses should not override __init__ (override initialize instead)
        #
        self.db = db if db else read_write_database()
        self.__session_data = None

    def data_received(self, chunk):
        pass

    def on_finish(self):
        self.db.close()

    def get_str_argument(self, name, default='', strip=True):
        value = self.get_argument(name, default=default, strip=strip)
        return value if value else default

    def get_int_argument(self, name, default=0):
        raw_value = self.get_argument(name, '', strip=True)
        return int(raw_value) if _int_pattern.match(raw_value) else default

    def get_float_argument(self, name, default=0.0):
        raw_value = self.get_argument(name, '', strip=True)
        return float(raw_value) if _float_pattern.match(raw_value) else default

    def get_json_argument(self, name, default=None):
        raw_value = self.get_argument(name, None, strip=True)
        return json.loads(raw_value) if raw_value else default

    def generate_session(self, user_id, session_data):
        timestamp = hex(int(time.time()))[2:]
        for retry_times in range(3):
            session_id = hashlib.md5(str(user_id).encode('utf-8')).hexdigest()
            session_id = hashlib.md5('{1}{0}'.format(session_id, random()).encode('utf-8')).hexdigest()
            session_id = hashlib.md5('{0}{1}'.format(session_id, random()).encode('utf-8')).hexdigest()
            session_id = '{0}{1}{2}'.format(timestamp, session_id[len(timestamp):len(session_id) - 1], retry_times)
            session = Session.add(self.db, session_id, session_data)
            if session:
                return session_id, session.expireTime
        return None, None

    def get_session(self, key):
        if not self.session_id:
            return None
        return self.session_data[key] if key in self.session_data else None

    def set_session(self, key, value):
        if not self.session_id:
            return
        self.session_data[key] = value
        Session.update(self.db, self.session_id, self.session_data)

    @property
    def session_data(self):
        if not self.session_id:
            return None
        if self.__session_data is None:
            session = Session.find_by_session_id(self.db, self.session_id)
            self.__session_data = json.loads(session.data) if session else dict()
        return self.__session_data

    def invalidate_session(self):
        if not self.session_id:
            return
        Session.expire_by_session_id(self.db, self.session_id)

    @property
    def session_id(self):
        raise NotImplementedError

    def on_login_required(self):
        raise NotImplementedError


class PageHandler(BaseHandler):
    @property
    def session_id(self):
        return self.get_cookie('sessionId')

    def on_login_required(self):
        self.redirect(options.login_url)


class ApiHandler(BaseHandler):
    @property
    def session_id(self):
        return self.get_str_argument('sessionId')

    def on_login_required(self):
        self.set_status(401)
        self.finish('请登录'.encode('utf-8'))

    def api_succeeded(self, result=None):
        if result is None:
            self.finish()
        else:
            self.finish(json.dumps(result, separators=(',', ':')).encode('utf-8'))

    def api_failed(self, message=''):
        self.set_status(400)
        self.finish(message.encode('utf-8'))


class InvalidUrlHandler(BaseHandler):
    def head(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def get(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def post(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def delete(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def patch(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def put(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)

    def options(self, *args, **kwargs):
        raise tornado.web.HTTPError(404)
