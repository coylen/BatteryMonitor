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


# def run():
#     gc.collect()
#     # Initialise display
#     disp = epaper.Display('R',mode = epaper.FAST)
#     gc.collect()
#     # Initialise ADC for current measurements
#     screen = draw(disp)
#     currentADC = BatteryCurrentADC()
#     # Initialise batteries
#     battery1 = testBattery(pyb.Pin.board.X11, currentADC, AfuncArg='chan 0_1', initialcharge=100, batteryAH=100)
#     battery2 = testBattery(pyb.Pin.board.X12, currentADC, AfuncArg='chan 2_3', initialcharge=100, batteryAH=100)
#     # Initialize logger use I2C object from ADC?
#
#
#     # initialse CMD
#     #cmd = CMDThread(battery1, battery2)
#     # Setup scheduler
#     screen.update(battery1, battery2)
#     last_write = time.time()
#     screen_timer = pyb.millis()
#     current_time_tuple = time.localtime()
#     #TODO read last write from backup ram
#     if current_time_tuple[5] % 15 == 0:
#         pass
#         #TODO demo of method to do 15 minutes data
#
#
#     while True:
#         # Update battery data and screen every 10 seconds
#         if pyb.elapsed_millis(screen_timer) > 10000:
#             battery1.update()
#             battery2.update()
#             screen.update(battery1, battery2)
#             screen_timer = pyb.millis()
#
#         # check to see if ready to log
#         if battery1.write_flag and battery2.write_flag:
#             pass
#             write_data(battery1.log_message, battery2.log_message)
#             battery1.write_flag = False
#             battery2.write_flag = False
#
#         # check for command
#
#         # write data
#         # if 15 mins write data
#         # current_time = time.time()
#         # if check_for_write(current_time, last_write):
#         #     write_data(current_time)
#         #     last_write = time.time()
#
#         gc.collect()
#         # time.sleep(10)
#
# #TODO timer for refreash - 10s
# #TODO timer for battery update - 10s
# #TODO timer for write - 15mins
#
# #TODO consider rate of use AH/hour AH/day AH/total
#
# def check_for_write(current_time, last_write):
#     current_time_tuple = time.localtime(current_time)
#     #TODO read last write from backup ram
#     if current_time_tuple[5] % 15 == 0 and current_time - last_write > 100:
#         return True
#     else:
#         return False
#
# def write_data(msg1,msg2):
#     print(msg1, msg2)
#     pass

#####################################################################################################################
##                       REIMPLIMENT                                    ############################
##################################################################################################
class monitor:

    def __init__(self):
        gc.collect()
        disp = epaper.Display('R', mode=epaper.FAST)
        gc.collect()
        self.screen = draw(disp)
        currentADC = BatteryCurrentADC()
        # Initialise batteries
        self.battery1 = testBattery(pyb.Pin.board.X11, currentADC, AfuncArg='chan 0_1', initialcharge=100, batteryAH=100)
        self.battery2 = testBattery(pyb.Pin.board.X12, currentADC, AfuncArg='chan 2_3', initialcharge=100, batteryAH=100)
        # initialise CMD

        # initialse logger
        self.last_write = 0
        self.update()
        self.mount_fram()

    def filename(self, ctime):
        tt = time.localtime(ctime)
        fn1 = "/fram/Bat1-{0}-{1}-{2}".format(tt[2], tt[1],tt[0])
        fn2 = "/fram/Bat2-{0}-{1}-{2}".format(tt[2], tt[1],tt[0])
        return fn1, fn2

    def run(self):
        self.screen.update(self.battery1, self.battery2)
        self.last_write = time.time()
        screen_timer = pyb.millis()
#        self.current_time_tuple = time.localtime()
        # TODO read last write from backup ram
#        if current_time_tuple[5] % 15 == 0:
#            pass
            # TODO demo of method to do 15 minutes data

        while True:
            # Update battery data and screen every 10 seconds
            if pyb.elapsed_millis(screen_timer) > 10000:
                screen_timer = self.update()
                self.log_test()
                gc.collect()

    def update(self):
        self.battery1.update()
        self.battery2.update()
        self.screen.update(self.battery1, self.battery2)
        screen_timer = pyb.millis()
        return screen_timer

    def log_test(self):
        current_time = time.time()
        if time.localtime(current_time)[4] % 15 == 0 and time.localtime(current_time - self.last_write)[4] > 5:
        #write log
            #get current filenames
            fn1, fn2 = self.filename(current_time)
            if self.check_files(fn1,fn2):
                self.battery1.new_day()
                self.battery2.new_day()
            self.write_log(fn1, self.battery1.log(current_time))
            self.write_log(fn2, self.battery2.log(current_time))
            self.last_write = current_time
            print('written to {}'.format(fn1))

    @staticmethod
    def write_log(fn,data):
        with open(fn,'a')as f:
            f.write(data)
        sync()

    @staticmethod
    def check_files(fn1,fn2):
        new_day = False
        ld = listdir('/fram')
        if len(ld) > 2:
            for f in ld:
                fullname ='/fram/'+f
                if fullname != fn1 and fullname != fn2:
                    #file not current so move
                    monitor.move_files(fullname)
            new_day = True
        return new_day




    @staticmethod
    def move_files(fn):
        cp(fn,'/sd/logs/')
        remove(fn)
        sync()


    @staticmethod
    def mount_fram():
        i2c = pyb.I2C(1, pyb.I2C.MASTER)
        f = FRAM(i2c)
        try:
            pyb.mount(None,'/fram')
        except:
            pass
        pyb.mount(f, '/fram')

