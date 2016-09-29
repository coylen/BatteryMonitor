import pyb
from ADS1115 import ADS1115
import time

_SOCCurrentFlow = (5, 10, 20, 40, 0, -100, -20, -10, -5)

_SOCParameters = ((12.2434210526, 0.0344855436963, -0.000264929149807, -3.04001553989e-006, 6.0498711814e-008, 0),
                  (1.20842105263E+01, 3.34084161446E-02,	-7.35983314892E-04,	2.54569991403E-05,	-4.25714636231E-07,	2.42914979753E-09),
                  (1.16221052632E+01, 4.67049564450E-02,	-3.66994847150E-04,	8.45295053464E-07,	-4.56692430146E-08,	5.26315789391E-10),
                  (1.10449122807E+01, 9.47550116578E-02,	-2.31528340096E-03,	3.64820267486E-05,	-3.43792172774E-07,	1.40350877205E-09),
                  (1.14031578948E+01, 3.38904796922E-02,	-4.05671083116E-04,	1.68629615581E-06,	1.26671574454E-08,	-1.07962213375E-10),
                  (1.16532035013E+01, 3.35225750801E-02,	-6.67046139745E-04,	9.97748462460E-06,	-8.18147832570E-08,	2.53560730705E-10),
                  (1.13536822820E+01, 4.13432297069E-02,	-8.43434866531E-04,	1.21687775227E-05,	-9.31012578543E-08,	2.69844269393E-10),
                  (1.11094538947E+01, 1.24981757467E-02,	5.86636093368E-04, -1.62853045119E-05,	1.67579269763E-07,	-6.20763884640E-10),
                  (1.02305921020E+01, 4.23200247107E-02,	-4.26235501414E-04,	1.49575401002E-06,	1.77734569617E-08,	-1.40482461634E-10))


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
        self.AH_15 = 0
        self.AH_60 = 0
        self.capacityV = 0
        self.capacityAH = 0
        # start timer
        self.timer = pyb.millis()
        self.last_write = time.time()
        self.log_message= ''
        self.write_flag = False
        self.AH_day = 0
        self.update()

    def voltage(self):
        # Read Voltage
        v = self.voltage_adc.read() / 4095 * 18.3
        self.V = v

    def current(self):
        # Read current
        a = self.Afunc.read(self.AfuncArg)
        self.A = a
        AHtemp = self.A * pyb.elapsed_millis(self.timer) / 3600000
        self.AH += AHtemp
        self.AH_15 += AHtemp
        self.AH_60 += AHtemp
        self.AH_day +=AHtemp
        self.timer = pyb.millis()

    def capacity(self):
        self.capacityV = self.SOCfromV()
        self.capacityAH = round((self.initialcharge + (self.AH / self.AHCapacity)*100)/5)*5
        if self.capacityAH > 100:
            self.capacityAH = 100
        if self.capacityAH < 0:
            self.capacityAH = 0

    def update(self):
        self.voltage()
        self.current()
        self.capacity()
 #       self.logging()

    def log(self, current_time):
        current_time_tuple = time.localtime(current_time)
        # TODO need to choose format V, A, AH15, AH60, AHday, capacityAH, capacityV
        self.log_message = "{0}-{1}-{2},{3}:{4},{5},{6},{7},{8}\r\n".format(current_time_tuple[2], current_time_tuple[1],
                                                                        current_time_tuple[0], current_time_tuple[3],
                                                                        current_time_tuple[4], self.V, self.AH_15,
                                                                        self.AH_60, self.AH_day)
        self.AH_15 = 0
        if current_time_tuple[4] == 0:
            self._AH60 = 0
        return self.log_message

    def new_day(self):
        self.AH_day = 0

    # def logging(self):
    #     current_time = time.time()
    #     if time.localtime(current_time)[4] % 15 == 0 and time.localtime(current_time - self.last_write)[4] > 5:
    #         current_time_tuple = time.localtime(current_time)
    #         # TODO need to choose format V, A, AH15, AH60, AHday, capacityAH, capacityV
    #         self.log_message = "{0}-{1}-{2},{3}:{4},{5},{6},{7},{8}".format(current_time_tuple[2], current_time_tuple[1],
    #                                                                   current_time_tuple[0], current_time_tuple[3],
    #                                                                   current_time_tuple[4], self.V, self.AH_15,
    #                                                                   self.AH_60, self.AH_day)
    #         self.AH_15 = 0
    #         if time.localtime(current_time)[5] == 0:
    #             self._AH60 = 0
    #         self.write_flag = True
    #         self.last_write = current_time


    def interpolateSOC(self):
        x = 0
        while x < 9:
            try:
                currentrate = self.AHCapacity / _SOCCurrentFlow[x]
            except:
                currentrate = 0
            if self.A > currentrate:
                break
            x += 1
        if x == 0:
            return _SOCParameters[0]
        if x == 9:
            return _SOCParameters[8]
        if x == 4:
            rate1 = self.AHCapacity / _SOCCurrentFlow[x - 1]
            rate2 = 0
        elif x == 5:
            rate1 = 0
            rate2 = self.AHCapacity / _SOCCurrentFlow[x]
        else:
            rate1 = self.AHCapacity / _SOCCurrentFlow[x - 1]
            rate2 = self.AHCapacity / _SOCCurrentFlow[x]

        factor = (self.A - rate1) / (rate2 - rate1)
        params1 = _SOCParameters[x - 1]
        params2 = _SOCParameters[x]
        interpolatedparams = []
        for x in range(6):
            y = (params2[x] - params1[x]) * factor + params1[x]
            interpolatedparams.append(y)
        return interpolatedparams

    def SOCfromV(self):
        params = self.interpolateSOC()
        # check extreme cases
        if self.V < params[0]:
            return 0

        v = 0
        for x in range(6):
            v += params[x] * pow(100, x)
        if self.V > v:
            return 100

        SOCestimate = 50
        a = 25
        while a > 2.5:
            v = 0
            for x in range(6):
                v += params[x] * pow(SOCestimate, x)
            if v > self.V:
                SOCestimate -= a
            else:
                SOCestimate += a
            a /= 2
        return round(SOCestimate / 5) * 5


