# __author: Lambert
# __date: 2017/9/19 15:27
import socketserver
from server import login


class MyServer(socketserver.BaseRequestHandler):
    def login(self, cmd):
        username = cmd[1]
        password = cmd[2]
        is_login = login.Login()
        if is_login.validator(username, password):
            print(self.client_address, '登录成功')
            self.conn.sendall(bytes('0', 'utf8'))

    def handle(self):
        print('服务端启动......')
        Flag = True
        hander_json = {
            'login': self.login
        }
        while Flag:
            self.conn = self.request
            print(self.client_address)
            while True:
                try:
                    cmd_data = self.conn.recv(1024)
                except Exception as e:
                    print(e)
                    Flag = False
                    break
                else:
                    cmd_data = str(cmd_data, 'utf8')
                    cmd = cmd_data.split(' ')
                    if cmd[0] in hander_json:
                        hander_json[cmd[0]](cmd)
                    else:
                        self.conn.sendall(bytes('无此操作选项', 'utf8'))
            self.conn.close()
