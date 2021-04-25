import os

import tornado.web
from tornado.options import options
import tornado.httpserver
import tornado.ioloop

from config import config
from core.handlers import InvalidUrlHandler
import account.handlers
import library.handlers


def main():
    config()
    handlers = list()
    handlers.extend([(r'^/$', tornado.web.RedirectHandler, {'url': '/library/hotKeywordList'})])
    handlers.extend(account.handlers.__api_handlers__)
    handlers.extend(account.handlers.__page_handlers__)
    handlers.extend(library.handlers.__api_handlers__)
    handlers.extend(library.handlers.__page_handlers__)
    handlers.extend([(r'^.*$', InvalidUrlHandler)])
    application = tornado.web.Application(
            handlers=handlers,
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            debug=options.debug)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.bind(options.port)
    http_server.start(options.num_processes)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
