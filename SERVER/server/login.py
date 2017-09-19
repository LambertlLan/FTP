# __author: Lambert
# __date: 2017/9/19 16:55
from db import db_hander
import hashlib


class Login:
    def validator(self, user, pwd):
        main_json = db_hander.read_data()
        if user in main_json:
            m = hashlib.md5()
            m.update(pwd.encode('utf8'))
            if main_json[user] == m.hexdigest():
                return True
        else:
            return False
