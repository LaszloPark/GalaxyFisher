import sys,os
import time
import json
import threading

import ImgUtil

from LogUtil import Log
from random import randrange

class GalaxyFisher():
    
    interval = 0.2              # 主循环间隔，单位为秒。情景判断的逻辑包含于此循环。此间隔未计算逻辑实现所需时间。
    frame_interval = 0          # 帧循环间隔，单位为秒。有微操需求的逻辑包含此循环。此间隔未计算逻辑实现所需时间。
    where_to_reel = (0.4,1)     # 鱼的挣扎槽位于何处时拉杆, [0,1]
    loose_time = 0.3            # 松杆时长。单位为秒。目的是为了避免频繁操作，取值比较随意，但不建议大于0.6，可能导致漏鱼。

    config_path = "./config.json"
    images_path = "./templaters"
    
    screen = None
    bait_count = 0
    target_count = 1
    config_dict = {}


    def __init__(self,adb_util,win_util=None) -> None:
        self._adb_util = adb_util
        self._win_util = win_util

        if self._win_util:
            Log.info("使用模拟器窗口捕捉加速帧循环。")
            self.set_win_util(win_util)
        else:
            self.load_config()
    
        self._is_reeling = False
        self.reel_thread = threading.Thread(target=self.reel)

        Log.info("初始化完毕。")


    def start(self):
        while self.bait_count < self.target_count:
            self.mainloop()
        else:
            Log.info("已达到目标饵数，即将退出程序。")
            time.sleep(3)
            sys.exit()


    def load_config(self):
        with open(self.config_path, 'r') as json_file:
            configs = json.load(json_file)

        for key,value in configs.items():

            if not all((
                    "enable" in value and type(value["enable"]) is bool,
                    "path" in value and type(value["path"]) is str
                )):
                Log.warning("无效的配置项： {}".format(configs[key]))
                continue

            if value["enable"]:
                self.config_dict[key] = value
                self.config_dict[key]["path"] = os.path.normpath(os.path.join(self.images_path,self.config_dict[key]["path"]))
                self.config_dict[key]["rect"] = value["rect"] if "rect" in value else None
                self.config_dict[key]["pic"] = ImgUtil.read_from_path(self.config_dict[key]["path"])
                self.config_dict[key]["mask"] = ImgUtil.get_image_mask(self.config_dict[key]["pic"])
                Log.info("导入:{}".format(self.config_dict[key]["path"]))


    def mainloop(self):
        Log.debug("进入主循环。")
        self.update()
        for key,value in self.config_dict.items():
            Log.debug("检测：" + key)
            cropped = ImgUtil.crop_image(self.screen,value["rect"])
            if ImgUtil.match_image(cropped,value["pic"],value["threshold"],value["mask"]):
                Log.info("识别到" + key)
                self.do_action(key)
            else:
                continue
        time.sleep(self.interval)


    def update(self):
        t = time.time()
        if self._win_util is None:
            screen_bytes = self._adb_util.getScreenBytes()
            self.screen = ImgUtil.read_from_bytes(screen_bytes)
        else:
            self.screen = ImgUtil.read_from_pil(self._win_util.get_window_snap())
        # time.sleep(self.frame_interval)
        Log.debug("更新帧耗时 %f" % (time.time() - t))


    def set_target_count(self,target_count):
        self.target_count = target_count


    @property
    def adb_util(self):
        return self._adb_util.device.get_properties()["ro.product.device"]

    @property
    def win_util(self):
        return self._win_util.name

    # def set_adb_util(self,abd_util):
        # TODO:分离逻辑

    def set_win_util(self,win_util):
        Log.info("当前捕捉的模拟器：{}".format(self._win_util.name))
        self._win_util = win_util
        self._win_util.set_focus()
        self.load_config()
        self.add_offset_to_dict()


    def fishing(self):
        Log.info("尝试钓鱼。")
        bar_sample = self.config_dict["bar"]["pic"]
        bar_rec = self.config_dict["bar"]["rect"]
        bar_match_thres = self.config_dict["bar"]["threshold"]

        height,width,_ = bar_sample.shape
        center_row = height // 2
        
        min_tense = width * self.where_to_reel[0]
        max_tense = width * self.where_to_reel[1]

        bar_on_screen = ImgUtil.crop_image(self.screen,bar_rec)
        
        if self.reel_thread.is_alive():
            self.reel_thread.join() 
            self.reel_thread = threading.Thread(target=self.reel)
            self.reel_thread.start()

        count = 0

        while ImgUtil.match_image(bar_on_screen,bar_sample,bar_match_thres) is not None:
            tense = ImgUtil.match_pixel_color(bar_on_screen[center_row:],ImgUtil.WHITE)
            if tense:
                tense = tense[1]
                if count >= 10:
                    Log.info("当前张力：" + "=" * (tense//10) + "▼" + "=" * ((width - tense)//10))
                    count = 0
                else:
                    count += 1
                    
                if min_tense <= tense <= max_tense:
                    if self._is_reeling:
                        pass
                    else:
                        if self.reel_thread.is_alive():
                            self.reel_thread.join()
                        self.reel_thread = threading.Thread(target=self.reel)
                        self.reel_thread.start()
                else:
                    if self._is_reeling:
                        self.loose()
            self.update()
            bar_on_screen = ImgUtil.crop_image(self.screen,bar_rec)


    def reel(self,duration=1000):
        Log.info("收线。")
        self._is_reeling = True
        rect = self.config_dict["pull"]["rect"]
        x1 = randrange(rect[0], rect[2])
        y1 = randrange(rect[1], rect[3])
        self._adb_util.longPress(x1,y1,duration=duration)
        self._is_reeling = False


    def loose(self):
        Log.info("松线。")
        self._adb_util.cancelSwipe()
        time.sleep(self.loose_time)
        self._is_reeling = False



    def click(self,action):
        Log.info("点击 {}".format(action))
        self._adb_util.touchScreen(self.config_dict[action]["rect"])


    def do_action(self,action):
        #TODO: Hardcoding

        if action in ["bar","pull"]:
            self.fishing()
        if action in ["confirm","fish_caught"]:
            self.click(action)
            self.bait_count += 1
            time.sleep(2)
        if action == "start_fishing":
            self.click(action)
            time.sleep(3)


    def add_offset_to_dict(self):
        screen_bytes = self._adb_util.getScreenBytes()
        adb_screen = ImgUtil.read_from_bytes(screen_bytes)
        self.update()
        [x,y,_,_] = ImgUtil.match_image(self.screen,adb_screen,0.8)
        Log.debug("修正窗口轮廓：x:{},y:{}".format(x,y))
        keys = self.config_dict.keys()
        new_dict = self.config_dict.copy()
        for key in keys:
            rect = self.config_dict[key]["rect"]
            if rect:
                new_dict[key]["rect"] = [rect[0] + x,rect[1] + y, rect[2] + x, rect[3]+y ]
        self.config_dict = new_dict


if __name__ == "__main__":
    from AdbUtil import AdbUtil
    from WinUtil import WinUtil
    Log.setDebugLevel()
    adbUtil = AdbUtil()
    win_util = WinUtil("MuMu模拟器12")
    # adbUtil.adb.remote_disconnect()
    adbUtil.adb.remote_connect("127.0.0.1",16384)
    adbUtil.setDevice("127.0.0.1:16384")
    fisher = GalaxyFisher(adbUtil,win_util)
    # fisher = GalaxyFisher(adbUtil)
    fisher.set_target_count(3)
    fisher.start()