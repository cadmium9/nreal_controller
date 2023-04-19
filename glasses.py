import pywinusb.hid as hid
import binascii 
import struct
import array as arr
import ctypes
import operator
import time
import sys



'''
T:  Bus=01 Lev=02 Prnt=04 Port=01 Cnt=02 Dev#=  7 Spd=12   MxCh= 0
D:  Ver= 2.00 Cls=00(>ifc ) Sub=00 Prot=00 MxPS= 8 #Cfgs=  1
P:  Vendor=0486 ProdID=573c Rev= 2.00
S:  Manufacturer=STMicroelectronics
S:  Product=NREAL GLASSES
S:  SerialNumber=00000000001A
C:* #Ifs= 1 Cfg#= 1 Atr=c0 MxPwr=100mA
I:* If#= 0 Alt= 0 #EPs= 2 Cls=03(HID  ) Sub=00 Prot=00 Driver=usbfs
E:  Ad=81(I) Atr=03(Int.) MxPS=  64 Ivl=1ms
E:  Ad=01(O) Atr=03(Int.) MxPS=  64 Ivl=1ms
'''

class Glasses():

    def __init__(self):        
        self.Vendor = 0x0486
        self.Product = 0x573c
        self.Tick = time.perf_counter()
        self.TickKeepAlive = self.Tick
        self.PacketId = 0x61282fcd
        self.LatchedFrame = 0
        self.PacketCount = 0
        self.Sending = 0
                
        self.device = hid.HidDeviceFilter(vendor_id = self.Vendor, product_id = self.Product).get_devices()[0]        
        self.device.open()
        
        hid.core.show_hids(self.Vendor, self.Product)
        
        self.device.set_raw_data_handler(self.OnHidRead)
        self.report = self.device.find_output_reports()[0]
      
        
        self.inited = True

    def Close(self):
        pass
       

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
        szData = bytes(data).decode("utf-8")
        #print("Rx Len " + str(len(szData)) + ": " + szData)
        self.Sending = 0
        return None
        
    def CreatePacket(self, payload):
        payload = chr(2) + payload
        crc = '{0:{1}x}'.format(self.CRC(payload, len(payload)) % (1<<32), 8)
        payload = payload + crc + ":" + chr(3)
        
        # Create HID payload
        rawdata = bytearray(bytes([0]))
        rawdata += bytes(payload, 'utf-8')
        if len(rawdata) < 65:
            for i in range(65-len(rawdata)):
                rawdata += bytes([0])
                
        return rawdata
    
    def SendPacket(self, packet):
        self.Sending = 1       
        
        szData = bytes(packet).decode("utf-8")
        #print("Tx Len " + str(len(packet)) + ": " + str(szData))
        self.report.set_raw_data(packet)
        self.report.send()
        
        self.PacketCount = self.PacketCount + 1
        
    
    def KeepAlive(self):
        if self.Sending == 1:
            return
            
        #if self.LatchedFrame == 0:
        #    if (self.PacketCount > 7) ==  0:
        self.PacketId = self.PacketId + 1
        #else:
        #    self.PacketId = self.LatchedFrame
        
        
        tickMs = int(self.Tick * 1000) % (1<<32)        
        payload = ":@:K:" + '{0:0{1}x}'.format(tickMs, 16) +  ":" + '{0:0{1}x}'.format(self.PacketId, 8) + ":"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)
        
    def StartSDK(self):
        #@:3:1:61282fcf:c0f55a9d:
        self.LatchedFrame = self.PacketId
        payload = ":@:3:1:" + '{0:0{1}x}'.format(self.PacketId, 8) + ":"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)
        
    def OpenPower(self):
        payload = ":1:9:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)

    def DisplayStart(self):
        payload = ":1:X:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)
        
    def DisplayUpdate(self):
        payload = ":@:M:0:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)

    def OpenOrbitFunction(self):
        payload = ":3:7:0:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)        

    def CloseOrbitFunction(self):
        payload = ":@:4:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)        

    def SetUpdateTime0(self):
        payload = ":@:5:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def OpenKeySwitch(self):
        payload = ":@:H:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   
        
    def OpenRGBCamera(self):
        payload = ":1:h:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)           
        
    def OpenUSARTLog(self):
        payload = ":@:1:8:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)           
        
    def OpenGeoMagnetism(self):
        payload = ":1:U:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)         

    def CloseGeoMagnetism(self):
        payload = ":1:U:0:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)         
       
    def SDKShake(self):
        payload = ":@:N:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   
    
    def ReadEEPROM(self, addr):
        payload = ":3:K:" + '{0:{1}x}'.format(addr, 8) +":6:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   
           
    def ResetOV580(self):
        payload = ":1:T:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   
    
    def OpenOV580(self):
        payload = ":1:i:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   
                
    def OpenTemp(self):
        payload = ":1:`:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def Active(self):
        payload = ":1:e:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet) 

    def SuperActive(self):
        payload = ":1:g:1:0:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet) 

    def OLedStart(self):
        payload = ":F:1:1:2:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def SetDisplayMode2D1080(self):
        payload = ":1:3:1:2:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def SetDisplayMode3D540(self):
        payload = ":1:3:2:2:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def SetDisplayMode3D1080(self):
        payload = ":1:3:3:2:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def SetDisplayMode3D1080_72hz(self):
        payload = ":1:3:4:2:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def SetPrivilegiation(self):
        payload = ":1:g:1:613ac044:"
        packet = self.CreatePacket(payload)
        
        self.SendPacket(packet)   

    def Process(self):
        delta = time.perf_counter() - self.Tick
        self.Tick = time.perf_counter()
        
        # 100ms KeepAlive signal
        if self.Tick - self.TickKeepAlive > 0.1:
            #print("Delta KA " + str(self.Tick - self.TickKeepAlive))
            self.TickKeepAlive = self.Tick            
            self.KeepAlive()


def fmthex(stri):
    result = stri
    i = stri.find('L')
    if (i > -1):
        result = stri[:-1]
    return result

def ReverseByteEndian(data):
    """
    Method to reverse the byte order of a given unsigned data value
    Input:
        data:   data value whose byte order needs to be swap
                data can only be as big as 4 bytes
    Output:
        revD: data value with its byte order reversed
    """
    s = "Error: Only 'unsigned' data of type 'int' or 'long' is allowed"
    if not ((type(data) == int)or(type(data) == long)):
        s1 = "Error: Invalid data type: %s" % type(data)
        print(''.join([s,'\n',s1]))
        return data
    if(data < 0):
        s2 = "Error: Data is signed. Value is less than 0"
        print(''.join([s,'\n',s2]))
        return data

    seq = ["0x"]

    while(data > 0):
        d = data & 0xFF     # extract the least significant(LS) byte
        seq.append('%02x'%d)# convert to appropriate string, append to sequence
        data >>= 8          # push next higher byte to LS position

    revD = int(''.join(seq),16)

    return revD

