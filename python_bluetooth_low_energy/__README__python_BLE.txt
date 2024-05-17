simplepyble
-----------
alternative for  pybluez BLE:  https://simpleble.readthedocs.io/en/latest/

  pip3 install simplepyble

 docs: https://simpleble.readthedocs.io/en/latest/

 
pybluez    -> BLE experimental support only for linux
--------

des/spike_hub/api/official_lego_firmware_spike_prime/hub2hub/LEGO-Hub2Hub-Communication-Hacks/raspberry-pi/hub2hub.py 

does

  import bluetooth._bluetooth as bluez
  
  bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS, param)
                                           --
                                            `-> low energy. => use BLE

bluetooth module comes from pybluez package
 
  https://github.com/pybluez/pybluez     -> not under active development
    IMPORTANT: it says:
    
      This project is not under active development. Contributions are strongly desired to resolve compatibility problems on newer
      systems, address bugs, and improve platform support for various features.
      
      
info over hci_send_cmd
    https://people.csail.mit.edu/albert/bluez-intro/x682.html
 
     BlueZ provides a number of other socket types. The most useful of these is the Host Controller Interface (HCI) socket, which
    provides a direct connection to the microcontroller on the local Bluetooth adapter. This socket type, introduced in section Section
    4.1, can be used to issue arbitrary commands to the Bluetooth adapter. Programmers requiring precise control over the Bluetooth
    controller to perform tasks such as asynchronous device discovery or reading signal strength information should use HCI sockets.
 
    The Bluetooth Core Specification describes communication with a Bluetooth microcontroller in great detail, which we summarize here.
    The host computer can send commands to the microcontroller, and the microcontroller generates events to indicate command responses
    and other status changes. A command consists of a Opcode Group Field that specifies the general category the command falls into, an
    Opcode Command Field that specifies the actual command, and a series of command parameters. In BlueZ, hci_send_cmd is used to
    transmit a command to the microcontroller.

       int hci_send_cmd(int sock, uint16_t ogf, uint16_t ocf, uint8_t plen, 
                      void *param);
 
    Here, sock is an open HCI socket, ogf is the Opcode Group Field, ocf is the Opcode Command Field, and plen specifies the length of
    the command parameters param.

    Calling read on an open HCI socket waits for and receives the next event from the microcontroller. An event consists of a header
    field specifying the event type, and the event parameters. A program that requires asynchronous device detection would, for
    example, send a command with ocf of OCF_INQUIRY and wait for events of type EVT_INQUIRY_RESULT and EVT_INQUIRY_COMPLETE. The
    specific codes to use for each command and event are defined in the specifications and in the BlueZ source code.
 





pybluez  install 
----------------

pybluez 
 - for classic bluetooth: supported on  linux,mac,windows
 - for BLE :  only experimental support on linux
 
     BLE (bluetooth low energy) is experimental and only supported on linux
        https://github.com/pybluez/pybluez/blob/master/docs/install.rst
    
         For experimental Bluetooth Low Energy support (only for Linux platform - for additional dependencies please take look at: ble-dependencies)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^           ^^^^^^^^^^^^^                                                       `-> https://github.com/oscaracena/pygattlib/blob/master/DEPENDS
             pip install pybluez[ble]
     
 
note: project unmaintained at the moment


 
 $ pip3.10 install pybluez
 Collecting pybluez
   Using cached PyBluez-0.23.tar.gz (97 kB)
   Installing build dependencies ... done
   Getting requirements to build wheel ... error
   error: subprocess-exited-with-error

   × Getting requirements to build wheel did not run successfully.
   │ exit code: 1
   ╰─> [1 lines of output]
       error in PyBluez setup command: use_2to3 is invalid.
       [end of output]                 ^^^^^^^^^^^^^^^^^^^

   note: This error originates from a subprocess, and is likely not a problem with pip.
 error: subprocess-exited-with-error

 × Getting requirements to build wheel did not run successfully.
 │ exit code: 1
 ╰─> See above for output.

 note: This error originates from a subprocess, and is likely not a problem with pip.
 
 
solution from https://stackoverflow.com/questions/75818465/pybluez-error-in-pybluez-setup-command-use-2to3-is-invalid
 
 pip3.10 install git+https://github.com/pybluez/pybluez.git#egg=pybluez
 pip3.10 install setuptools
 
 >> import bluetooth._bluetooth as bluez
 Traceback (most recent call last):
   File "<stdin>", line 1, in <module>
 ModuleNotFoundError: No module named 'bluetooth._bluetooth'
 
   https://github.com/hexway/apple_bleee/issues/3
     Use Linux. Bluez is not supported under macOS as far as I know
 
   https://github.com/pybluez/pybluez/blob/master/docs/install.rst
    
    For experimental Bluetooth Low Energy support (only for Linux platform - for additional dependencies please take look at: ble-dependencies)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^           ^^^^^^^^^^^^^                                                       `-> https://github.com/oscaracena/pygattlib/blob/master/DEPENDS
        pip install pybluez[ble]
        
        
     https://github.com/oscaracena/pygattlib/blob/master/DEPENDS
        pkg-config
        libboost-python-dev
        libboost-thread-dev
        libbluetooth-dev
        libglib2.0-dev
        python3-dev
 
   https://stackoverflow.com/questions/23985163/python3-error-no-module-named-bluetooth-on-linux-mint
   
   for linux do: 
     sudo apt-get install bluetooth libbluetooth-dev
     sudo python3 -m pip install pybluez
     
     
 
