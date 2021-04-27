from datetime import datetime
import json
import re

from sqlalchemy import Column, String, Text, or_, desc

from core.models import BaseModel, BaseModelMixin, paginate


class Library(BaseModel, BaseModelMixin):
    title = Column('title', String(40))
    blackPlayerName = Column('black_player_name', String(40))
    whitePlayerName = Column('white_player_name', String(40))
    manual = Column('manual', Text())
    pattern1 = Column('pattern_1', String(256), index=True)
    pattern2 = Column('pattern_2', String(256), index=True)
    pattern3 = Column('pattern_3', String(256), index=True)
    pattern4 = Column('pattern_4', String(256), index=True)
    pattern5 = Column('pattern_5', String(256), index=True)
    pattern6 = Column('pattern_6', String(256), index=True)
    pattern7 = Column('pattern_7', String(256), index=True)
    pattern8 = Column('pattern_8', String(256), index=True)
    pattern9 = Column('pattern_9', String(256), index=True)
    pattern10 = Column('pattern_10', String(256), index=True)
    pattern11 = Column('pattern_11', String(256), index=True)
    pattern12 = Column('pattern_12', String(256), index=True)
    pattern13 = Column('pattern_13', String(256), index=True)
    pattern14 = Column('pattern_14', String(256), index=True)
    pattern15 = Column('pattern_15', String(256), index=True)
    pattern16 = Column('pattern_16', String(256), index=True)
    pattern17 = Column('pattern_17', String(256), index=True)
    pattern18 = Column('pattern_18', String(256), index=True)
    pattern19 = Column('pattern_19', String(256), index=True)
    pattern20 = Column('pattern_20', String(256), index=True)
    pattern21 = Column('pattern_21', String(256), index=True)
    pattern22 = Column('pattern_22', String(256), index=True)
    pattern23 = Column('pattern_23', String(256), index=True)
    pattern24 = Column('pattern_24', String(256), index=True)
    pattern25 = Column('pattern_25', String(256), index=True)
    pattern26 = Column('pattern_26', String(256), index=True)
    pattern27 = Column('pattern_27', String(256), index=True)
    pattern28 = Column('pattern_28', String(256), index=True)
    pattern29 = Column('pattern_29', String(256), index=True)
    pattern30 = Column('pattern_30', String(256), index=True)

    @staticmethod
    def add(db, title, black_player_name, white_player_name, manual):
        now = datetime.now()
        library = Library()
        library.createTime = now
        library.updateTime = now
        library.title = title
        library.blackPlayerName = black_player_name
        library.whitePlayerName = white_player_name
        library.manual = manual
        library.__extract_patterns()
        db.add(library)
        db.commit()
        return library

    @staticmethod
    def update(db, library_id, title, black_player_name, white_player_name, manual):
        library = db.query(Library).filter(Library.id == library_id).one()
        library.updateTime = datetime.now()
        library.title = title
        library.blackPlayerName = black_player_name
        library.whitePlayerName = white_player_name
        library.manual = manual
        library.__extract_patterns()
        db.merge(library)
        db.commit()
        return library

    @staticmethod
    def find_by_id(db, library_id):
        return db.query(Library).filter(Library.id == library_id).one()

    @staticmethod
    def list_by_page(db, page_index, page_size=10):
        libraries = db.query(Library).order_by(desc(Library.createTime)).all()
        return paginate(libraries, page_index, page_size)

    @staticmethod
    def search_text_by_page(db, keyword, page_index, page_size=10):
        criteria = or_(Library.title.like(f'%{keyword}%'),
                       Library.blackPlayerName.like(f'%{keyword}%'),
                       Library.whitePlayerName.like(f'%{keyword}%'))
        libraries = db.query(Library).filter(criteria).order_by(desc(Library.createTime)).all()
        return paginate(libraries, page_index, page_size)

    @staticmethod
    def search_manual_by_page(db, search_datas, page_index, page_size=10):
        if not search_datas or len(search_datas) == 0:
            return Library.list_by_page(db, page_index, page_size)
        num_moves = sum(1 for c in search_datas[0] if c == '|')
        if num_moves < 1 or num_moves > 30:
            return paginate(list(), page_index, page_size)
        pattern_n = getattr(Library, f'pattern{num_moves}')
        libraries = db.query(Library).filter(pattern_n.in_(search_datas)).order_by(desc(Library.createTime)).all()
        return paginate(libraries, page_index, page_size)

    def __extract_patterns(self):
        root_move = json.loads(self.manual)
        if not self.__is_valid_move(root_move):
            raise Exception()
        descendants, max_depth, part1, part2 = root_move['d'], 30, list(), list()
        patterns = ['' for _ in range(max_depth)]
        for i in range(max_depth):
            major_found = False
            for descendant in descendants:
                if descendant['m'] == 1:
                    if i % 2 == 0:
                        part1.append('|{0}_{1}'.format(descendant['x'], descendant['y']))
                        part1.sort()
                    else:
                        part2.append('|{0}_{1}'.format(descendant['x'], descendant['y']))
                        part2.sort()
                    patterns[i] = '{0}{1}'.format(''.join(part1), ''.join(part2))
                    major_found, descendants = True, descendant['d']
                    break
            if not major_found:
                break
        self.pattern1, self.pattern2, self.pattern3, self.pattern4, self.pattern5,\
            self.pattern6, self.pattern7, self.pattern8, self.pattern9, self.pattern10,\
            self.pattern11, self.pattern12, self.pattern13, self.pattern14, self.pattern15,\
            self.pattern16, self.pattern17, self.pattern18, self.pattern19, self.pattern20,\
            self.pattern21, self.pattern22, self.pattern23, self.pattern24, self.pattern25,\
            self.pattern26, self.pattern27, self.pattern28, self.pattern29, self.pattern30 = patterns

    def __is_valid_move(self, move):
        if type(move) is not dict:
            return False
        if 'x' not in move or type(move['x']) is not int or move['x'] < -1 or move['x'] >= 15:
            return False
        if 'y' not in move or type(move['y']) is not int or move['y'] < -1 or move['y'] >= 15:
            return False
        if 'm' not in move or move['m'] not in {0, 1}:
            return False
        if 'l' in move and type(move['l']) is not str:
            return False
        if 'c' in move and type(move['c']) is not str:
            return False
        if 'd' in move:
            for descendant in move['d']:
                if not self.__is_valid_move(descendant):
                    return False
        return True


