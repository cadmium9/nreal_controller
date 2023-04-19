import pywinusb.hid as hid
import binascii 
import struct
import array as arr
import ctypes
import operator
import time
import sys
from winusbpy import *
import usb.core
import usb.util

'''
Top Level Details
-----------------

Manufacturer String:    Omnivision Technologies, Inc.
Product Sting:          USB Camera-OV580
Serial Number:          OV0001

Vendor ID:              0x05a9
Product ID:             0x0680
Version number:         0x0100

Device Path:            \\?\hid#vid_05a9&pid_0680&mi_02#b&2ba6913d&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}
Device Instance Id:     HID\VID_05A9&PID_0680&MI_02\B&2BA6913D&0&0000
Parent Instance Id:     26

Top level usage:        Page=0xa0ff, Usage=0x01
Usage identification:   Unknown Page/usage
Link collections:       1 collection(s)
'''

# Interface 2
# EndPoint Input 0x89

# Before claiming interface, there's a 1 byte packet sent:
# usb_control32: 
#    fd: 5c
#    rq: c0105500
#{"bRequestType":128,"bRequest":8,"wValue":0,"wIndex":0,"wLength":1,"timeout":1000,"data":"0xc19a4a63"}
#           0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F  0123456789ABCDEF
#c19a4a63  01 80 08 00                                      ....
#ioctl result: 0x1

