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

    def receive_file(self, cmd_order, cmd_list):
        self.conn.send(bytes('1', 'utf8'))
        file_info = self.conn.recv(1024)
        file_info = eval(str(file_info, 'utf8'))
        file_name = file_info['file_name']
        file_size = file_info['file_size']
        file_path = os.path.join(self.user_data['dir'], file_name)
        self.conn.send(bytes('file_info已接收', 'utf8'))
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as file:
                has_receive = 0
                while has_receive != file_size:
                    data = self.conn.recv(1024)
                    file.write(data)
                    has_receive += len(data)
            print('%s文件接收完成' % file_name)
            self.send_msg('msg', '%s文件接收完成' % file_name)
        else:
            self.send_msg('msg', '该文件已经存在')

    def send_file(self, cmd_order, cmd_list):
        file_path = os.path.join(setting.BASE_DIR, self.user_data['dir'], cmd_list[1])
        if os.path.exists(file_path):

            file_name = os.path.basename(file_path)
            file_size = os.stat(file_path).st_size
            file_info = dict([('file_name', file_name), ('file_size', file_size)])
            file_data = {
                'type': 'file',
                'file_info': file_info,
            }
            self.conn.sendall(bytes(str(file_data), 'utf8'))
            length_response = str(self.conn.recv(1024), 'utf8')
            if length_response == '-1':
                print('当前文件在客户端已存在')
            else:
                has_send = int(length_response)
                print('开始传输文件')
                with open(file_path, 'rb') as file:
                    file.seek(has_send)
                    while has_send != file_size:
                        data = file.read(1024)
                        has_send += len(data)
                        try:
                            self.conn.sendall(data)
                        except Exception as e:
                            print(e)
                            break
                    if has_send == file_size:
                        print('%s文件下载完成' % file_name)
                    else:
                        print('%s文件传输了%s' % (file_name, round(has_send / file_size * 100, 2)))
        else:
            self.send_msg('msg', '没有该文件')


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
                'home': obj.home,
                'post': obj.receive_file,
                'get': obj.send_file
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
