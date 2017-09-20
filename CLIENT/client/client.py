# __author: Lambert
# __date: 2017/9/19 15:39
import socket, os
from client_conf import setting


class Client(object):
    def __init__(self):
        self.sk = socket.socket()
        self.sk.connect(setting.CLIENT_ADDRESS)
        self.login()

    def send_file(self, inp_list):
        # 上传文件
        self.sk.recv(1024)
        # 获取文件信息
        file_path = os.path.join(setting.BASE_DIR, 'files', inp_list[1])
        file_size = os.stat(file_path).st_size
        file_name = os.path.basename(file_path)
        file_info = dict([('file_name', file_name), ('file_size', file_size)])
        self.sk.sendall(bytes(str(file_info), 'utf8'))

        status = str(self.sk.recv(1024), 'utf8')
        if status != '-1':
            with open(file_path, 'rb') as file:
                has_sent = 0
                while has_sent != file_size:
                    data = file.read(1024)
                    self.sk.sendall(data)
                    has_sent += len(data)
                    print(round((has_sent / file_size) * 100, 2), '%')
            self.receive_json()
        else:
            print('用户可用空间不足')

    # 封装接收消息函数
    def receive_json(self):
        data = self.sk.recv(1024)  # 先接收json
        data = eval(str(data, 'utf8'))
        if data['type'] == 'msg':
            self.receive_msg(data['length'], 'utf8')
        elif data['type'] == 'cmd':
            self.receive_msg(data['length'], 'gbk')
        elif data['type'] == 'file':
            self.receive_file(data['file_info'])
        else:
            self.receive_file()

    # 封装接收消息函数
    def receive_msg(self, length, coding):
        self.sk.send(bytes('1', 'utf8'))
        data = bytes()
        while len(data) != length:
            result = self.sk.recv(1024)
            data += result
            print(len(data))
        print(str(data, coding))

    # 封装接收文件函数
    def receive_file(self, file_info):
        file_size = file_info['file_size']
        file_name = file_info['file_name']
        file_path = os.path.join(setting.DOWN_DIR, file_name)
        # 先初始化已接收数据为0
        has_received = 0
        if os.path.exists(file_path):
            # 如果文件已经存在获取文件大小
            current_file_size = os.stat(file_path).st_size
            if current_file_size == file_size:
                # 文件已经下载完成
                print('%s已经存在' % file_name)
                self.sk.sendall(bytes('-1', 'utf8'))
            elif current_file_size < file_size:
                # 文件未下载完成，进行续传
                has_received = current_file_size
                print('%s已经接收%s开始续传' % (file_name, round(current_file_size / file_size * 100, 2)))
                self.sk.sendall(bytes(str(current_file_size), 'utf8'))
        else:
            # 文件不存在，直接下载
            self.sk.sendall(bytes('0', 'utf8'))
        # 接收文件开始
        with open(file_path, 'ab') as file:
            while has_received != file_size:
                data = self.sk.recv(1024)
                file.write(data)
                has_received += len(data)
                # 获取下载进度
                print(round((has_received / file_size) * 100, 2), '%')

    def login(self):
        # 登录成功则执行run函数
        while True:
            username = input('用户名>>>')
            password = input('密码>>>')
            self.sk.sendall(bytes('login %s %s' % (username, password), 'utf8'))
            data = str(self.sk.recv(1024), 'utf8')
            if data == '0':
                self.run(username)
            else:
                print('用户名或密码错误')

    def run(self, user):
        menu = '''
                -----------用户%s 欢迎登录FTP-----------
                切换目录:CD 盘符、相对路经、根路径 
                查看家目录:HOME 
                查看当前文件夹下文件:DIR
                下载文件:GET FILE_NAME
                上传文件:POST CLIENT_FILE_PATH
                注销:LOGOUT
                ''' % user
        while True:
            print(menu)
            inp = input('请输入指令进行操作>>>')
            inp_list = inp.split(' ')
            if inp == 'exit':
                break
            # 上传文件
            elif inp_list[0] == 'post':
                self.sk.sendall(bytes(inp, 'utf8'))
                self.send_file(inp_list)
            # 下载文件
            else:
                self.sk.sendall(bytes(inp, 'utf8'))
                self.receive_json()
