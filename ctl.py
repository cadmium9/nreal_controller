import operator
import time
import sys
import getopt
import os
import array
import os.path
import cv2
import math
from numpy import save

from monitor import Monitor
from camera import Camera
from glasses import Glasses
from imu import Imu

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image

from math import *
from string import *

def ShowCmdHelp():
    print("Command-Line Parameters:\n")
    print("-h, --help       =   Show Help")
    print("-v, --verbose    =   Verbose Mode")

def main(argv=None):

    print("Controller for Nreal Light")
    print("--------------------------\n")
    
    monitors = Monitor.list_monitors()
    for monitor in monitors:
        print(monitor)
    


    # print(str(SlamCamera.image_grabbed.shape))
    
    # plt.axis("off")
    # plt.imshow(SlamCamera.image_grabbed)
    # plt.show()
    
    #cv2.imshow('grayscale image', SlamCamera.image_grabbed)    
    #image = Image.frombytes('L', (SlamCamera.height, SlamCamera.width), frame)
    #image.show()
    # while True:
        # time.sleep(0.1)
    
    # return 1
    
    
    if argv is None:
        argv = sys.argv
    
    try:
        opts, args = getopt.getopt(argv[1:], "h:v", ["help", "verbose"])
    except getopt.GetoptError as msg:        
        print(str(msg))
        ShowCmdHelp()
        return 1
        
    pUsbMonFile = ""
    pUsbDevice = ""
    pVerbose  = False
        
    for o, a in opts:
        if o in ("-h", "--help"):
            ShowCmdHelp()
            return 2

        elif o in ("-v", "--verbose"):
            pVerbose = True
        
        else:
            assert False, "Unhandle Option!"


   
    nreal = Glasses()
    startPacketId = nreal.PacketId
    sdkStarted = 0
    frameCount = 0
    
   # Shake
   
    nreal.Active()
    while nreal.Sending != 0:
       time.sleep(0.1)      
   
    nreal.OpenPower()
    while nreal.Sending != 0:
        time.sleep(0.1)
        
    # nreal.OpenOrbitFunction()
    # while nreal.Sending != 0:
        # time.sleep(0.1)

    nreal.OpenKeySwitch()
    while nreal.Sending != 0:
        time.sleep(0.1)        

    # nreal.OpenUSARTLog()
    # while nreal.Sending != 0:
        # time.sleep(0.1)        
    
    nreal.OpenGeoMagnetism()
    while nreal.Sending != 0:
       time.sleep(0.1)        
    

    # nreal.DisplayStart()
    # while nreal.Sending != 0:
        # time.sleep(0.1)

    # nreal.DisplayUpdate()
    # while nreal.Sending != 0:
        # time.sleep(0.1)

    #nreal.SDKShake()
    #while nreal.Sending != 0:
    #    time.sleep(0.1)
       

    #nreal.SetUpdateTime0()
    #while nreal.Sending != 0:
    #   time.sleep(0.1)        
       
       
    # nreal.CloseGeoMagnetism()
    # while nreal.Sending != 0:
       # time.sleep(0.1)        
       
    nreal.OpenTemp()
    while nreal.Sending != 0:
       time.sleep(0.1)        

    # nreal.SuperActive()
    # while nreal.Sending != 0:
        # time.sleep(0.1)        
    
    nreal.SetDisplayMode3D1080_72hz()
    while nreal.Sending != 0:
        time.sleep(0.1)        
    
    nreal.OLedStart()
    while nreal.Sending != 0:
        time.sleep(0.1)        
    
    # nreal.OpenRGBCamera()
    # while nreal.Sending != 0:
        # time.sleep(0.1)        
    
    # nreal.ResetOV580()
    # while nreal.Sending != 0:
        # time.sleep(0.1)        
    
    # nreal.OpenOV580()
    # while nreal.Sending != 0:
        # time.sleep(0.1)        

    nreal.SetPrivilegiation()
    while nreal.Sending != 0:
        time.sleep(0.1)        


    # Set Super active

    


    #Odometry = Imu()
    
    #SlamCamera = Camera()
    
    # print(SlamCamera.get_devices())    

    # SlamCamera.set_device(1)
    # SlamCamera.start()
    # SlamCamera.grab_frame()
    # SlamCamera.wait_image()

    
    
    # ax1 = plt.subplot(1,1,1)    
    # plt.axis("off")
    # img = ax1.imshow(SlamCamera.image_grabbed)    
    # plt.ion()
    
    
    frameid = 0
    
    
    renderTick = time.perf_counter()
    while True:
        nreal.Process()
        #Odometry.Process()
        frameCount = frameCount + 1
        
        if (sdkStarted == 0) and (nreal.PacketId == 0x61282fcf and nreal.Sending == 0):
            sdkStarted = 1
            nreal.StartSDK()

        if time.perf_counter() - renderTick > 0.05:
            renderTick = time.perf_counter()
            frameid = frameid + 1
            # SlamCamera.grab_frame()
            # SlamCamera.wait_image()
            
            #for a in range(0,128,1):
            #    print(hex(SlamCamera.image_grabbed[480,a,0]) + hex(SlamCamera.image_grabbed[480,a,1]) + hex(SlamCamera.image_grabbed[480,a,2]), end='')
            #print()

            # img.set_data(SlamCamera.image_grabbed)
            # plt.draw()
            # plt.pause(0.0000001)

        if (frameCount % 10000) == 0:
            time.sleep(0.000000000001)
        
   # nreal.KeepAlive()
    #payload = chr(2)+":4:M:50:61282fe5:00000000:"+chr(3)
    #print("CRC = " + hex(nreal.CRC(payload, len(payload)-10) % (1<<32)))
    #nreal.wrEp.write();

   
    return 0


if __name__ == "__main__":
    sys.exit(main())
