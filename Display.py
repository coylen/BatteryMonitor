import math
# Block co-ordinates
capacity_batY = [121, 132, 151, 162]
capacity_batX = [34, 45, 56, 67, 78, 89, 100, 111, 122, 133, 144,
                 155, 166, 177, 188, 199, 210, 221, 232, 243, 254]
text_batx = [155, 225]
text_baty = [28, 53, 78]

# class BatteryFASTDisplay:
#     def __init__(self, side='R', bat1=None, bat2=None):
#         self.disp = epaper.Display(side,mode = epaper.FAST)
#         self.bat1 = bat1
#         self.bat2 = bat2
#         self.dV1 = 0
#         self.dA1 = 0
#         self.dV2 = 0
#         self.dA2 = 0
#         self.timer = pyb.millis()

class draw:

    def __init__(self, disp):
        self.display = disp
# Draws standard background for monitor
    def background(self):
        self.display.clear_screen(False)
        self.display.line(0, 25, 263, 25)
        self.display.line(0, 50, 263, 50)
        self.display.line(0, 75, 263, 75)
        self.display.line(0, 100, 263, 100)
        self.display.line(123, 0, 123, 100)
        self.display.line(193, 0, 193, 100)
        with self.display.font('/sd/arial21x21'):
            self.display.locate(125, 4)
            self.display.puts("BAT 1")
            self.display.locate(195, 4)
            self.display.puts("BAT 2")
            self.display.locate(10, 28)
            self.display.puts("Voltage")
            self.display.locate(10, 53)
            self.display.puts("Current")
            self.display.locate(10, 78)
            self.display.puts("AH Balance")
            self.display.locate(0, 121)
            self.display.puts("1")
            self.display.locate(0, 151)
            self.display.puts("2")
        with self.display.font('/sd/ab'):
            self.display.locate(10, 103)
            self.display.puts("Capacity   25%     50%     75%   100%")
        with self.display.font('/sd/ab8'):
            self.display.locate(20, 121)
            self.display.puts("V")
            self.display.locate(14, 132)
            self.display.puts("AH")
            self.display.locate(20, 151)
            self.display.puts("V")
            self.display.locate(14, 161)
            self.display.puts("AH")

        # top marks
        self.display.line(88, 116, 88, 119, width=3)
        self.display.line(143, 116, 143, 119, width=3)
        self.display.line(198, 116, 198, 119, width=3)
        # mid marks
        self.display.line(88, 144, 88, 149, width=3)
        self.display.line(143, 144, 143, 149, width=3)
        self.display.line(198, 144, 198, 149, width=3)
        # bottom marks
        self.display.line(88, 174, 88, 175, width=3)
        self.display.line(143, 174, 143, 175, width=3)
        self.display.line(198, 174, 198, 175, width=3)
        # bounding boxes
        self.display.rect(32, 119, 254, 144)
        self.display.rect(32, 149, 254, 174)

    def draw_capacity(self, current_capacity, test=False):
        if test is True:
            for x in range(0, 20):
                self.display.fillrect(capacity_batX[x], capacity_batY[0], capacity_batX[x+1]-1, capacity_batY[0]+10)
                self.display.fillrect(capacity_batX[x], capacity_batY[1], capacity_batX[x+1]-1, capacity_batY[1]+10)
                self.display.fillrect(capacity_batX[x], capacity_batY[2], capacity_batX[x+1]-1, capacity_batY[2]+10)
                self.display.fillrect(capacity_batX[x], capacity_batY[3], capacity_batX[x+1]-1, capacity_batY[3]+10)
        else:
            y = 0
            for lne in current_capacity:
                if lne > 0:
                    sects = lne // 5
                    for x in range(0, sects):
                        self.display.fillrect(capacity_batX[x], capacity_batY[y],
                                           capacity_batX[x+1]-1, capacity_batY[y]+10)
                else:
                    with self.display.font('/sd/ab8'):
                        self.display.locate(50, capacity_batY[y])
                        self.display.puts("- - - - CHARGING - - - -")
                y += 1

    def update(self, bat1, bat2):
        self.background()
        self.print_number(bat1.V, text_batx[0], text_baty[0])
        self.print_number(bat1.A, text_batx[0], text_baty[1], positive_sign=True)
        self.print_number(bat1.AHbalance, text_batx[0], text_baty[2], positive_sign=True)
        self.print_number(bat2.V, text_batx[1], text_baty[0])
        self.print_number(bat2.A, text_batx[1], text_baty[1], positive_sign=True)
        self.print_number(bat2.AHbalance, text_batx[1], text_baty[2], positive_sign=True)
        self.draw_capacity([bat1.Vcapacity, bat1.AHcapacity, bat2.Vcapacity, bat2.AHcapacity])
        self.display.refresh()

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

        with self.display.font('/sd/arial21x21'):
            self.display.locate(x - wdth, y)
            self.display.puts(str(value_integer) + "." + str(value_fraction))

        if positive_sign:
            with self.display.font('/sd/arial21x21'):
                self.display.locate(x - wdth - 9, y)
                self.display.puts("+")

        if negative_sign:
            with self.display.font('/sd/arial21x21'):
                self.display.locate(x - wdth - 7, y)
                self.display.puts("-")


