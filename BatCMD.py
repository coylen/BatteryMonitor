#  class to read commands into the battery monitor and action their results
#  acceptable commands
#  bat (battery number) (cap, current) (value)
import pyb
from usched import Timeout


class BatCMD:

    def __init__(self, bat1, bat2, uart=2, baudrate=9600):
        self.bat1 = bat1
        self.bat2 = bat2
        self.stream = pyb.UART(uart, baudrate)
        self.data = ''
        self.commands = {'cap': self.setbatterycapacity, 'current': self.setbatterychargelevel,
                         'dump': self.dumpbatterydata}

    def Poll(self):
        if self.stream.any():
            stream_data = self.stream.readline()
            self.decode(stream_data)

    def decode(self, data):
        com = str(data).lower()
        command = command.split(' ')

        # check for valid command
        if command[0] == 'bat':
            # check for battery number and check valid
            if command[1].isdigit():
                b = int(command[1])
                if b == 1 or b == 2:
                    # check for command option
                    try:
                        self.commands[command[2]](self, b, com)
                    except:
                        self.stream.write('command not recognised')
                else:
                    self.stream.write('invalid battery')
            else:
                self.stream.write('invalid battery - number expected')
        else:
            self.stream.write('command not recognised')

    # commands
    def setbatterycapacity(self, bat, data):
        pass

    def setbatterychargelevel(self, bat, data):
        pass

    def dumpbatterydata(self, bat, data):
        pass


def CMDThread(bat1, bat2):
    CMD = BatCMD(bat1, bat2)
    wf = Timeout(1)
    while True:
        CMD.Poll()
        yield wf()
