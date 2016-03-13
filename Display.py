import epaper
import math
import pyb
from usched import Poller

# Block co-ordinates
capacity_batY = [121, 132, 151, 162]
capacity_batX = [34, 45, 56, 67, 78, 89, 100, 111, 122, 133, 144,
                 155, 166, 177, 188, 199, 210, 221, 232, 243, 254]
text_batx = [155, 225]
text_baty = [28, 53, 78]


class BatteryDisplay:
    def __init__(self, side='L', bat1=None, bat2=None):
        self.disp = epaper.Display(side)
        self.bat1 = bat1
        self.bat2 = bat2
        self.dV1 = 0
        self.dA1 = 0
        self.dV2 = 0
        self.dA2 = 0

    # Draws standard background for monitor
    def background(self):
        self.disp.clear_screen(False)
        self.disp.line(0, 25, 263, 25)
        self.disp.line(0, 50, 263, 50)
        self.disp.line(0, 75, 263, 75)
        self.disp.line(0, 100, 263, 100)
        self.disp.line(123, 0, 123, 100)
        self.disp.line(193, 0, 193, 100)
        with self.disp.font('/sd/arial21x21'):
            self.disp.locate(125, 4)
            self.disp.puts("BAT 1")
            self.disp.locate(195, 4)
            self.disp.puts("BAT 2")
            self.disp.locate(10, 28)
            self.disp.puts("Voltage")
            self.disp.locate(10, 53)
            self.disp.puts("Current")
            self.disp.locate(10, 78)
            self.disp.puts("AH Balance")
            self.disp.locate(0, 121)
            self.disp.puts("1")
            self.disp.locate(0, 151)
            self.disp.puts("2")
        with self.disp.font('/sd/ab'):
            self.disp.locate(10, 103)
            self.disp.puts("Capacity   25%     50%     75%   100%")
        with self.disp.font('/sd/ab8'):
            self.disp.locate(20, 121)
            self.disp.puts("V")
            self.disp.locate(14, 132)
            self.disp.puts("AH")
            self.disp.locate(20, 151)
            self.disp.puts("V")
            self.disp.locate(14, 161)
            self.disp.puts("AH")
    
        # top marks
        self.disp.line(88, 116, 88, 119, width=3)
        self.disp.line(143, 116, 143, 119, width=3)
        self.disp.line(198, 116, 198, 119, width=3)
        # mid marks
        self.disp.line(88, 144, 88, 149, width=3)
        self.disp.line(143, 144, 143, 149, width=3)
        self.disp.line(198, 144, 198, 149, width=3)
        # bottom marks
        self.disp.line(88, 174, 88, 175, width=3)
        self.disp.line(143, 174, 143, 175, width=3)
        self.disp.line(198, 174, 198, 175, width=3)
        # bounding boxes
        self.disp.rect(32, 119, 254, 144)
        self.disp.rect(32, 149, 254, 174)
    
    def draw_capacity(self, current_capacity, test=False):
        if test is True:
            for x in range(0, 20):
                self.disp.fillrect(capacity_batX[x], capacity_batY[0], capacity_batX[x+1]-1, capacity_batY[0]+10)
                self.disp.fillrect(capacity_batX[x], capacity_batY[1], capacity_batX[x+1]-1, capacity_batY[1]+10)
                self.disp.fillrect(capacity_batX[x], capacity_batY[2], capacity_batX[x+1]-1, capacity_batY[2]+10)
                self.disp.fillrect(capacity_batX[x], capacity_batY[3], capacity_batX[x+1]-1, capacity_batY[3]+10)
        else:
            y = 0
            for lne in current_capacity:
                if lne > 0:
                    sects = lne // 5
                    for x in range(0, sects):
                        self.disp.fillrect(capacity_batX[x], capacity_batY[y],
                                           capacity_batX[x+1]-1, capacity_batY[y]+10)
                else:
                    with self.disp.font('/sd/ab8'):
                        self.disp.locate(50, capacity_batY[y])
                        self.disp.puts("- - - - CHARGING - - - -")
                y += 1

    def update(self):
        self.background()
        self.print_number(self.bat1.V, text_batx[0], text_baty[0])
        self.print_number(self.bat1.A, text_batx[0], text_baty[1], positive_sign=True)
        self.print_number(self.bat1.AHbalance, text_batx[0], text_baty[2], positive_sign=True)
        self.print_number(self.bat2.V, text_batx[1], text_baty[0])
        self.print_number(self.bat2.A, text_batx[1], text_baty[1], positive_sign=True)
        self.print_number(self.bat2.AHbalance, text_batx[1], text_baty[2], positive_sign=True)
        self.draw_capacity([self.bat1.Vcapacity, self.bat1.AHcapacity, self.bat2.Vcapacity, self.bat2.AHcapacity])
        self.dV1 = self.bat1.V
        self.dA1 = self.bat1.A
        self.dV2 = self.bat2.V
        self.dA2 = self.bat2.A
        self.disp.show()

    def print_number(self, value, x, y, positive_sign=False):
        negative_sign = False
        value_fraction, value_integer = math.modf(value)
        value_fraction = int(abs(value_fraction) * 100)
        value_integer = int(value_integer)
        if value_integer < 0:
            negative_sign = True
            value_integer = abs(value_integer)
        if value_integer // 10 == 1:
            wdth = 18
        elif value_integer // 10 > 1:
            wdth = 22
        else:
            wdth = 11

        with self.disp.font('/sd/arial21x21'):
            self.disp.locate(x - wdth, y)
            self.disp.puts(str(value_integer) + "." + str(value_fraction))

        if positive_sign:
            with self.disp.font('/sd/arial21x21'):
                self.disp.locate(x - wdth - 9, y)
                self.disp.puts("+")

        if negative_sign:
            with self.disp.font('/sd/arial21x21'):
                self.disp.locate(x - wdth - 7, y)
                self.disp.puts("-")

    def Poll(self):
        if (abs(self.dV1-self.bat1.V) > 0.2 or abs(self.dV2-self.bat2.V) > 0.2 or
                    abs(self.dA1-self.bat1.A) > 0.2 or abs(self.dA2-self.bat2.A) > 0.2):
            return 1
        return None


def displayThread(bat1, bat2):
    disp = BatteryDisplay(bat1=bat1, bat2=bat2)
    wf = Poller(disp.Poll, 30)
    start = pyb.millis()
    while True:
        reason = (yield wf())
        if reason[1] and pyb.elapsed_millis(start) > 10000:
            start = pyb.millis()
            disp.update()
        else:
            start = pyb.millis()
            disp.update()
