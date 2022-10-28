import serial
import os
import time
import sys
import re

def bytes_to_hexstring(bytes):
    return ''.join('0x%02X, ' % b for b in bytes)

class TJCScreen():
    regular_expression = "comok ([01]),(\d+),TJC(.+),(\d+),(\d+),(.+),(\d+)\xff\xff\xff"
    regular_expression_dic = "comok (?P<屏幕类型>[01]),(\d+),(?P<型号>.+),(?P<固件号>\d+),(?P<主控芯片内部编码>\d+),(?P<唯一序列号>.+),(?P<FLASH大小>\d+)\xff\xff\xff"

    # 数据解释
    # 以TJC4024T032_011R设备为例，设备返回如下8组数据(每组数据逗号隔开):
    # comok 1,101,TJC4024T032_011R,52,61488,D264B8204F0E1828,16777216
    # comok:握手回应
    # 1:表示带触摸(0是不带触摸)
    # 101:设备内部预留数据
    # TJC4024T032_011R:设备型号
    # 52:设备固件版本号
    # 61488:设备主控芯片内部编码
    # D264B8204F0E1828:设备唯一序列号
    # 16777216:设备FLASH大小(单位：字节)
    def parse(self, data:str):
        result = re.search(self.regular_expression_dic, data)
        if result:
            (
                self.is_touch_screen,
                self.reserved_data,
                self.device_model,
                self.version,
                self.mcu_code,
                self.uuid,
                self.flash_size
            ) = result.groups()

            self.device_info = result.groupdict()

    def __init__(self):
        self.is_touch_screen = None
        self.reserved_data = None
        self.device_model = None
        self.version = None
        self.mcu_code = None
        self.uuid = None
        self.flash_size = None
        
        self.device_info = None

'''
    陶晶池 串口屏 程序更新
    协议 http://wiki.tjc1688.com/doku.php?id=6.%E6%8C%87%E4%BB%A4%E9%9B%86:6.%E9%AB%98%E7%BA%A7%E5%BA%94%E7%94%A8%E4%B8%8E%E7%89%B9%E6%AE%8A%E6%8C%87%E4%BB%A4#b2
    (1) 连接屏幕
    (2) 发送下载指令 whmi-wri {文件大小},{波特率},0\xff\xff\xff
    (3) 开始下载程序,每次最多发送4096比特
'''
class UpGrade():
    ota_file = None
    ota_file_size = None
    port = serial.Serial()

    # 属性
    is_touch_screen = True
    reserved_data: int

    def search(self):
        pass

    @classmethod
    def connect(cls):
        cls.port.write(b'\x00\xff\xff\xff')
        cls.port.read(1024)
        cls.port.write(b'connect\xff\xff\xff')
        print(cls.port.read(1024))

    @classmethod
    def begin_download(cls):
        cls.port.write(b'whmi-wri ' + str(cls.ota_file_size).encode('utf-8') + b',115200,0\xff\xff\xff')
        time.sleep(0.5)
        while(cls.port.read(1024) != b'\x05'):
            pass

    @classmethod
    def end_download(cls):
        i = cls.ota_file_size
        send_size = 0
        with open(cls.ota_file, 'rb') as f:
            while send_size<cls.ota_file_size:
                if (i>=4096):
                    cls.port.write(f.read(4096))
                    i = i-4096
                    send_size = send_size + 4096
                else:
                    cls.port.write(f.read(i))
                    send_size = send_size + i
                    i = 0
                while(cls.port.read(1024) != b'\x05'):
                    pass
                print("progress: %" + str(((cls.ota_file_size-i)/cls.ota_file_size)*100) + ' ' + str(send_size))

    @classmethod
    def read_tft_file(cls, filename):
        cls.ota_file = filename
        cls.ota_file_size = os.path.getsize(filename)
        print(b'whmi-wri ' + str(cls.ota_file_size).encode('utf-8') + b',115200,0\xff\xff\xff')

    def __init__(self, port_name):
        self.port.port = port_name
        self.port.baudrate = 115200
        self.port.timeout = 0.1
        self.port.open()

if __name__ == '__main__':
    pass