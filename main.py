from AdbUtil import AdbUtil
from WinUtil import WinUtil
import GalaxyFisher


bait = None                          # 预计消耗的鱼饵数
simulator = None                  # 不指定模拟器窗口名的场合，脚本默认使用 adb 截图，可后台运行，但帧间隔因设备而异(200-1000ms)，可能无法满足钓鱼需求。
simulator = "MuMu模拟器12"        # 指定模拟器窗口名的场合，脚本使用 pyautogui 截图，模拟器窗口锁定前置。帧间隔较低（30-40ms）。若无法捕捉模拟器窗口，使用 winUtil.set_window_with_title() 指定 window_index。


def run():

    serial = None
    adbUtil = AdbUtil()
           
    while not serial:   
        serial = adbUtil.selectSerial()
    else:
        adbUtil.setDevice(serial)

    winUtil = None if not simulator else WinUtil(windows_name=simulator,window_index=0)
    
    target_count = bait if bait else input("请输入预计消耗的鱼饵数：")

    fisher = GalaxyFisher.GalaxyFisher(adbUtil,winUtil)
    fisher.set_target_count(target_count)
    fisher.start()


if __name__ == "__main__":
    run()