_pga = (6144, 4096, 2048, 1024, 512, 256)


class BatteryCurrentADC:

    def __init__(self):
        self.adc = ADS1115()
        self.pgx = 1

    def read(self, mux):
        self.adc.setConfig(acqmode='single', pga=_pga[self.pgx], mux=mux)
        valid_reading = False
        res = 0
        while not valid_reading:
            self.adc.startADCConversion()
            # read Voltages
            res = self.adc.readConversion()
            valid_reading = True
            if res >= _pga[self.pgx]:
                # overload - reduce sensitivity
                if self.pgx > 0:
                    self.pgx -= 1
                    self.adc.setPGA(_pga[self.pgx])
                    valid_reading = False
            if self.pgx < 5 and res <= _pga[self.pgx + 1]:
                # not using full range
                self.pgx += 1
                self.adc.setPGA(_pga[self.pgx])
                valid_reading = False
        return res/625*50


from urandom import randrange

# simply class to generate random data for display testing
class testBattery(Battery):

    def __init__(self, Vpin, Afunc, AfuncArg='chan 0_1', initialcharge=100, batteryAH=110):
        super().__init__(Vpin, Afunc, AfuncArg='chan 0_1', initialcharge=100, batteryAH=110)

    def update(self):
        self.V = randrange(118, 138)/10
        self.A = randrange(-40, 40)/10
        AHtemp = self.A * pyb.elapsed_millis(self.timer) / 3600000
        self.AH += AHtemp
        self.AH_15 += AHtemp
        self.AH_60 += AHtemp
        self.AH_day +=AHtemp
        self.timer = pyb.millis()
        self.capacity()