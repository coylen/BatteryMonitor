import os
import pyb

def seefilesystem():
    with open('/sd/boot.py', mode='w') as f:
        f.write('import pyb\n')
        f.write('pyb.usb_mode(\'CDC+MSC\')\n')
    os.sync()

def hidefilesystem():
    with open('/sd/boot.py', mode='w') as f:
        f.write('import pyb\n')
        f.write('pyb.usb_mode(\'CDC+HID\')\n')
    os.sync()

def reset():
    pyb.hard_reset()
