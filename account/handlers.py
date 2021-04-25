from account.models import User
from core.handlers import ApiHandler, PageHandler


class LoginApiHandler(ApiHandler):
    def post(self, *args, **kwargs):
        user_name = self.get_str_argument('userName', '')
        password = self.get_str_argument('password', '')
        if not user_name or not password:
            return self.api_failed('用户名/密码不正确')
        try:
            user = User.auth_by_password(self.db, user_name, password)
            session_data = {'userId': user.id,
                            'userName': user.userName,
                            'permissions': [p.name for p in user.permissions]}
            session_id, session_expire_time = self.generate_session(str(user.id), session_data)
            return self.api_succeeded({'sessionId': session_id})
        except:
            return self.api_failed('用户名/密码不正确')


__api_handlers__ = [
    (r'^/api/account/login$', LoginApiHandler)
]


class LoginPageHandler(PageHandler):
    def get(self, *args, **kwargs):
        return self.render('account/login.html')


class LogoutPageHandler(PageHandler):
    def get(self, *args, **kwargs):
        self.invalidate_session()
        return self.redirect('/')


__page_handlers__ = [
    (r'^/account/login$', LoginPageHandler),
    (r'^/account/logout$', LogoutPageHandler)
]
