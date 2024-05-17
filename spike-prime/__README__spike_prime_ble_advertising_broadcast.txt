
SHORT: look at 

    spike-prime/spike-prime-app-2__latest_legacy/*.improved.py
    
    spike-prime/ spike-prime-app-3.4.0/*.improved.py


NOTE:  
   to test brick code, you could
   
     run working bluetooth code on  spike 2   to test new software on spike 3
     or                            linux pc
                                     `-> note: pc code works only on linux
                                              because pybluez only supports BLE
                                              experimentally for linux!
                                              see: ../python_bluetooth_low_energy/  


 https://docs.micropython.org/en/latest/library/bluetooth.html#bluetooth.BLE.gap_advertise
     adv_data and resp_data can be any type that implements the buffer protocol
     
     
     ble active scan vs passive scan
       https://pressbooks.bccampus.ca/iotbook/back-matter/appendix-a/#:~:text=In%20passive%20scanning%2C%20a%20scanner,request%20packet%20to%20the%20advertiser.
        
        In passive scanning, a scanner receives advertisement messages, but does not send any packet to the advertiser, while
        in active scanning, the scanner listens to advertisement messages and after receiving an advertisement message, it
        sends a scan request packet to the advertiser.
        
        => we keep to simple sending data, and receiver can fetch latest needed
        
        
      so 
       1. fetch sensor data.  -> takes time. -> how much?     => need profiling
       2. send data   -> how often do we repeat sending?
       3. receiver receives data, only on new data it takes action
       
       
       in counter example we send a number 2 a 3 times    
       because  
         advertising interval is 100000us -> 100 ms
         we advertise only for 300 ms  -> then we switch to next number
       so receiver has 2 a 3 shots to receive the data
       
        => hmmm. adapt receive program to show number of received packages for specific trans id!
       
       => hmmm... what happens if we only advertise for 100 ms?  a single package always send?
           does the advertiser send already at 1th ms ?  does 1 ms also work? TODO: test
           REASON: if one advertised package already is guaranteed received because bricks are close
                   then no need to send more often.
                   NOTE: in test setup we only have 1 robot with 2 bricks, but in practical situation 
                         we could have multiple robots which could interfere each others sending
                         -> so could work in lab but not in practice!
                         => tuning in practice needed
                         
        => less advertising  does interrupt the receiver less!! -> more time for other things on receiver!         
        
        
         
     
 send 
     
     def transmit_signal(transmission_id, ahash, value):
         transmission_id = transmission_id & 0xff
         header = ustruct.pack('<BBBBL', 0xff, 0x03, 0x97, transmission_id, ahash)
                                   `-> 8 bytes in total (each B 1 byte, and L 4 bytes)
         data = header + value.encode()[:23] 
                  8bytes   max 23 bytes (index 0 till 22 excluding index 23). -> total of 31 bytes
         ble.gap_advertise(100000, adv_data=data, connectable=False)               -> immmediately returns
         utime.sleep_ms(300)
         ble.gap_advertise(None)                                                   -> immmediately returns
         
         
        => with cooperative scheduling with coroutines we could improve this with
           during advertising we can fetch sensor data 
         
         
 receive        
    def receive_signal(duration_ms, callback):
        def _bt_irq(event, data):
            global transmission_id
            if event == _IRQ_SCAN_RESULT:
                addr_type, addr, adv_type, rssi, adv_data = data
                if adv_type == 0x02 and len(adv_data) >= 8 and adv_data[:3] == b'\xff\x03\x97':
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
    
        ble.gap_scan(duration_ms, 1000000, 1000000)     
   
   
   
   
https://docs.micropython.org/en/latest/library/bluetooth.html#bluetooth.BLE.gap_scan

   BLE.gap_scan(duration_ms, interval_us=1280000, window_us=11250, active=False, /) 

           Run a scan operation lasting for the specified duration (in milliseconds).

           To scan indefinitely, set duration_ms to 0.

           To stop scanning, set duration_ms to None.

           Use  interval_us  and  window_us  to optionally configure the duty cycle. The scanner will run
           for  window_us  microseconds every  interval_us  microseconds for a total of  duration_ms  milliseconds.
           The default interval and window are 1.28 seconds and 11.25 milliseconds respectively (background
           scanning).

           For each scan result the _IRQ_SCAN_RESULT event will be raised, with event
           data  (addr_type,addr,adv_type, rssi, adv_data).

               addr_type values indicate public or random addresses:

                * 0x00 - PUBLIC

                * 0x01 - RANDOM (either static, RPA, or NRPA, the type is encoded in the address itself)

               adv_type values correspond to the Bluetooth Specification:

                * 0x00 - ADV_IND - connectable and scannable undirected advertising

                * 0x01 - ADV_DIRECT_IND - connectable directed advertising

                * 0x02 - ADV_SCAN_IND - scannable undirected advertising                   => what we use!!

                * 0x03 - ADV_NONCONN_IND - non-connectable undirected advertising

                * 0x04 - SCAN_RSP - scan response

           active can be set True if you want to receive scan responses in the results.     => we user False -> no response

           When scanning is stopped (either due to the duration finishing or when explicitly stopped),
           the _IRQ_SCAN_DONE event will be raised.
           
           

References

   Visible links
   . Link to this definition
	https://docs.micropython.org/en/latest/library/bluetooth.html#bluetooth.BLE.gap_scan
   
     
length missing in example
--------------------------

 in https://github.com/NStrijbosch/RevEng-hub2hub-word-blocks
 and in Digi_MicroPython_programming_guide.pdf
 they say first byte should be length in advertising package
 however in example code 'transmitter.py' it is missing,
 where in receiver.py code they just do:
   value = adv_data[8:].decode()
 so assuming adv_data has some ending automatically at right place...
 
QUESTIONS:
  1. does it still work if I had length byte?
  2. if missing length byte is not a problem, can I choose any from of data myself? 
     just ignoring the whole advertising protocol as a whole??
      -> eg. see what happens if you remove also the manufacturing bytes of lego

ANSWER: 

  https://docs.micropython.org/en/latest/library/bluetooth.html#bluetooth.BLE.gap_advertise
     BLE.gap_advertise(interval_us,**adv_data=None,***,**resp_data=None,**connectable=True)**

             Starts advertising at the specified interval (in microseconds). This interval will be rounded down to the
             nearest 625us. To stop advertising, set interval_us to None.

             adv_data and resp_data can be any type that implements the buffer protocol
             (e.g. bytes, bytearray, str). adv_data is included in all broadcasts, and resp_data is send in
             reply to an active scan.

             Note: if adv_data (or resp_data) is None, then the data passed to the previous call
             to gap_advertise will be reused. This allows a broadcaster to resume advertising with
             just gap_advertise(interval_us). To clear the advertising payload pass an empty bytes, i.e. b''.

  => adv_data can be any type that implements the buffer protocol
     (e.g. bytes, bytearray, str).

   THUS free to choose format in adv_data !!  However one limit survives: max length is 31 bytes!
                                                -> they forgot to mention this size limit in https://docs.micropython.org/
                                                    but mentioned in 'Digi_MicroPython_programming_guide.pdf  (XBee device)'
    
    examples of different format adv_data:                                                
      lego graphical block in old Mindstorms retail app used format https://github.com/NStrijbosch/RevEng-hub2hub-word-blocks
      xbee uses format specified in Digi_MicroPython_programming_guide.pdf

https://github.com/NStrijbosch/RevEng-hub2hub-word-blocks

Reverse Engineering the Hub to Hub Word Blocks of the LEGO MINDSTORMS Robot Inventor (51515)
The hub to hub communication blocks exploit the Bluetooth Low Energy (BLE) capabilities of the MINDSTORMS Hubs

The protocol is based on broadcasting data in the advertisement data similar to Beacons.

When transmitting data using the wordblock: transmit block: hub transmit signal signal111 with abcd the hub starts advertising the following data

0x0C, 0xFF, 0x97, 0x03, 0x01, 0x1D, 0xC6, 0x73, 0x49, 0x61, 0x62, 0x63, 0x64
  ^     ^     ^     ^     ^     ^     ^     ^     ^     ^
  |     |     |_____|     |     |_________________|     |_________________
  |     |     |           |     |                     ASCII string containing transmitted data (number of bytes depends on the length of the transmitted data, the maximum is 23 bytes)
  |     |     |           |    Signal name encoded as a CRC32 hash                                                                                                (prefix is 9 bytes) => 32 bytes together
  |     |     |         Index of the message                                                                                                                     Digi_MicroPython_programming_guide.pdf
  |     |     LEGO Company identifier                                                                                                                               says adv_data is max 31 bytes
  |     Indicating manufacturer data
  Length (number of bytes that follow, not including this one)
  
  
  

Digi_MicroPython_programming_guide.pdf  (XBee device)

 SHORT: <adv_data> should consist of one or more Advertising Data (AD) elements

 page 105
   
   
 
   gap_advertise()

     Start or stop GAP advertisements from the XBee device.

         ble.gap_advertise(interval_us, adv_data=None)

     <interval_us>

         Start advertising at the specified interval, in microseconds. This value will be rounded down to the nearest
         multiple of 625 microseconds. The interval, if not None, must be at least 20,000 microseconds (20 milliseconds)
         and no larger than approximately 40.96 seconds (40,959,375 microseconds).

         To stop advertising, set <interval_us> to None. 
     
     <adv_data>

         This is the payload that will be included in GAP advertisement broadcasts. <adv_data> can be a bytes or bytearray
         object up to 31 bytes in length, or None.
                ^^^^^^^^^^^^^^^^^^^^^^^^
                
         If <adv_data> is empty--for example b''--then GAP advertising will return to the default XBee behavior, which is
         to advertise the product name--such as XBee3 Zigbee, or the value in ATBI.



         If <adv_data> is None or not specified, then the data passed to the previous call to gap_advertise is used, unless
         there was no previous call or the previous data was empty, in which case the behavior will be as if an empty
         value--b''--was passed.

         Otherwise, <adv_data> should consist of one or more Advertising Data (AD) elements, as defined in the Bluetooth
         Core Specification Supplement, Part A Section 1.
         
         
          * Each AD element consists of a length byte, a data type byte, and one or more bytes of data. The length byte
            indicates how long the rest of the element is, for example a Complete Local Name element with value My XBee
            would have a length byte 0x08 - 1 byte for type plus 7 bytes for the value.
              -> take data (without lengt byte, only type and data), calculate length, then prepend length byte!

          * The Bluetooth SIG provides the list of defined Advertising Data element types here:
            https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
         
         Be aware that <adv_data> must be formatted as one or more Advertising Data elements in order to be interpreted
         as a valid Bluetooth Low Energy advertisement by other devices. For example, to advertise the name My XBee:
           
           ble.gap_advertise(200000, b"\x08\x09My XBee")
           
           
           
         notes:
            - first byte is length:  "My XBee"   has length 7 and together with the data type byte the total lenght is 8  
            - second byte is type: 
               from src: https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf?v=1705709926908
                   type 0x09 :  Complete Local Name
                   
  
  
  
           
https://github.com/bricklife/LEGO-Hub2Hub-Communication-Hacks


code
 * raspberry 
    -> use pybluez 
 * spike prime ( board with micropython )
    -> uses micropython's own bluetooth api for BLE 


How to transmit a signal by hcitool

    $ sudo hcitool -i hci0 cmd 0x08 0x0006 a0 00 a0 00 02 00 00 00 00 00 00 00 00 07 00
    $ sudo hcitool -i hci0 cmd 0x08 0x0008 0b ff 03 97 01 48 03 83 a3 31 32 33                  <- send 
    $ sudo hcitool -i hci0 cmd 0x08 0x000a 01
    ...
    $ sudo hcitool -i hci0 cmd 0x08 0x000a 00

Ref. Bluetooth Core Specification Version 5.3, Vol 4, Part E, 7.8 LE Controller Commands
  => Core_v5.3.pdf


  hcitool only linux!
    -> on macos use bleak
    
        https://koen.vervloesem.eu/blog/develop-your-own-bluetooth-low-energy-applications/
         https://github.com/koenvervloesem/bluetooth-low-energy-applications/blob/main/3-advertisements/bleak/scanner.py
          -> scanner , but not a sender ..


    Data structure

        FF 03 97 01 48 03 83 A3 31 32 33

   +-----------------------------------------------------------------------------------------------------+
      |    Bytes    |                    Meaning                    |                 Note                  |
      |-------------+-----------------------------------------------+---------------------------------------|
3     | FF 03 97    | Fixed header                                  |                                       |
      |-------------+-----------------------------------------------+---------------------------------------|
2     | 01          | Transmission ID (0x00**-**0xff)               | MUST be changed for each transmission |
      |-------------+-----------------------------------------------+---------------------------------------|
4     | 48 03 83 A3 | Signal name hash = CRC32("ABC") =**0xA3830348 |                                       |
      |-------------+-----------------------------------------------+---------------------------------------|
<=23  | 31 32 33    | Value =**"123"                                | Max 23 bytes                          |
       +-----------------------------------------------------------------------------------------------------+

total <=31 bytes


  -> no length byte at beginning!!! -> forgot? 
  
  
https://community.thunkable.com/t/ble-receive-arduino-ide-vs-micropython/2530372


    name = bytes(self.name, 'UTF-8')
    adv_data = bytearray(b'\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
    self.ble.gap_advertise(100, adv_data)
    
    -> OK: bytearray((len(name) + 1, 0x09)) + name  
            lenth over data(name) and type(+1)  then type and name concated -> OK
            
      BUT what is prefix     b'\x02\x01\x02' ???    

https://github.com/digidotcom/xbee-micropython/blob/master/samples/bluetooth/gap_advertise/main.py

  def form_adv_name(name):
      payload = bytearray()
      payload.append(len(name) + 1)    -> length over data + type(+1)!           OK
      payload.append(0x08)            -> type
      payload.extend(name.encode())
      return payload
      
  # Turn on Bluetooth
  ble.active(True)
  print("Started Bluetooth with address of: {}".format(form_mac_address(ble.config("mac"))))

  payload = form_adv_name("My custom advertisement name")

  print("Advertising payload: {}".format(payload))
  # Advertise the new local name with an interval of 100000 microseconds (0.1 seconds).
  ble.gap_advertise(100000, payload)
        
      

https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_advertising.py


 def _append(adv_type, value):
     nonlocal payload
     payload += struct.pack("BB", len(value) + 1, adv_type) + value
                                     `-> length over data + type(+1)!               OK
           

https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf?v=1705709926908


Common Data Type       NAME                                  Reference
--------------------------------------------------------------------------------
0xFF                 Manufacturer Specific Data           Core Specification Supplement, Part A, Section 1.4


https://www.bluetooth.com/specifications/specs/core-specification-supplement-9/


    1.4 MANUFACTURER SPECIFIC DATA 1.4.1 Description

    The Manufacturer Specific data type is used for manufacturer specific data. The first two
    data octets shall contain a company identifier from Assigned Numbers. The interpretation of
    any other octets within the data shall be defined by the manufacturer specified by the
    company identifier.

      Data Type.                               Description
      --------------------------------------------------------------------------------
       «Manufacturer Specific Data».            Size: 2 or more octets The first 2 octets
                                                contain the Company Identifier Code followed by
                                                additional manufacturer specific data
  
  

===================


spike 2
-------


latest 'spike app 2' ("SPIKE Legacy.app") has after updating hub os:    

  hub os:  4.0.0.7
  micropython: v1.14-876-gfbecba865 on 2021-05-04
   `-> comparable with cpython 3.4.0 
   
   
   the code in spike-prime/ folder didn't work on the latest spike 2 version,
   however you only needed to fix one line in receiver.py
   
    change      
     value = adv_data[8:].decode()
    to  
     value = bytes(adv_data[8:]).decode()
     
    then it works!
    
  However I made an improved version in
          
         spike-prime/spike-prime-app-2__latest_legacy/
         
         
spike 3
-------          

   the spike 3 app has a new python api for the spike prime,
   however the micropython api is offcourse still simular.
   
   I had to rewrite the code in spike-prime/ folder 
   to make it work on on the spike 3 firmware.
   The result is in :
   
      spike-prime-app-3.4.0/
      
    unfortunately there is a bug in the firmware causing the spike to 
    crash when calling   
    
         ble.gap_advertise(100000, adv_data=data, connectable=False)
         
    in transmitter.py . 
    I also tried the firmware of the spike prime 3.3.1 app. But that had the same problem!
    
    => note: I'm sure the code is right because similar code is run in spike 2 app's firmware!
    
    
    I also implemented a simplified version (with .improved.py extension) which does use
    a fixed hash not calculated from a string. (same improvement as done for spike2 code!)
    
    
    SOLUTION:
      wait for new firmware which fixes the problem!!     