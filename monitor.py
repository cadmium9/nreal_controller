import logging
import win32api
import time
import pywintypes
 
 
from win32con import MONITOR_DEFAULTTONEAREST
from win32con import MONITOR_DEFAULTTOPRIMARY
import ctypes
from ctypes import wintypes


class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('DeviceName', wintypes.WCHAR * 32),
        ('DeviceString', wintypes.WCHAR * 128),
        ('StateFlags', wintypes.DWORD),
        ('DeviceID', wintypes.WCHAR * 128),
        ('DeviceKey', wintypes.WCHAR * 128)
    ]


        
class Monitor(object):
 
    def __init__(self, hMonitor): 
        self.hMonitor = hMonitor 
        self.deviceId = win32api.GetMonitorInfo(hMonitor)["Device"]
        self.name = self.deviceId

    def __eq__(self, other): 
        return int(self.hMonitor) == int(other.hMonitor)
 
    def __hash__(self): 
        return hash(self.hMonitor)
 
    def exists(self):
        if self in display_monitors():
            return True
 
        else:
            return False

    def __str__(self):
        return str(self.deviceId) + "\\" + str(self.name)
 
 
    def contains_window(self, window):
        """
        Checks if the given window is in the monitor
        Returns true if it is
        Returns false if it is not
        Returns None on error
        """
 
        try:
 
            if win32api.MonitorFromWindow(window.hWindow, MONITOR_DEFAULTTONEAREST) == self.hMonitor:
 
                return True
 
            else:
 
                return False
 
        except win32api.error:
 
            logging.exception("Error while grabbing monitor from window")
             
            return None
 
    def is_main(self):
        """
        Looks if the monitor is the main monitor
        """
 
        try:
 
            if self.hMonitor == win32api.MonitorFromPoint((0, 0), MONITOR_DEFAULTTOPRIMARY):
 
                return True
 
            else:
 
                return False
 
        except win32api.error:
         
            logging.exception("Error while grabbing the monitor with point 0,0")
 
            return None
 
    def has_point(self, point):
        """
        Looks if the monitor contains the point
        """
 
        try:
 
            if self.hMonitor == win32api.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST):
 
                return True
 
            else:
 
                return False
 
        except win32api.error:
         
            logging.exception("Error while grabbing the monitor with point")
 
            return None
 
    @property
    def workarea(self):
        """
        Returns the work rectangle for the monitor
        Tuple (left, top right, bottom)
        Returns None on error
        """
 
        try:
 
            return win32api.GetMonitorInfo(self.hMonitor)["Work"]
 
        except win32api.error:
             
            logging.exception("Error while getting the monitorinfo")
 
            return None

 
    @staticmethod
    def list_monitors():
        EnumDisplayDevices = ctypes.windll.user32.EnumDisplayDevicesW       # get the function address
        EnumDisplayDevices.restype = ctypes.c_bool                          # set return type to BOOL

        """    
        the following list 'displays', stores display adapter info in the following Structure:
        
            'List containing Tuple of displayAdapterInfo and list of monitorInfo controlled by the adapter'
            [
                (dispAdapterInfo1, [Monitor1, Monitor2, . . . ]), 
                (dispAdapterInfo2, [Monitor1, Monitor2, . . . ]), 
                . . . .
            ]
            
            Number of dispAdapter depends on the graphics driver, and number of Monitors per adapter depends on 
            number of monitors connected and controlled by adapter.
        """
        displays = []

        i = 0                   # iteration variable for 'iDevNum'
        while True:
            DISP_INFO = DISPLAY_DEVICEW()               # struct object for adapter info
            DISP_INFO.cb = ctypes.sizeof(DISP_INFO)     # setting 'cb' prior to calling 'EnumDisplayDevicesW'

            if not EnumDisplayDevices(None, i, ctypes.byref(DISP_INFO), 0):
                break       # break as soon as False is returned by 'EnumDisplayDevices'

            monitors = []       # stores list of monitors per adapter
            j = 0
            while True:
                MONITR_INFO = DISPLAY_DEVICEW()              # struct object for Monitor info
                MONITR_INFO.cb = ctypes.sizeof(MONITR_INFO)  # setting 'cb' prior to calling 'EnumDisplayDevicesW'

                if not EnumDisplayDevices(DISP_INFO.DeviceName, j, ctypes.byref(MONITR_INFO), 0):
                    break  # break as soon as False is returned by 'EnumDisplayDevices'

                monitors.append(MONITR_INFO)
                j += 1

            displays.append((DISP_INFO, monitors))      # add the tuple (dispAdapterInfo, [MonitorsInfo])
            i += 1
     
        try: 
            for hMonitor, hdcMonitor, pyRect in win32api.EnumDisplayMonitors():
                monitor = Monitor(hMonitor)
                
                # Associate deviceId wit monitor name
                for display in displays:
                    if display[1] and display[0].DeviceName == monitor.deviceId:
                        monitor.name = display[1][0].DeviceString
                        break
                
                monitors.append(monitor)
 
            return monitors
 
        except win32api.error:
 
            logging.exception("Error while enumerating display monitors")
 
            return None
     
 
 
    @staticmethod
    def main_monitor_from_list(monitors):
        """
        Returns the main monitor
        main monitor is determined by returning the monitor containing
        coordinate 0,0
        """
 
        for monitor in monitors:
 
            if monitor.is_main():
 
                return monitor
 
    @staticmethod
    def monitor_from_point_in_list(monitors, point):
        """
        Returns the monitor from point
        """
 
        for monitor in monitors:
 
            if monitor.has_point(point):
 
                return monitor
 
    @staticmethod
    def monitor_from_window_in_list(monitors, window):
        """
        Returns the monitor from the window
        """
 
        for monitor in monitors:
 
            if monitor.contains_window(window):
 
                return monitor
 
    @staticmethod
    def current_monitor_from_list(monitors):
        """
        win32api.GetCursorPos() might fail repeatedly after wakeup from
        hibernate due to the underlying handle not (yet) being valid.
        Keep retrying for some time.
        """
 
        sleep_seconds = 2
        maximum_sleep = 60
        total_sleep = 0
 
 
        while total_sleep <= maximum_sleep:
 
            try:
                 
                result = Monitor.monitor_from_point_in_list(monitors,
                        win32api.GetCursorPos())
 
                logging.debug("current_monitor_from_list Total sleep time: %s)",
                        str(total_sleep))
 
                return result
 
            except pywintypes.error:
 
                time.sleep(sleep_seconds)
 
                total_sleep = total_sleep + sleep_seconds
 
 
        return None