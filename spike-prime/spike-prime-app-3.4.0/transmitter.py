import hub
#hub.config['hub_os_handle_bluetooth']=True

from hub import button
import ustruct

import ubluetooth
import utime

def make_crc_table():
    crc_table=None
    if crc_table:
        return
    crc_table = [0] * 256
    for i in range(256):
        c = i
        for j in range(8):
            if c & 1:
                c = 0xEDB88320 ^ (c >> 1)
            else:
                c = c >> 1
        crc_table[i] = c
    return crc_table


crc_table = make_crc_table()

def crc32(buf):
    global crc_table
    c = 0xFFFFFFFF
    l = len(buf)
    for i in range(l):
        c = crc_table[(c ^ buf[i]) & 0xFF] ^ (c >> 8)
    return c ^ 0xFFFFFFFF


ble = ubluetooth.BLE()
ble.active(True)
utime.sleep_ms(500)

count = 0
signal_name_hash = crc32('ABC'.encode())

def transmit_signal(transmission_id, ahash, value):
    transmission_id = transmission_id & 0xff
    header = ustruct.pack('<BBBBL', 0xff, 0x03, 0x97, transmission_id, ahash)
    data = header + value.encode()[:23]
    
    ble.gap_advertise(100000, adv_data=data, connectable=False)
    utime.sleep_ms(500)
    ble.gap_advertise(None)
    

while True:
    #Wait for the left button to be pressed
    while not button.pressed(button.LEFT):
        pass
    transmit_signal(count, signal_name_hash, str(count))
    count += 1
 
# problem: when ble.gap_advertise gets called the brick crashes! (stops, and need to start a new) 
#  IDEAS:
#     1) in repl with rshell then ble.gap_advertise does not crash?
#         -> maybe it misses some import?? -> do more imports
#
#     2) maybe bug in this specific version -> try other version
#          https://education.lego.com/nl-nl/downloads/spike-app/software/
#          https://education.lego.com/en-us/downloads/spike-app/software/
#                SPIKE App 3.4.0 Release Notes
#                SPIKE App 3.3.1 Release Notes
#                SPIKE App 3.3.0 Release Notes -> first official python (by default enabled)
#                SPIKE App 3.2.4 Release Notes -> first python experimental (by default disabled)
#          https://education.lego.com/en-us/
#              https://assets.education.lego.com/_/downloads/SPIKE_APP_3_macOS__3.2.4_Global.dmg
#              https://assets.education.lego.com/_/downloads/SPIKE_APP_3_macOS__3.3.0_Global.dmg
#              https://assets.education.lego.com/_/downloads/SPIKE_APP_3_macOS__3.3.1_Global.dmg
#              https://assets.education.lego.com/_/downloads/SPIKE_APP_3_macOS__3.4.0_Global.dmg
#
# #            https://github.com/bricklife/LEGO-Hub2Hub-Communication-Hacks
#
#              LEGO MINDSTORMS Robot Inventor's Hub to Hub Communication is implemented on Bluetooth LE (BLE) Advertising.
#
#               For example, when a hub transmits a signal named "ABC" with a value "123", some INVALID advertising packets will be sent
#               as follows:
#
#
#
#                MicroPython v1.12 scripts for SPIKE Prime Hub OS 3.1.21.9    => 3.1 version of spike app ???
#
#                   Transmitter program: spike-prime/transmitter.py
#                   Receiver program: spike-prime/receiver.py
#     
#     3)  -> try linux/rpi code -> get it to work?
#              if working, then send from linux receiver in brick ?
#    
#     => GENERAL: learn BLE better and better understand what code really is doing!!

# below is debugging code       
# data = b'\xff\x03\x97\x00H\x03\x83\xa3\x00'
# while True:
#     #Wait for the left button to be pressed
#     while not button.pressed(button.LEFT):
#         pass
#    #utime.sleep_ms(500)
#     data = b'\xff\x03\x97\x00H\x03\x83\xa3\x00'
#     #x="dfsd"
#
#     #ble.gap_advertise(200000, adv_data=data,resp_data=data, connectable=True)
# #    try:
#     ubluetooth.BLE().gap_advertise( adv_data=data,connectable=False)
#     # except:
#     #   pass
#       #print("An exception occurred")
#     #transmit_signal(count, signal_name_hash, str(count))
#     count += 1
    