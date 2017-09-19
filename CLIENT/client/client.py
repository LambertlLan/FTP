# __author: Lambert
# __date: 2017/9/19 15:39
import socket
from client_conf import setting


class Client:
    def __init__(self):
        self.sk = socket.socket()
        self.sk.connect(setting.CLIENT_ADDRESS)
        self.login()

    def run(self, user):
        menu = '''
                -----------用户%s 欢迎登录FTP-----------
                切换目录:CD
                查看家目录:HOME
                查看当前文件夹下文件:DIR
                下载文件:GET FILE_NAME
                上传文件:POST CLIENT_FILE_PATH
                退出:EXIT
                ''' % user
        while True:
            print(menu)
            inp = input('请输入指令进行操作>>>')
            if inp == 'exit':
                break
            self.sk.sendall(bytes(inp, 'utf8'))
            data = self.sk.recv(1024)  # 先接收json
            data = eval(str(data, 'utf8'))
            if data['type'] == 'msg':
                self.receive_msg(data['length'], 'utf8')
            elif data['type'] == 'cmd':
                self.receive_msg(data['length'], 'gbk')
            else:
                self.receive_file()

    def receive_msg(self, length, coding):
        self.sk.send(bytes('1', 'utf8'))
        data = bytes()
        while len(data) != length:
            result = self.sk.recv(1024)
            data += result
        print(str(data, coding))

    def receive_file(self):
        pass

    def login(self):
        while True:
            username = input('用户名>>>')
            passwrod = input('密码>>>')
            self.sk.sendall(bytes('login %s %s' % (username, passwrod), 'utf8'))
            data = str(self.sk.recv(1024), 'utf8')
            if data == '0':
                self.run(username)
            else:
                print('用户名或密码错误')
