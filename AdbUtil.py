import os
import random
import sys
from ppadb.client import Client as AdbClient
from LogUtil import Log

import subprocess

class AdbUtil:

    device = None
    adb = None
    swipe_path = [0,0,0,0]

    def getScreenDump(self):
        bytes = self.device.shell("screencap -p screen.dump")           # 16进制，头12字节为文件头，以四通道表示像素
        return bytes
    
    def getScreenBytes(self):
        process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
        screenshot = process.stdout.read()
        binary_screenshot = screenshot.replace(b'\r\n', b'\n')
        return binary_screenshot

    def getScreen(self, savePath=None):
        currentframe = None

        if self.device :
            currentframe = self.device.screencap()  

        if savePath  and len(currentframe) != 0 and currentframe is not None:
            dirs = os.path.dirname(savePath)

            if not os.path.exists(dirs):
                os.makedirs(dirs)

            with open(savePath, "wb") as f:
                f.write(currentframe)
        
        return currentframe


    def touchScreen(self, area):
        if self.device :
            self.device.input_tap(
                random.randrange(area[0],area[2]),
                random.randrange(area[1], area[3])
            )


    def longPress(self,x1,y1,duration=5000):
        if self.device :
            self.swipeScreen(x1,y1,x1,y1,duration=duration)


    def cancelSwipe(self):
        # 发送起始坐标与之前相同的滑动事件，覆盖长按。
        [x1,y1,x2,y2] = self.swipe_path
        self.swipeScreen(x1,y1,x2,y2,duration=50)


    def swipeScreen(self, x1, y1, x2, y2,duration=1000):
        # TEST
        print("swipe:",x1,y1,x2,y2)
        if self.device is not None :
            self.swipe_path = [x1,y1,x2,y2]
            self.device.input_swipe(x1, y1, x2, y2, int(random.uniform(0.5, 1.0) * duration))


    def selectSerial(self):
        devices = self.adb.devices()
        if len(devices) == 0:
            print("未检测到已连接的设备。")
            serial = input("请输入设备IP和端口进行连接（默认127.0.0.1:16384）\n")
            if serial.strip() == "":
                serial = "127.0.0.1:16384"
            ip, port = serial.split(":")
            self.adb.remote_connect(str(ip), int(port))
        else:
            print("检测到已连接的设备，请指定需要执行脚本的设备（默认设备0）:")
            for i in range(0, len(devices)):
                print("[{}] - {}".format(i, devices[i].serial))
            try:
                print("[-1] - 连接其他设备")
                index = input()
                if index is None or index == "":
                    index = 0
                else:
                    index = int(index)

                if index == -1:
                    serial = input("请输入设备IP和端口进行连接（默认127.0.0.1:16384）\n")
                    if serial.strip() == "":
                        serial = "127.0.0.1:16384"
                    ip, port = serial.split(":")
                    self.adb.remote_connect(str(ip), int(port))
                else:
                    serial = devices[index].serial
            except ValueError:
                Log.error("无效的序号。")
                sys.exit()
        return serial

    def setDevice(self, serial):

        if serial is None:
            return

        self.device = self.adb.device(serial)
        self.logDeviceInfo()

    def logDeviceInfo(self):
        try:
            props = self.device.get_properties()
            size = self.device.wm_size()

            Log.info("设备 : {}".format(props["ro.product.device"]))
            Log.info("序列号 : {}".format(self.device.serial))
            Log.info("制造商 : {}".format(props["ro.product.manufacturer"]))
            Log.info("型号 : {}".format(props["ro.product.model"]))
            Log.info("CPU 架构 : {}".format(props["ro.product.cpu.abi"]))
            Log.info("系统版本 : {}".format(props["ro.build.version.release"]))
            Log.info("分辨率 : {}x{}".format(size[0], size[1]))

        except ValueError:
            Log.error("未能获取设备信息。")
            sys.exit()

    # def checkHeartbeat(self,pid="",entry=""):
    #     if pid:
    #         wfPid = self.device.get_pid(pid)
    #         if wfPid is None:
    #             os.system('adb shell am start -n {pid}/{entry}')
    #             Log.info("游戏已停止运行，启动游戏")


    def __init__(self):
        if getattr(sys, "frozen", None):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)
        adbPath = os.path.join(basedir, "") + r"adb;"
        os.environ['PATH'] = adbPath + os.environ['PATH']
        os.system("adb start-server")
        self.adb = AdbClient(host="127.0.0.1", port=5037)


# adbUtil = AdbUtil()