_date_pattern = re.compile(r'.*?([\d]+)年([\d]+)月.*')


class HotKeyword(BaseModel, BaseModelMixin):
    keyword = Column('keyword', String(40))

    @staticmethod
    def add(db, keyword):
        now = datetime.now()
        hot_keyword = HotKeyword()
        hot_keyword.createTime = now
        hot_keyword.updateTime = now
        hot_keyword.keyword = keyword
        db.add(hot_keyword)
        db.commit()
        return hot_keyword

    @staticmethod
    def update(db, hot_keyword_id, keyword):
        hot_keyword = db.query(HotKeyword).filter(HotKeyword.id == hot_keyword_id).one()
        hot_keyword.updateTime = datetime.now()
        hot_keyword.keyword = keyword
        db.merge(hot_keyword)
        db.commit()
        return hot_keyword

    @staticmethod
    def delete(db, hot_keyword_id):
        db.query(HotKeyword).filter(HotKeyword.id == hot_keyword_id).delete()
        db.commit()

    @staticmethod
    def list_all(db):
        def sort_key(hot_keyword):
            match = _date_pattern.match(hot_keyword.keyword)
            return (-int(match[1]), -int(match[2])) if match else (0, 0)
        hot_keywords = db.query(HotKeyword).all()
        hot_keywords = sorted(hot_keywords, key=sort_key)
        return hot_keywords
