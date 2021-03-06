# __author: Lambert
# __date: 2017/9/19 16:13
from conf import setting
import os, pickle


def write_data(dic):
    with open(setting.DB_PATH, 'wb') as f:
        pickle.dump(dic, f)


def read_data():
    with open(setting.DB_PATH, 'rb') as f:
        data = pickle.load(f)
        return data


def update_data(username, user_data):
    main_data = read_data()
    main_data[username] = user_data
    with open(setting.DB_PATH, 'wb') as f:
        pickle.dump(main_data, f)
