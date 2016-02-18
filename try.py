import epaper

a=epaper.Display('L')

a.line(0,25,263,25)
a.line(0,50,263,50)
a.line(0,75,263,75)
a.line(0,100,263,100)
a.line(163,0,163,175)
with a.font('/sd/arial21x21'):
    a.locate(25,27)
    a.puts("Voltage")
    a.locate(25,52)
    a.puts("Current")
    a.locate(25,77)
    a.puts("AH Balance")
