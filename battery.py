import pyb


class Battery:

    def __init__(self, Vpin, Afunc,  initialcharge=100, AHCapacity=110):
        self.initialcharge = initialcharge
        self.AHCapacity = AHCapacity
        # Setup PINS
        self.voltage_adc = pyb.ADC(Vpin)
        self.Afunc = Afunc
        self.V = 0
        self.A = 0
        self.AH = 0
        self.BatteryVoltCurve = [(100, 12.6), (90, 12.5), (80, 12.42), (70, 12.32),
                                 (60, 12.2), (50, 12.06), (40, 11.9), (30, 11.75),
                                 (20, 11.58), (10, 11.31), (0, 10.5)]
        # start timer
        self.start = pyb.millis()

    def voltage(self):
        # Read Voltage
        v = self.voltage_adc.read()
        self.V = v / 4095 * 18.3

    def current(self):
        # Read current
        a = self.Afunc()
        self.A = a  # convert voltage to current?

        self.AH += self.A * pyb.elapsed_millis(self.start)/3600000
        self.start = pyb.millis()



    def Capacity(self):
        if self.V>13.0:
            cV = -1
        else:
            cV = self.capacityfromVoltage()

        cAH = round((self.initialcharge + (self.AH / self.AHCapacity)*100)/5)*5
        if cAH > 100:
            cA = 100

        return [cV, cAH]

    def capacityfromVoltage(self):
        x = 0
        while self.V <= self.BatteryVoltCurve[x][1]:
            x += 1

        a = (self.V - self.BatteryVoltCurve[x][1]) / (self.BatteryVoltCurve[x-1][1] - self.BatteryVoltCurve[x][1])

        return round((self.BatteryVoltCurve[x][0] + a * 10)/5)*5







