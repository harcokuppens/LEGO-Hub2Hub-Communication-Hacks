import hub

# below needed otherwise scanning just does not work 
hub.config['hub_os_handle_bluetooth']=False
#default: hub.config['hub_os_handle_bluetooth']=True

from hub import light_matrix
from hub import button

import ubluetooth
import ustruct
import utime

from micropython import const



ble = ubluetooth.BLE()
transmission_id = None

#note: we skip hash, not really needed, and is computational intensive
signal_name_hash = 6533

_IRQ_SCAN_RESULT    = const(5)
_IRQ_SCAN_DONE    = const(6)

def receive_signal(duration_ms, callback):
    def _bt_irq(event, data):
        global transmission_id
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if adv_type == 0x02 and len(adv_data) >= 8 and adv_data[:3] == b'\xff\x03\x97':
                # 8 or bigger, because first 3 bytes is  manufacturer data of lego compagny
                #               then next byte is transmission id
                #               then hash in long (4 bytes)
                tid, hash = ustruct.unpack("<BL", adv_data[3:8])
                if tid != transmission_id:
                    #value = adv_data[8:].decode()
                    # IMPORTANT: we needed to add bytes below, because view on data doesn't support decode method!
                    value = bytes(adv_data[8:]).decode()
                    callback(hash, value, False)
                    transmission_id = tid
        elif event == _IRQ_SCAN_DONE:
            callback(None, None, True)

    # if we do not pass True as param, then we do not activate and gap_scan gives NO_DEV as error
    ble.active(True)
    ble.irq(_bt_irq)
    
    #ble.gap_scan(duration_ms, 10000, 10000)
    
    # NOTE: every 300 ms we increase the number and we send it repeatly every 100ms;
    #ble.gap_scan(duration_ms, 300000, 100000) 
    #  every 300 ms scan only 100 ms 
    #  with above scan we should get it every digit at least once  
    # 
    #ble.gap_scan(duration_ms, 10000, 10000)
    #  interval 0.01 second, window 0.01 second =>  scanning the whole time, so we should get it always immediately!
    ble.gap_scan(duration_ms, 1000000, 1000000)
    #  interval 1 second, window 1 second => scanning the whole time, so we should get it always immediately!
    
    # BLE.gap_scan(duration_ms, interval_us=1280000, window_us=11250, active=False, /)
    #   Run a scan operation lasting for the specified duration (in milliseconds).
    #   To scan indefinitely, set duration_ms to 0. To stop scanning, set duration_ms to None.
    #   Use interval_us and window_us to optionally configure the duty cycle. 
    #   The scanner will run for window_us microseconds every interval_us microseconds 
    #   for a total of duration_ms milliseconds. 
    #   The default interval and window are 1.28 seconds and 11.25 milliseconds respectively (background scanning).

def _callback(hash, value, done):
    if hash == signal_name_hash:
        light_matrix.write(value)
    if done:
        light_matrix.show_image(light_matrix.IMAGE_ASLEEP)
        utime.sleep_ms(1000)
        #wait_for_seconds(1)

        light_matrix.clear()


#receive_signal(10 * 10000, _callback)
receive_signal(0, _callback)
print("started program")
# note: ble.gap_scan call returns immediately, but starts scanning in background! 
#       even when program code is ended, the program on spike prime brick keeps running (until we press button to stop)
# note: even when program ends scanning continues, we must explictly stop scanning on end program!
#       todo: wait on middle button press to stop scanning and exit program!

#while not button.center.is_pressed():
while not button.pressed(button.LEFT):
   utime.sleep_ms(50)
   # make period short, so we have enough time to stop scan and print before default handler for center button kills program..

# print("end program", flush=True) -> only cpython, not mpython
#sys.stdout.flush() # not on mpython
print("end program")

ble.gap_scan(None)