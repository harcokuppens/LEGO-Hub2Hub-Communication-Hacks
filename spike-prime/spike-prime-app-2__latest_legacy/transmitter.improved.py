from spike import PrimeHub
import ubluetooth
import ustruct
import utime


hub = PrimeHub()
ble = ubluetooth.BLE()

count = 0

#signal_name_hash = crc32('ABC'.encode())
#note: we skip hash, not really needed, and is computational intensive
signal_name_hash = 6533

def transmit_signal(transmission_id, hash, value):
    transmission_id = transmission_id & 0xff
    header = ustruct.pack('<BBBBL', 0xff, 0x03, 0x97, transmission_id, hash)
    data = header + value.encode()[:23]

    ble.gap_advertise(100000, adv_data=data, connectable=False)
    # BLE.gap_advertise(interval_us, adv_data=None, *, resp_data=None, connectable=True)
    #   Starts advertising at the specified interval (in microseconds). 
    #   This interval will be rounded down to the nearest 625us. To stop advertising, set interval_us to None.
    # => every 0.1 second advertises 
    utime.sleep_ms(300)
    ble.gap_advertise(None)
    # => advertising for duration of 0.3 seconds (every 0.1second a message -> 2 or 3 messages send)

while True:
    #hub.left_button.wait_until_pressed()
    #print(count)
    hub.light_matrix.write(str(count))
    transmit_signal(count, signal_name_hash, str(count))
    count += 1
    count = count%10