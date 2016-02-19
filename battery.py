import pyb
from usched import Timeout
from ADS1115 import ADS1115

class Battery:

    def __init__(self, Vpin, Afunc, AfuncArg='chan 0_1', initialcharge=100, batteryAH=110):
        self.initialcharge = initialcharge
        self.AHCapacity = batteryAH
        # Setup PINS
        self.voltage_adc = pyb.ADC(Vpin)
        self.Afunc = Afunc
        self.AfuncArg = AfuncArg
        self.V = 0
        self.A = 0
        self.AH = 0
        self.capacityV = 0
        self.capacityAH = 0
        self.delta = False
        self.BatteryVoltCurve = [(100, 12.6), (90, 12.5), (80, 12.42), (70, 12.32),
                                 (60, 12.2), (50, 12.06), (40, 11.9), (30, 11.75),
                                 (20, 11.58), (10, 11.31), (0, 10.5)]
        # start timer
        self.start = pyb.millis()

    def voltage(self):
        # Read Voltage
        v = self.voltage_adc.read() / 4095 *18.3
        self.V = v

    def current(self):
        # Read current
        a = self.Afunc(self.AfuncArg)
        self.A = a

        self.AH += self.A * pyb.elapsed_millis(self.start)/3600000
        self.start = pyb.millis()

    def capacity(self):
        if self.V > 13.0:
            self.capacityV = -1
        else:
            self.capacityV = self.capacityfromvoltage()

        self.capacityAH = round((self.initialcharge + (self.AH / self.AHCapacity)*100)/5)*5
        if self.capacityAH > 100:
            self.capacityAH = 100

    def capacityfromvoltage(self):
        x = 0
        while self.V <= self.BatteryVoltCurve[x][1]:
            x += 1

        a = (self.V - self.BatteryVoltCurve[x][1]) / (self.BatteryVoltCurve[x-1][1] - self.BatteryVoltCurve[x][1])

        return round((self.BatteryVoltCurve[x][0] + a * 10)/5)*5

    def update(self):
        self.voltage()
        self.current()
        self.capacity()

class BatteryCurrentADC:

    pga = [6144, 4096, 2048, 1024, 512, 256]

    def __init__(self):
        self.adc = ADS1115()
        self.pgx =1

    def battery(self, mux):
        self.adc.setConfig(acqmode='single', pga=self.pga[self.pgx], mux=mux)
        valid_reading = False
        res=0
        while not valid_reading:
            self.adc.startADCConversion()
            #read Voltages
            res = self.adc.readConversion()
            valid_reading = True
            if res >= self.pga[self.pgx]:
                # overload - reduce sensitivity
                if self.pgx > 0:
                    self.pgx -= 1
                    self.adc.setPGA(self.pga[self.pgx])
                    valid_reading = False
            if self.pgx < 5 and res <= self.pga[self.pgx + 1]:
                # not using full range
                self.pgx += 1
                self.adc.setPGA(self.pga[self.pgx])
                valid_reading = False
        return res

def BatteryThread(BatteryObject):
    bat = BatteryObject
    wf = Timeout(1)
    while True:
        bat.update()
        yield wf()
