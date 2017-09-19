# __author: Lambert
# __date: 2017/9/19 15:27
import socketserver, subprocess, os
from server import login
from conf import setting


class Actions:
    def __init__(self, conn):
        self.conn = conn
        self.user_data = {}
        self.current_dir = './'

    def login(self, cmd_order, cmd_list):
        username = cmd_list[1]
        password = cmd_list[2]
        is_login = login.Login()
        self.user_data = is_login.validator(username, password)
        if self.user_data:
            user_dir = os.path.join(setting.BASE_DIR, 'upload', self.user_data['username'])
            if not os.path.exists(user_dir):
                os.mkdir(user_dir)
            self.user_data['dir'] = user_dir
            self.conn.send(bytes('0', 'utf8'))
        else:
            self.conn.send(bytes('-1', 'utf8'))

    def home(self, cmd_order, cmd_list):
        self.current_dir = self.user_data['dir']
        cmd_order = 'dir'
        cmd_list = ['dir']
        self.show(cmd_order, cmd_list)

    def cmd_cd(self, cmd_order, cmd_list):
        if cmd_list[0] == 'cd' and len(cmd_list) > 1:
            if cmd_list[1].find(':') == -1:
                self.current_dir = os.path.join(self.current_dir, cmd_list[1])
            elif cmd_list[1].find(':') == 1:
                self.current_dir = cmd_list[1]
        self.show(cmd_order, cmd_list)

    def show(self, cmd_order, cmd_list):
        print(self.current_dir)
        cmd_obj = subprocess.Popen(cmd_order, shell=True, stdout=subprocess.PIPE, cwd=self.current_dir)
        cmd_result = cmd_obj.stdout.read()
        self.send_msg('cmd', cmd_result)

    def send_msg(self, msg_type, msg):
        if type(msg) == str:
            msg = bytes(msg, 'utf8')
        result_length = len(msg)
        res_data = {
            'type': msg_type,
            'length': result_length,
        }
        self.conn.sendall(bytes(str(res_data), 'utf8'))
        self.conn.recv(1024)

        self.conn.sendall(msg)


class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        print('服务端启动......')
        flag = True
        while flag:
            conn = self.request
            print(self.client_address)
            print(self.client_address[1], '登录成功')
            obj = Actions(conn)
            actions = {
                'login': obj.login,
                'cd': obj.cmd_cd,
                'dir': obj.show,
                'home': obj.home
            }
            while True:
                try:
                    cmd_data = conn.recv(1024)
                except Exception as e:
                    print(e)
                    flag = False
                    break
                else:
                    if not cmd_data:
                        break
                    cmd_data = str(cmd_data, 'utf8')
                    cmd = cmd_data.split(' ')
                    if cmd[0] in actions:
                        actions[cmd[0]](cmd_list=cmd, cmd_order=cmd_data)
                    else:
                        obj.send_msg('msg', '无此项操作')
            conn.close()
