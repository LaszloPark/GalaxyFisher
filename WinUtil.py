import win32gui,win32con
import pyautogui


class WinUtil:

    window = None

    def __init__(self,windows_name:str,window_index:int=0) -> None:
        self.set_window_with_title(windows_name,window_index)
    
    @property
    def window(self):
        return self._window


    @window.setter
    def window(self,window):
        self._window = window
        self._left = window.left
        self._top = window.top
        self._width = window.width
        self._height = window.height
        self._title = window.title
        self._hwnd = window._hWnd
        # print(">>> " + window.title)


    @property
    def name(self):
        return self._title

    def set_window_with_title(self,window_title:str,window_index:int=0):
        # TODO：出于未知原因，win32gui截取的模拟器图片总是全黑，故使用pyautogui。由于ImgUtil使用了cv2，不得不多一步pil_to_cv2 改为win32gui将提高帧循环速度
        window = pyautogui.getWindowsWithTitle(window_title)[window_index]      
        self.activate(window._hWnd)
        window = pyautogui.getWindowsWithTitle(window_title)[window_index]
        self.window = window


    def activate(self,hwnd=None):
        if hwnd is None:
            hwnd = self._hwnd
        # try:
        #     win32gui.SetForegroundWindow(hwnd)  
        # except:
        #     print(sys.exc_info())
        win32gui.ShowWindow(hwnd,win32con.SW_NORMAL)


    def get_window_rect(self):
        if self.window is None:
            return None
        return self._left,self._top,self._width,self._height


    def get_window_snap(self):
        return pyautogui.screenshot(region=self.get_window_rect())


    def set_focus(self,focus_on:bool=True):
        hwnd = self._hwnd
        if focus_on:
            self.activate()
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOOWNERZORDER | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        else:
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)



if __name__ == "__main__":
    
    window = WinUtil("MuMu模拟器12")
    # window.set_window_with_title("MuMu模拟器12")

