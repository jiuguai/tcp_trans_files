import json
import socket 
import struct
from threading import Thread
import os
import sys
import time



class RecvFile():

    def __init__ (self,ip, port, save_dir, lister_num=2, process_count=20):
        self.save_dir = save_dir
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        #  粘包后部分的数据
        self.sticky_data = b""
        self.sock.listen(lister_num)
        self.process_count = process_count
        self.size = 0.00001
        self.file_name = None
        self.cur_size = 0

    def info(self):
        per = self.cur_size/self.size
        done = int(per * self.process_count)
        doing = self.process_count - done
        return {
            "file_name":self.file_name,
            "file_size":self.size,
            "cur_size":self.cur_size,
            "per":"{:.2%}".format(per),
            "process":"[{}{}]".format("-"*done, " "*doing),
        }

    def accept(self):
        print('连接中....')
        self.conn, self.addr = self.sock.accept()
        print(self.addr)

    def recv(self):
        self.accept()
        while  True:
            count = 0
            self.file_name = None

            if len(self.sticky_data) >= 1024:
                print('数据有余%s')
                file_info_data = self.sticky_data[:1024]
                self.sticky_data = self.sticky_data[1024:]
            else:
                read_size = 1024 - len(self.sticky_data)
                print(read_size)
                file_info_data = self.sticky_data
                self.sticky_data = b""
                while True:
                    count += 1
                    file_info_data += self.conn.recv(read_size)
                    print("文件信息长度：%s " %len(file_info_data))
                    if file_info_data != b"":
                        # 
                        if len(file_info_data) < read_size:
                            read_size -= len(file_info_data)
                            continue
                        break
                    else:
                        time.sleep(0.8)

                    # 当有 5次获取为空 从新寻找连接
                    if count == 5:
                        count = 0

                        self.accept()

            file_info_data = struct.unpack("!1024s",file_info_data)
            result = file_info_data[0].decode().strip('\x00')
            
            file_info = json.loads(result)
            print(file_info)
            self.size = file_info['size']
            self.file_name = file_info['file_name']
            self.cur_size = 0

            with open(os.path.join(self.save_dir, self.file_name), 'wb') as f:

                temp_size = len(self.sticky_data)
                
                temp = self.sticky_data
                # 处理粘包
                if self.cur_size + temp_size > self.size:
                    x = self.size - self.cur_size
                    self.sticky_data = temp[x:]
                    temp = temp[:x]
                    temp_size = x
                    f.write(temp)
                    continue

                self.sticky_data = b""
                self.cur_size += temp_size
                print(type(temp))
                f.write(temp)

                retry_count = 0
                while True:
                    print('读取数据...')
                    temp = self.conn.recv(4096)

                    temp_size = len(temp)

                    if temp_size == 0:
                        time.sleep(0.8)
                        retry_count += 1
                    else:
                        retry_count = 0

                    # 10 次获取为空将跳出
                    if retry_count > 10:
                        print('读取失败...')

                        break

                    # 处理粘包
                    if self.cur_size + temp_size > self.size:
                        x = self.size - self.cur_size
                        self.sticky_data = temp[x:]
                        temp = temp[:x]
                        temp_size = x
                    else:
                        self.sticky_data = b""

                    self.cur_size += temp_size
                    f.write(temp)
                    print("%s/%s  %s" %(self.cur_size, self.size, self.file_name))
                    if self.cur_size == self.size:
                        print('粘包大小%s' %len(self.sticky_data))
                        break


rf = None
 

def recv(ip,port,save_dir, is_accept=True,**kargs):
    global rf
    if rf is not None:
        self.sticky_data = b""
        if is_accept:
            rf.accept()
        return

    rf = RecvFile(ip, port, save_dir, **kargs)
    # rf.recv()
    Thread(target=rf.recv).start()


def get_info():

    return rf.info()

def get_rf():
    return rf

if __name__ == "__main__":
    
    save_dir = r"C:\Users\Administrator\Desktop\recv"
    # ip = "192.168.1.100"
    # port = 40000


    ip = "127.0.0.1"
    port = 6666


    recv(ip, port, save_dir)






        #  # 响应处理 | 把客服端发送过来的数据又转发回去
        # self.conn.sendall(data.encode('gbk'))
        # print(self.conn)
        # #  # 关闭客户端连接
        # self.conn.colse()