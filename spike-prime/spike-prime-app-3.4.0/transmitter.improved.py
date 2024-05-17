import hub
#hub.config['hub_os_handle_bluetooth']=True

# below line fixes crash when calling ble.gap_advertise. -> this spike 3 transmit code works!  -> receiver on spike 2 cooperates with it!
#                                                           but  sender on spike 2 , with receiver on spike 3 does not work??
hub.config['hub_os_handle_bluetooth']=False

from hub import light_matrix

from hub import button
import ustruct

import ubluetooth
import utime


ble = ubluetooth.BLE()
ble.active(True)
utime.sleep_ms(500)

count = 0

#signal_name_hash = crc32('ABC'.encode())
#note: we skip hash, not really needed, and is computational intensive
signal_name_hash = 6533

def transmit_signal(transmission_id, ahash, value):
    transmission_id = transmission_id & 0xff
    header = ustruct.pack('<BBBBL', 0xff, 0x03, 0x97, transmission_id, ahash)
    
    data = header + value.encode()[:23]
    #       8     +  max 23 bytes  => max 31 bytes in adv_data
    ble.gap_advertise(100000, adv_data=data, connectable=False)
    utime.sleep_ms(300)
    ble.gap_advertise(None)
    

while True:
    # #Wait for the left button to be pressed
    # while not button.pressed(button.LEFT):
    #     pass
    light_matrix.write(str(count))
    transmit_signal(count, signal_name_hash, str(count))
    count += 1
    count = count%10
 
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
    