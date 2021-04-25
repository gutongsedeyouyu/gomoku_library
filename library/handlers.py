from core.decorators import require_permissions
from core.handlers import ApiHandler, PageHandler
from library.models import Library, HotKeyword


class LibraryApiSaveHandler(ApiHandler):
    @require_permissions('root')
    def post(self, *args, **kwargs):
        library_id = self.get_str_argument('id', '')
        title = self.get_str_argument('title', '')
        black_player_name = self.get_str_argument('blackPlayerName', '')
        white_player_name = self.get_str_argument('whitePlayerName', '')
        manual = self.get_str_argument('manual', '')
        if not library_id:
            library = Library.add(self.db, title=title,
                                  black_player_name=black_player_name, white_player_name=white_player_name,
                                  manual=manual)
        else:
            library = Library.update(self.db, library_id=library_id, title=title,
                                     black_player_name=black_player_name, white_player_name=white_player_name,
                                     manual=manual)
        return self.api_succeeded({'id': str(library.id)})


class LibraryApiSaveHotKeywordHandler(ApiHandler):
    @require_permissions('root')
    def post(self, *args, **kwargs):
        hot_keyword_id = self.get_str_argument('id', '')
        hot_keyword_keyword = self.get_str_argument('keyword', '')
        if not hot_keyword_id:
            hot_keyword = HotKeyword.add(self.db, keyword=hot_keyword_keyword)
        else:
            hot_keyword = HotKeyword.update(self.db, hot_keyword_id=hot_keyword_id, keyword=hot_keyword_keyword)
        return self.api_succeeded({'id': str(hot_keyword.id)})


class LibraryApiDeleteHotKeywordHandler(ApiHandler):
    @require_permissions('root')
    def post(self, *args, **kwargs):
        hot_keyword_id = self.get_str_argument('id', '')
        HotKeyword.delete(self.db, hot_keyword_id=hot_keyword_id)
        return self.api_succeeded()


__api_handlers__ = [
    (r'^/api/library/save$', LibraryApiSaveHandler),
    (r'^/api/library/saveHotKeyword$', LibraryApiSaveHotKeywordHandler),
    (r'^/api/library/deleteHotKeyword$', LibraryApiDeleteHotKeywordHandler)
]


class LibraryListHandler(PageHandler):
    def get(self, *args, **kwargs):
        session = self.session_data
        page_index = self.get_int_argument('pageIndex')
        libraries, page_index, page_count = Library.list_by_page(self.db, page_index)
        return self.render('library/list.html',
                           session=session, libraries=libraries, page_index=page_index, page_count=page_count)


class LibrarySearchHandler(PageHandler):
    def get(self, *args, **kwargs):
        return self.render('library/search.html')


class LibrarySearchTextHandler(PageHandler):
    def post(self, *args, **kwargs):
        keyword = self.get_str_argument('keyword', '')
        page_index = self.get_int_argument('pageIndex')
        libraries, page_index, page_count = Library.search_text_by_page(self.db, keyword, page_index)
        return self.render('library/search_text_results.html',
                           libraries=libraries, keyword=keyword, page_index=page_index, page_count=page_count)


class LibrarySearchManualHandler(PageHandler):
    def post(self, *args, **kwargs):
        search_datas = self.get_json_argument('searchDatas', [])
        page_index = self.get_int_argument('pageIndex')
        libraries, page_index, page_count = Library.search_manual_by_page(self.db, search_datas, page_index)
        return self.render('library/search_manual_results.html',
                           libraries=libraries, search_datas=search_datas, page_index=page_index, page_count=page_count)


class LibraryViewOrEditHandler(PageHandler):
    def get(self, *args, **kwargs):
        session = self.session_data
        library_id = self.get_str_argument('id', '')
        # View/edit a blank library or an existing one.
        if not library_id:
            return self.render('library/view_or_edit.html',
                               library=None,
                               can_edit=session and 'root' in session['permissions'])
        else:
            library = Library.find_by_id(self.db, library_id=library_id)
            return self.render('library/view_or_edit.html',
                               library=library,
                               can_edit=session and 'root' in session['permissions'])


class LibraryHotKeywordListHandler(PageHandler):
    def get(self, *args, **kwargs):
        session = self.session_data
        hot_keywords = HotKeyword.list_all(self.db)
        return self.render('library/hot_keyword_list.html',
                           session=session, hotKeywords=hot_keywords, can_edit=session and 'root' in session['permissions'])


__page_handlers__ = [
    (r'^/library/list$', LibraryListHandler),
    (r'^/library/search$', LibrarySearchHandler),
    (r'^/library/searchText$', LibrarySearchTextHandler),
    (r'^/library/searchManual$', LibrarySearchManualHandler),
    (r'^/library/viewOrEdit$', LibraryViewOrEditHandler),
    (r'^/library/hotKeywordList$', LibraryHotKeywordListHandler)
]