class Imu():

    def __init__(self):        
        self.Vendor = 0x05a9
        self.Product = 0x0680
        self.Tick = time.perf_counter()
        self.TickKeepAlive = self.Tick
        self.PacketId = 0x61282fcd
        self.LatchedFrame = 0
        self.PacketCount = 0
        self.Sending = 0

        
        # find our device
        self.dev = usb.core.find(idVendor=self.Vendor, idProduct=self.Product)

        # was it found?
        if self.dev is None:
            raise ValueError('Glasses device not found')
        
                
        self.dev.set_configuration()
        
        
        # get an endpoint instance
        self.cfg = self.dev.get_active_configuration()
        print(self.cfg)
        # self.intf = self.cfg[(2,0)]

        # self.wrEp = usb.util.find_descriptor(
            # self.intf,
            #match the first OUT endpoint
            # custom_match = \
            # lambda e: \
                # usb.util.endpoint_direction(e.bEndpointAddress) == \
                # usb.util.ENDPOINT_OUT)
                
        # assert self.wrEp is not None
                
        # self.rdEp = usb.util.find_descriptor(
            # self.intf,
            # match the first OUT endpoint
            # custom_match = \
            # lambda e: \
                # usb.util.endpoint_direction(e.bEndpointAddress) == \
                # usb.util.ENDPOINT_IN)                

        # assert self.rdEp is not None        
        
        payload = bytearray(1)
        payload[0] = 0x01
        self.dev.ctrl_transfer(
            128,
            8,
            wValue = 0,
            wIndex = 0,
            data_or_wLength = payload,
            timeout = 1000)
        
        usb.util.claim_interface(self.dev, 2)
        
        #data = bytearray(11)
        #self.dev.write(0x00, data)
                
                
                
        # self.device = hid.HidDeviceFilter(vendor_id = self.Vendor, product_id = self.Product).get_devices()[0]        
        # self.device.open()
        
        # hid.core.show_hids(self.Vendor, self.Product)
        
        
        # self.device.set_raw_data_handler(self.OnHidRead)
        # self.report0 = self.device.find_input_reports()[0]
        # self.report = self.device.find_input_reports()[1]
        # self.reportOut = self.device.find_output_reports()[0]

    
        #self.rxBuffer = bytearray(128)        
        #self.report.set_raw_data(self.rxBuffer)
        
        
        # self.wup = WinUsbPy()
        # result = self.wup.list_usb_devices(deviceinterface=True, present=True)
        # print(result)
        
        # if self.wup.init_winusb_device(vid=self.Vendor, pid=self.Product):
            # print("WinUsbPy work")
            #[("request_type", c_ubyte), ("request", c_ubyte), ("value", c_ushort), ("index", c_ushort), ("length", c_ushort)]
            # pkt1 = self.wup.UsbSetupPacket(128, 8, 0, 0, 1)
            # self.wup.control_transfer(pkt1, buff=[0xbda81a63])
        # else:
            # print("WinUsbPy fail")
       


        # 0x21, 0x09, 0x02, 0x02, 0x02, 0x00, 0x03, 0x00, 0x02, 0x19, 0x01       
        p = bytearray(3)
        
        
        #/* F:\Sources\hacks\nreal\fridaFrame_5c_11.txt (2021-09-04 22:36:43)
        # 0x00, 0x03, 0x00, 0x02, 0x19, 0x01

        p[0] = 0x02
        p[1] = 0x19
        p[2] = 0x01
        self.hid_set_report(p)
        #self.dev.write(0, p)
        # self.SendPacket(p)

        
        # 0x85, 0x16,                    //   REPORT_ID (22)
      # 0x96, 0x00, 0x01,              //   REPORT_COUNT (256) one less then rid
      # 0x09, 0x00,                    //   USAGE (Undefined)
      # 0xb2, 0x02, 0x01,              //   FEATURE (Data,Var,Abs,Buf)
        
        
        self.inited = True

    def hid_set_report(self, report):
        """ Implements HID SetReport via USB control transfer """
        self.dev.ctrl_transfer(
          0x21,  # REQUEST_TYPE_CLASS | RECIPIENT_INTERFACE | ENDPOINT_OUT
          9,     # SET_REPORT
          0x202, # "Vendor" Descriptor Type + 0 Descriptor Index
          2,     # USB interface № 0
          report # the HID payload as a byte array -- e.g. from struct.pack()
        )

    def hid_get_report(self):
        """ Implements HID GetReport via USB control transfer """
        return self.dev.ctrl_transfer(
          0xA1,  # REQUEST_TYPE_CLASS | RECIPIENT_INTERFACE | ENDPOINT_IN
          1,     # GET_REPORT
          0x202, # "Vendor" Descriptor Type + 0 Descriptor Index
          2,     # USB interface № 0
          128     # max reply size
        )

    def Close(self):
        pass

    def SendPacket(self, packet):
        self.Sending = 1               
        self.reportOut.set_raw_data(packet)
        self.reportOut.send()
               

    def swap32(self,i):
        return struct.unpack("<I", struct.pack(">I", i))[0]
       
       
    def CRC(self, payload, len):
        gCRCBytes = arr.array ("I", [ 0x00000000, 0x96300777, 0x2c610eee, 0xba510999, 0x19c46d07, 0x8ff46a70, 0x35a563e9, 0xa395649e, 0x3288db0e, 0xa4b8dc79, 0x1ee9d5e0, 
                      0x88d9d297, 0x2b4cb609, 0xbd7cb17e, 0x072db8e7, 0x911dbf90, 0x6410b71d, 0xf220b06a, 0x4871b9f3, 0xde41be84, 0x7dd4da1a, 0xebe4dd6d, 
                      0x51b5d4f4, 0xc785d383, 0x56986c13, 0xc0a86b64, 0x7af962fd, 0xecc9658a, 0x4f5c0114, 0xd96c0663, 0x633d0ffa, 0xf50d088d, 0xc8206e3b, 
                      0x5e10694c, 0xe44160d5, 0x727167a2, 0xd1e4033c, 0x47d4044b, 0xfd850dd2, 0x6bb50aa5, 0xfaa8b535, 0x6c98b242, 0xd6c9bbdb, 0x40f9bcac, 
                      0xe36cd832, 0x755cdf45, 0xcf0dd6dc, 0x593dd1ab, 0xac30d926, 0x3a00de51, 0x8051d7c8, 0x1661d0bf, 0xb5f4b421, 0x23c4b356, 0x9995bacf, 
                      0x0fa5bdb8, 0x9eb80228, 0x0888055f, 0xb2d90cc6, 0x24e90bb1, 0x877c6f2f, 0x114c6858, 0xab1d61c1, 0x3d2d66b6, 0x9041dc76, 0x0671db01, 
                      0xbc20d298, 0x2a10d5ef, 0x8985b171, 0x1fb5b606, 0xa5e4bf9f, 0x33d4b8e8, 0xa2c90778, 0x34f9000f, 0x8ea80996, 0x18980ee1, 0xbb0d6a7f, 
                      0x2d3d6d08, 0x976c6491, 0x015c63e6, 0xf4516b6b, 0x62616c1c, 0xd8306585, 0x4e0062f2, 0xed95066c, 0x7ba5011b, 0xc1f40882, 0x57c40ff5, 
                      0xc6d9b065, 0x50e9b712, 0xeab8be8b, 0x7c88b9fc, 0xdf1ddd62, 0x492dda15, 0xf37cd38c, 0x654cd4fb, 0x5861b24d, 0xce51b53a, 0x7400bca3, 
                      0xe230bbd4, 0x41a5df4a, 0xd795d83d, 0x6dc4d1a4, 0xfbf4d6d3, 0x6ae96943, 0xfcd96e34, 0x468867ad, 0xd0b860da, 0x732d0444, 0xe51d0333, 
                      0x5f4c0aaa, 0xc97c0ddd, 0x3c710550, 0xaa410227, 0x10100bbe, 0x86200cc9, 0x25b56857, 0xb3856f20, 0x09d466b9, 0x9fe461ce, 0x0ef9de5e, 
                      0x98c9d929, 0x2298d0b0, 0xb4a8d7c7, 0x173db359, 0x810db42e, 0x3b5cbdb7, 0xad6cbac0, 0x2083b8ed, 0xb6b3bf9a, 0x0ce2b603, 0x9ad2b174, 
                      0x3947d5ea, 0xaf77d29d, 0x1526db04, 0x8316dc73, 0x120b63e3, 0x843b6494, 0x3e6a6d0d, 0xa85a6a7a, 0x0bcf0ee4, 0x9dff0993, 0x27ae000a, 
                      0xb19e077d, 0x44930ff0, 0xd2a30887, 0x68f2011e, 0xfec20669, 0x5d5762f7, 0xcb676580, 0x71366c19, 0xe7066b6e, 0x761bd4fe, 0xe02bd389, 
                      0x5a7ada10, 0xcc4add67, 0x6fdfb9f9, 0xf9efbe8e, 0x43beb717, 0xd58eb060, 0xe8a3d6d6, 0x7e93d1a1, 0xc4c2d838, 0x52f2df4f, 0xf167bbd1, 
                      0x6757bca6, 0xdd06b53f, 0x4b36b248, 0xda2b0dd8, 0x4c1b0aaf, 0xf64a0336, 0x607a0441, 0xc3ef60df, 0x55df67a8, 0xef8e6e31, 0x79be6946, 
                      0x8cb361cb, 0x1a8366bc, 0xa0d26f25, 0x36e26852, 0x95770ccc, 0x03470bbb, 0xb9160222, 0x2f260555, 0xbe3bbac5, 0x280bbdb2, 0x925ab42b, 
                      0x046ab35c, 0xa7ffd7c2, 0x31cfd0b5, 0x8b9ed92c, 0x1daede5b, 0xb0c2649b, 0x26f263ec, 0x9ca36a75, 0x0a936d02, 0xa906099c, 0x3f360eeb, 
                      0x85670772, 0x13570005, 0x824abf95, 0x147ab8e2, 0xae2bb17b, 0x381bb60c, 0x9b8ed292, 0x0dbed5e5, 0xb7efdc7c, 0x21dfdb0b, 0xd4d2d386, 
                      0x42e2d4f1, 0xf8b3dd68, 0x6e83da1f, 0xcd16be81, 0x5b26b9f6, 0xe177b06f, 0x7747b718, 0xe65a0888, 0x706a0fff, 0xca3b0666, 0x5c0b0111, 
                      0xff9e658f, 0x69ae62f8, 0xd3ff6b61, 0x45cf6c16, 0x78e20aa0, 0xeed20dd7, 0x5483044e, 0xc2b30339, 0x612667a7, 0xf71660d0, 0x4d476949, 
                      0xdb776e3e, 0x4a6ad1ae, 0xdc5ad6d9, 0x660bdf40, 0xf03bd837, 0x53aebca9, 0xc59ebbde, 0x7fcfb247, 0xe9ffb530, 0x1cf2bdbd, 0x8ac2baca, 
                      0x3093b353, 0xa6a3b424, 0x0536d0ba, 0x9306d7cd, 0x2957de54, 0xbf67d923, 0x2e7a66b3, 0xb84a61c4, 0x021b685d, 0x942b6f2a, 0x37be0bb4, 
                      0xa18e0cc3, 0x1bdf055a, 0x8def022d ])
        
        crc = 0xffffffff;
        for index in range(len):
            crc = self.swap32(gCRCBytes[int(ord(payload[index])) ^ (crc & 0xFF)]) ^ (crc >> 8);
        
        return ~crc;


    def OnHidRead(self, data):
        print("OnHidRead")
        szData = bytes(data).decode("utf-8")
        print("Rx Len " + str(len(szData)) + ": " + szData)
        self.Sending = 0
        return None

    def Process(self):
        #try:
        #    result = self.dev.read(0x89,64,100)
        result = self.hid_get_report()
        print(result)
        #except:
        #    pass
        
    
        delta = time.perf_counter() - self.Tick
        self.Tick = time.perf_counter()
        


