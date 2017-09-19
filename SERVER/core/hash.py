# __author: Lambert
# __date: 2017/9/19 16:25
import hashlib

m = hashlib.md5()


def encipher(pwd):
    m.update(pwd.encode('utf8'))
    return m.hexdigest()


print(encipher('admin'))
