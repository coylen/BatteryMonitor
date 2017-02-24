# Battery Monitor
# NRC V1.0

# Startup - import functionality
import pyb
import gc
import epaper
from time import time, localtime
from Battery import Battery, BatteryCurrentADC, testBattery
from Display import draw
from BatCMD import BatCMD
from fram import FRAM, cp
from os import listdir, remove, sync


class Monitor:

    def __init__(self):
        # To avoid memory errors setup display ASAP and surround in garbabe collection to improvce chances
        gc.collect()
        disp = epaper.Display('R', mode=epaper.FAST)
        gc.collect()
        # Pass display to draw Class
        self.screen = draw(disp)
        #Create battery ADC interface
        currentADC = BatteryCurrentADC()
        # Initialise batteries can be test or normal
        #self.battery1 = testBattery(pyb.Pin.board.X11, currentADC, AfuncArg='chan 0_1',
        #                            initialcharge=100, batteryAH=100)
        #self.battery2 = testBattery(pyb.Pin.board.X12, currentADC, AfuncArg='chan 2_3',
        #                            initialcharge=100, batteryAH=100)
        self.mount_fram()
        try:
            Aoff1, Aoff2 = self.config()
        except:
            Aoff1 = 0
            Aoff2 = 0
            print('no config')

        self.battery1 = Battery(pyb.Pin.board.X12, currentADC, AfuncArg='chan 0_1',
                                initialcharge = 65, batteryAH = 100, Aoffset=Aoff1)

        self.battery2 =self.battery1

        # TODO: initialise CMD
        self.CMD = BatCMD(self.battery1, self.battery2)

        # initialse logger and file things up
        self.last_write = 0
        self.update()


    # Main functional loop of the program
    def run(self):
        self.screen.update(self.battery1, self.battery2)
        self.last_write = time()
        screen_timer = pyb.millis()

        while True:
            # Update battery data and screen every 10 seconds
            if pyb.elapsed_millis(screen_timer) > 10000:
                screen_timer = self.update()
                self.log_test()
                gc.collect()
                self.CMD.Poll()
            # TODO - check for command interface

    # Function to update battery data and screen
    def update(self):
        self.battery1.update()
        self.battery2.update()
        self.screen.update(self.battery1, self.battery2)
        screen_timer = pyb.millis()
        return screen_timer

    # Function to check if log is to be written
    # and if so write log and tidy files
    def log_test(self):
        current_time = time()
        if localtime(current_time)[4] % 15 == 0 and localtime(current_time - self.last_write)[4] > 5:
            # write log
            # get current filenames
            # note:adjust time by 5 minutes to ensure midnight appears on previous days log
            fn1, fn2 = self.filename(current_time - 300)
            self.check_files(fn1, fn2)
            self.write_log(fn1, self.battery1.log(current_time))
            self.write_log(fn2, self.battery2.log(current_time))
            self.last_write = current_time
        # TODO: remove debug sentence
            print('written to {}'.format(fn1))

    # Static function to determine filenames on the basis of current time
    @staticmethod
    def filename(ctime):
        tt = localtime(ctime)
        fn1 = "/fram/Bat1-{0}-{1}-{2}".format(tt[2], tt[1], tt[0])
        fn2 = "/fram/Bat2-{0}-{1}-{2}".format(tt[2], tt[1], tt[0])
        return fn1, fn2

    # Static function to write data to file
    @staticmethod
    def write_log(fn, data):
        with open(fn, 'a')as f:
            f.write(data)
        sync()

    # Static function to move old files out of fram and into logs folder of SD drive
    @staticmethod
    def check_files(fn1, fn2):
        ld = listdir('/fram')
        if len(ld) > 2:
            for f in ld:
                #ignore config file
                if f !='config':
                    fullname = '/fram/' + f
                    if fullname != fn1 and fullname != fn2:
                        # file not current so move
                        cp(fullname, '/sd/logs/')
                        remove(fullname)
                        sync()

    # Static function to mount fram drive at startup
    @staticmethod
    def mount_fram():
        i2c = pyb.I2C(1, pyb.I2C.MASTER)
        f = FRAM(i2c)
        try:
            pyb.mount(None, '/fram')
        except:
            pass
        pyb.mount(f, '/fram')

    # Function to setup Fram and read config file values for calibration
    def config(self):
        with open('/fram/config', 'r') as f:
            Aoff1 = f.readline()
            Aoff2 = f.readline()
        return float(Aoff1), float(Aoff2)

    def write_config(self, Aoff1, Aoff2):
        with open('/fram/config', 'w') as f:
            f.write("{0}\r\n".format(Aoff1))
            f.write("{0}\r\n".format(Aoff2))
        sync()
