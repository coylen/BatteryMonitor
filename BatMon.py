# Battery Monitor
# NRC V1.0

# Startup - import functionality
import pyb
import gc
import epaper
from time import sleep
from Battery import Battery, BatteryCurrentADC, testBattery
from Display import draw
from BatCMD import CMDThread


def run():
    gc.collect()
    # initialise display
    disp = epaper.Display(side,mode = epaper.FAST)
    gc.collect()
    # initialise ADC for current measurements
    screen = draw(disp)
    currentADC = BatteryCurrentADC()
    # initialise batteries
    battery1 = testBattery(pyb.Pin.board.X11, currentADC.read, AfuncArg='chan 0_1', initialcharge=100, batteryAH=100)
    battery2 = testBattery(pyb.Pin.board.X12, currentADC.read, AfuncArg='chan 2_3', initialcharge=100, batteryAH=100)
    # initialse CMD
    #cmd = CMDThread(battery1, battery2)
    # Setup scheduler
    screen.update(battery1, battery2)

    while True:
        battery1.update()
        battery2.update()
        screen.update(battery1, battery2)
        gc.collect()
        sleep(1)