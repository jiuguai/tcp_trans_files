import json
import sys
import socket
import struct
import os
import shutil
import time
from threading import Thread

class SendFile():
    def __init__(self, ip, port, listener_dir, process_count=20):

        self.cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.cli_sock.connect((ip, port))

        self.listener_dir = listener_dir

        self.stop = False

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



    def file_filter(self, files):
        file_dir = self.listener_dir
        return [os.path.join(file_dir,file) for file in files if os.path.isfile(os.path.join(file_dir,file))]


    def listener(self):
        while True:
            
            if self.stop:
                break

            files = self.file_filter(os.listdir(self.listener_dir))
            print(files)
            if len(files) == 0:
                time.sleep(1.5)
                continue
            else:
                self.send(files)

    def send(self, files):
        
        for file_path in files:
            file_info = {
                "file_name":os.path.basename(file_path),
                "size":os.path.getsize(file_path),
                "ext":os.path.splitext(file_path)[1],
                "name":os.path.splitext(os.path.basename(file_path))[0]
            }

            print(file_info)
            self.size = file_info['size']
            self.file_name = file_info['file_name']
            self.cur_size = 0

            send_info = json.dumps(file_info)
            send_info = send_info.encode()

            r = struct.pack("!1024s", send_info)


            self.cli_sock.send(r)

            with open(file_path, "rb") as f:

                while True:
                   
                    buff = f.read(4096)
                    self.cur_size += len(buff)
                    print("%s/%s" %(self.cur_size, self.size))

                    if buff != b"":
                        self.cli_sock.send(buff)
                        # time.sleep(0.8)
                    else:
                        f.close()
                        dir_name = os.path.dirname(file_path)
                        base_name = os.path.basename(file_path)
                        print(dir_name, base_name)
                        shutil.move(file_path,os.path.join(dir_name, "已发", base_name))
                        self.file_name = None
                        break


sf = None

def send(ip, port, listener_dir):
    global sf

    if sf is not None:
        return

    sf = SendFile(ip, port, listener_dir)
    # sf.listener()  
    Thread(target=sf.listener).start()

def get_info():
    global sf
    return sf.info()

if __name__ == "__main__":
    listener_dir = r"C:\Users\Administrator\Desktop\send"
    # ip = "192.168.1.101"
    # port = 40000

    ip = "127.0.0.1"
    port = 6666
    
    send(ip, port, listener_dir)

