# __author: Lambert
# __date: 2017/9/19 15:27
import socketserver, subprocess
from server import login


class MyServer(socketserver.BaseRequestHandler):
    def login(self, cmd_order, cmd_list):
        username = cmd_list[1]
        password = cmd_list[2]
        is_login = login.Login()
        if is_login.validator(username, password):
            print(self.client_address[1], '登录成功')
            self.conn.send(bytes('0', 'utf8'))
        else:
            self.conn.send(bytes('-1', 'utf8'))

    def show(self, cmd_order, cmd_list):
        cmd_obj = subprocess.Popen(cmd_order, shell=True, stdout=subprocess.PIPE)
        cmd_result = cmd_obj.stdout.read()
        self.send_msg(cmd_result)

    def send_msg(self, msg):

        result_length = len(msg)
        res_data = {
            'type': 'cmd',
            'length': result_length,
        }
        self.conn.sendall(bytes(str(res_data), 'utf8'))
        self.conn.recv(1024)
        if type(msg) == 'str':
            msg = bytes(msg, 'utf8')
        self.conn.sendall(msg)

    def handle(self):
        print('服务端启动......')
        Flag = True
        hander_json = {
            'login': self.login,
            'cd': self.show,
            'dir': self.show
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
                    if not cmd_data:
                        break
                    cmd_data = str(cmd_data, 'utf8')
                    cmd = cmd_data.split(' ')
                    if cmd[0] in hander_json:
                        hander_json[cmd[0]](cmd_list=cmd, cmd_order=cmd_data)
                    else:
                        self.send_msg('无此项操作')
            self.conn.close()
