# Battery Monitor
# NRC V1.0

# Startup - import functionality
from usched import Sched
import pyb
# from ADS1115 import ADS1115
from Battery import Battery, BatteryThread, BatteryCurrentADC
from Display import displayThread

def run():
    # initialise ADC for current measurements
    currentADC = BatteryCurrentADC()

    # initialise batteries
    battery1 = Battery(pyb.Pin.Y12, currentADC, AfuncArg='chan 0_1', initialcharge=100, batteryAH=100)
    BT1=BatteryThread(battery1)

    #initialise display
    disp = displayThread(battery1, battery1)

    # Setup scheduler
    objSched = Sched()
    objSched.add_thread(BT1)
    objSched.add_thread(disp)
    objSched.run()


# def test():
#     adc = ADS1115()
#     adc.setConfig(acqmode='contin', mux='chan 0_1')
#     #bat1 = Battery(bat1Vpin, bat1Afunc)
#     #bat1 = Battery(bat2Vpin, bat2Afunc)
#     # Main Loop
#     adc.startADCConversion()
#     while True:
#         #read Voltages
#         res = adc.readConversion()
#         print(res)
#         pyb.delay(500)
#
#
# def test2():
#     adc = ADS1115()
#     pga = [6144, 4096, 2048, 1024, 512, 256]
#     pgx = 1
#     adc.setConfig(acqmode='single',pga=pga[pgx], mux='chan 0_1')
#     #bat1 = Battery(bat1Vpin, bat1Afunc)
#     #bat1 = Battery(bat2Vpin, bat2Afunc)
#     # Main Loop
#     while True:
#         adc.startADCConversion()
#         #read Voltages
#         res = adc.readConversion()
#         print(res)
#         if res >= pga[pgx]:
#             print("overload")
#             if pgx>0:
#                 pgx-=1
#                 adc.setPGA(pga[pgx])
#                 print("range {0}".format(pga[pgx]))
#         if pgx < 5 and res<=pga[pgx+1]:
#             print("increase resolution")
#             pgx += 1
#             adc.setPGA(pga[pgx])
#             print("range {0}".format(pga[pgx]))
#         pyb.delay(5000)