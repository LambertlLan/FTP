# __author: Lambert
# __date: 2017/9/19 15:15
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_ADDRESS = ('127.0.0.1', 8081)
DB_PATH = os.path.join(BASE_DIR, 'db/main.json')
