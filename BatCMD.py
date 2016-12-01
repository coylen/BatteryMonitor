# Battery Monitor
# NRC V1.0

# Startup - import functionality
import pyb
import gc
import epaper
import time
from Battery import Battery, BatteryCurrentADC, testBattery
from Display import draw
#from BatCMD import CMDThread
from fram import FRAM, cp
from os import listdir, remove, sync


# Class to impliment command interface
# Based on command line interface which will ultimately be incorporated into
# a QT5 based interface

class BatCMD:

    def __init__(self, bat1, bat2):
        # need access to these functions to be able to access and change data
        self.bat1 = bat1
        self.bat2 = bat2
        self.stream = pyb.USB_VCP()
        self.data = ''
        self.stream_data = bytearray()
        # Dictionary of commands and corresponding functions
        # this method allows easy estention of commands
        self.commands = {'bat': self.batterycommands, 'sync': self.dumpbatterydata, 'time':self.setclock}

        #############################################################################################################
        # COMMAND LIST                                                                                              #
        #-----------------------------------------------------------------------------------------------------------#
        # bat batnumber cap AH - bat 1 cap 110 - set battery capacity to 110                                        #                                                                                      #
        #                                                                                                           #
        # bat batnumber current [% or AH] - bat 1 current 50% - bat 1 current 50                                    #
        #           - set battery charge level in % or AH                                                           #                                                                                                           #
        # sync [all/date] - sync all - sync 29/09/2016                                                              #
        #                                                                                                           #
        # time [read/set] [day/month/year hour:mins] - time set 29/09/2016 15:47 - time read                        #
        #                                                                                                           #
        # bat batnumber cal                                                                                         #
        #                                                                                                           #
        #############################################################################################################

    # function to read from VCP and process if end of line
    def Poll(self):
        while self.stream.any():
            self.stream_data.extend(bytearray(self.stream.readline()))
            print(self.stream_data[-1:])
            if self.stream_data[-1:] == b'\r':
                print('hit')
                self.decode(self.stream_data)


    def decode(self, data):
        com = str(data, 'utf-8').lower()
        command = com.split(' ')

        try:
            self.commands[command[0]](command[1:])
        except:
            # command not recognised
            print('FAIL')
        self.stream_data = bytearray()

        # TODO need to define command string to set options

        # # check for valid command
        # if command[0] == 'bat':
        #     # check for battery number and check valid
        #     if command[1].isdigit():
        #         b = int(command[1])
        #         if b == 1 or b == 2:
        #             # check for command option
        #             try:
        #                 self.commands[command[2]](self, b, com)
        #             except:
        #                 self.stream.write('command not recognised')
        #         else:
        #             self.stream.write('invalid battery')
        #     else:
        #         self.stream.write('invalid battery - number expected')
        # else:
        #     self.stream.write('command not recognised')

    # commands
    def batterycommands(self, data):
        batcommands = {'cap': self.setbatterycapacity, 'current': self.setbatterychargelevel}
        # checkformat
        self.debug(data)
        pass

    # Function to dump data to main program
    def dumpbatterydata(self, data):
        self.debug(data)
        pass

    def setclock(self,data):
        self.debug(data)
        pass

    def setbatterycapacity(self, bat, data):
        self.debug(data)
        pass

    def setbatterychargelevel(self, bat, data):
        self.debug(data)
        pass

    def debug(self,data):
        print(data)

def CMDThread(bat1, bat2):
    CMD = BatCMD(bat1, bat2)
    wf = Timeout(1)
    while True:
        CMD.Poll()
        yield wf()

def test():
    a=BatCMD(1,2)
    while True:
        a.Poll()
        print(a.stream_data)
        time.sleep(10)

