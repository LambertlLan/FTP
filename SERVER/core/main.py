# __author: Lambert
# __date: 2017/9/19 15:15
import socketserver, os, hashlib
from server import server
from conf import setting
from db import db_hander


def init_db():
    if not os.path.exists(setting.DB_PATH):
        main_json = {'admin': {'pwd': '21232f297a57a5a743894a0e4a801fc3', 'uploading_file': {}, 'downloading_file': {}}}
        db_hander.write_data(main_json)


def run():
    init_db()
    _server = socketserver.ThreadingTCPServer(setting.SERVER_ADDRESS, server.MyServer)
    _server.serve_forever()
