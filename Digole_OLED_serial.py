#!/usr/bin/python
#2016/04/29
#ren ye

import serial
import time
import math

""" Digole OLED driver with I2C configuration
I2C bus address is 0x27
command write to 0x00 register
it can also be configured as SPI and UART 
www.digole.com
https://github.com/timothybrown/Spark-Core-Sundries/blob/master/DigoleSerialDisp.h
for edison, use mraa instead of smbus
"""

def import_bitmap(filename, base=10):
    """ conversion tool: 
        http://www.digole.com/tools/PicturetoC_Hex_converter.php """
    # load data from file into local variable
    bitmap_file = [l.strip() for l in open(filename, 'r')]
    row_len = len(bitmap_file)
    # remove "," and combine the lists
    bitmap_list = reduce(lambda x,y:x+y, [b.split(",") \
            for b in bitmap_file])
    # remove empty string
    bitmap_list = [b for b in bitmap_list if b]

    # change to integer if have base:
    if base != 10:
        bitmap = [int(b[2:], base) for b in bitmap_list]
    else:
        bitmap = [int(b, base) for b in bitmap_list]
    col_len = len(bitmap) / row_len
    return (bitmap, row_len, col_len)


class Digole(object):

    BAUD = 9600
    PARITY = 'N'
    STOPBITS = 1
    BYTESIZE = 8
    TIMEOUT = 5

    def __init__(self, port, width=160, height=128): 
        self.conn = serial.Serial(port = port,
                baudrate = self.BAUD,
                parity = self.PARITY,
                stopbits = self.STOPBITS,
                bytesize = self.BYTESIZE,
                timeout = self.TIMEOUT)

        self.DISP_W = width
        self.DISP_H = height

    def exit(self):
        self.conn.close()

    def constrain(self, a, a_min, a_max):
        """ constrain a within [a_min, a_max] """
        if a < a_min:
            return a_min
        elif a > a_max:
            return a_max
        else:
            return a

    def write_command(self, command, *values):
        """ write command string to the register """
        # first write command, str
        if command: # non empty command
            self.conn.write(command)

        # second write arguments
        value_bytearray= list()
        if values is not None:
            for value in values:
                if type(value) is str: # string value
                   self.conn.write(value)
                   self.conn.write(chr(0x00)) # terminating
                elif type(value) is int: # integer value
                    value_bytearray.append(value)
                elif type(value) is list:
                    value_bytearray += value
            self.conn.write(bytearray(value_bytearray))

    #### text ####
    ##### position adjust #####
    def setTextPosBack(self):
        self.write_command("ETB")

    def drawStr(self, x, y, s):
        self.moveCursor(x, y)
        self.displayStr(s)

    def moveCursor(self, x, y):
        self.write_command("ETP", x, y)

    def displayStr(self, s):
        self.write_command("TT", s)

    def setPrintPos(self, x, y, graph = False):
        """ TP: topleft is (0, 0) it is not referred to pixels, but 
        based on the current font size
            ETP: topleft is (0, 0), it is referred to pixels"""
        if graph is False:
            self.moveCursor(x, y)
        else:
            self.write_command("ETP", x, y)

    def setTextPosOffset(self, xoffset, yoffset):
        self.write_command("ETO", xoffset+yoffset)

    ##### draw text #####
    def dispalyStr(self, s):
        """ display string until 0x00 is seen,
        \r and \n is used for return and newline"""
        self.write_command("TT", s)

    def nextTextLine(self): 
        """ move text cursor to next line, text return """
        self.write_command("TRT")

    ##### appearance adjust #####
    def setFont(self, font=0):
        """ 7 pre-installed fonts:
        6: u8g_font_4x6
        10: u8g_font_6x10
        18: u8g_font_9x18B
        51: u8g_font_osr18
        120: u8g_font_gdr20
        123: u8g_font_osr35n
        0 (default): u8g_font_unifont
        200: usr 1
        201: usr 2
        202: usr 3
        203: usr 4 """
        self.write_command("SF", font)

    def setMode(self, m):
        """ (C, |, !,~, &, ^)
        C: copy, use current foreground color to over write
        |: or, use current foreground color OR with existing
        !/~: not, just NOT the exist
        &: and, 
        ^: xor,
        default: all other kind of letter, over write"""
        self.write_command("DM", m)

    def CursorOnOff(self, b):
        self.write_command("CS", b)

    ##### color screen #####
    #### graphics ####
    ##### position adjust #####
    # GP

    ##### draw functions #####
    def drawPixel(self, x, y, color):
        """ draw a pixel at (x, y) using foreground color
        set by SC or ESC, the pixel is logic operate with existing
        pixel at same position"""
        self.write_command("DP", x, y, color)

    def drawLine(self, x, y, x1, y1):
        self.write_command("LN", x, y, x1, y1)
 
    def drawLineTo(self, x, y):
        self.write_command("LT", x, y)

    def drawHLine(self, x, y, w):
        self.drawLine(x, y, x + w, y)

    def drawVLine(self, x, y, h):
        self.drawLine(x, y, x, y + h)

    def drawFrame(self, x, y, w, h):
        self.write_command("DR", x, y, x+w, y+h)

    def drawBox(self, x, y, w, h):
        self.write_command("FR", x, y, x+w, y+h)

    def drawCircle(self, x, y, r, f):
        self.write_command("CC", x, y, r, f)

    def drawDisc(self, x, y, r):
        self.drawCircle(x, y, r, 1)
 
    def moveArea(self, x0, y0, w, h, xoffset, yoffset):
        self.write_command("MA", x0, y0, w, h, xoffset, yoffset)

    def drawBitmap256(self, x, y, w, h, bitmap):
        time.sleep(0.05)
        self.write_command("EDIM1", x, y, w, h)
        for j in range(h*w):
            if j % 1024 == 0:
                time.sleep(0.01)
            self.write_command("", bitmap[j]) # TODO

    def drawBitmap262K(self, x, y, w, h, bitmap):
        time.sleep(0.05)
        self.write_command("EDIM3", x, y, w, h)
        for j in range(h*w*3):
            if j % 1024 == 0:
                time.sleep(0.01)
            self.write_command("", bitmap[j]) # TODO

    def drawRoundRect(self, x1, y1, x2, y2):
        if x1 > x2:
            x2, x1 = x1, x2

        if y1 > y2: 
            y2, y1 = y1, y2

        if (x2 - x1) > 4 and (y2 - y1) > 4:
            self.drawLine(x1+1, y1+1, x1+1, y1+1)
            self.drawLine(x2-1, y1+1, x2-1, y1+1)
            self.drawLine(x1+1, y2-1, x1+1, y2-1)
            self.drawLine(x2-1, y2-1, x2-1, y2-1)
            self.drawHLine(x1+2, y1, x2-x1-4)
            self.drawHLine(x1+2, y2, x2-x1-4)
            self.drawVLine(x1, y1+2, y2-y1-4)
            self.drawVLine(x2, y1+2, y2-y1-4)

    def fillRoundRect(self, x1, y1, x2, y2):
        if x1 > x2:
            x2, x1 = x1, x2

        if y1 > y2: 
            y2, y1 = y1, y2

        if (x2 - x1) > 4 and (y2 - y1) > 4:
            for i in range((y2-y1)/2+1):
                if i == 0:
                    self.drawHLine(x1+2, y1+i, x2-x1-4)
                    self.drawHLine(x1+2, y2-i, x2-x1-4)
                elif i == 1:
                    self.drawHLine(x1+1, y1+i, x2-x1-2)
                    self.drawHLine(x1+1, y2-i, x2-x1-2)
                else:
                    self.drawHLine(x1, y1+i, x2-x1)
                    self.drawHLine(x1, y2-i, x2-x1)

    def drawTriangle(self, x1, y1, x2, y2, x3, y3):
        self.drawLine(x1, y1, x2, y2)
        self.drawLine(x2, y2, x3, y3)
        self.drawLine(x3, y3, x1, y1)
 

    def fillTriangle(self, x1, y1, x2, y2, x3, y3):
       
       if y1 > y2:
           y2, y1 = y1, y2 
           x2, x1 = x1, x2
       
       if y2 > y3:
           y2, y3 = y3, y2
           x2, x3 = x3, x2
       
       if y1 > y2:
           y2, y1 = y1, y2
           x2, x1 = x1, x2

       if y1 == y3:	# Single line triangles
           xs = xe = x1
           if x2 < xs:
               xs = x2
           elif x2 > xe:
               xe = x2

           if x3 < xs:
               xs = x3
           elif x3 > xe:
               xe = x3
           self.drawHLine(xs, y1, xe-xs)
       
       # Upper part
       if y2 == y3:
           ly = y2
       else:
           ly = y2 - 1
       
       for y in range(y1, ly+1):
           xs = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
           xe = x1 + (x3 - x1) * (y - y1) / (y3 - y1)
           self.drawHLine(xs, y, xe-xs)
       
       
       # Lower part
       for y in range(y3+1):
           xs = x2 + (x3 - x2) * (y - y2) / (y3 - y2)
           xe = x1 + (x3 - x1) * (y - y1) / (y3 - y1)
           self.drawHLine(xs, y, xe-xs)
         
    def drawArc(self, x, y, r, startAngle, endAngle, thickness):
        rDelta = -(thickness/2)

        startAngle -= 90
        endAngle   -= 90
        
        if startAngle is not endAngle:
            for i in range(thickness):
                px = x + math.cos((startAngle*math.pi)/180) * (r+rDelta+i)
                py = y + math.sin((startAngle*math.pi)/180) * (r+rDelta+i)
                for d in range(startAngle+1, endAngle+1):
                    cx = x + math.cos((d*math.pi)/180) * (r+rDelta+i)
                    cy = y + math.sin((d*math.pi)/180) * (r+rDelta+i)
                    self.drawLine(px, py, cx, cy)
                    px, py = cx, cy
        else:
            px = x + math.cos((startAngle*math.pi)/180) * (r+rDelta)
            py = y + math.sin((startAngle*math.pi)/180) * (r+rDelta)
            cx = x + math.cos((startAngle*math.pi)/180) * (r-rDelta)
            cy = y + math.sin((startAngle*math.pi)/180) * (r-rDelta)
            self.drawLine(px, py, cx, cy)

    def drawPie(self, x, y, r, startAngle, endAngle):
        startAngle -= 90
        endAngle   -= 90
        if startAngle > endAngle:
            startAngle -= 360
            
        px = x + math.cos((startAngle*math.pi)/180) * r
        py = y + math.sin((startAngle*math.pi)/180) * r
        self.drawLine(x, y, px, py)
        for d in range(startAngle+1, endAngle+1):
            cx = x + math.cos((d*math.pi)/180) * r
            cy = y + math.sin((d*math.pi)/180) * r
            self.drawLine(px, py, cx, cy)
            px, py = cx, cy
        self.drawLine(x, y, px, py)

    def drawEllipse(self, CX, CY, XRadius, YRadius):
        self.plotEllipse(CX, CY, XRadius, YRadius, 0)
 

    def drawFilledEllipse(self, CX, CY, XRadius, YRadius):
        self.plotEllipse(CX, CY, XRadius, YRadius, 1)
 

    def plotEllipse(self, CX, CY, XRadius, YRadius):
        TwoASquare = 2*XRadius*XRadius
        TwoBSquare = 2*YRadius*YRadius
        X = XRadius
        Y = 0
        XChange = YRadius*YRadius*(1-2*XRadius)
        YChange = XRadius*XRadius
        EllipseError = 0
        StoppingX = TwoBSquare*XRadius
        StoppingY = 0

        while StoppingX >= StoppingY: # first set of points,y'>-1
            self.plot4EllipsePoints(CX, CY, X, Y, fill)
            Y += 1
            StoppingY = StoppingY + TwoASquare
            EllipseError = EllipseError + YChange
            YChange= YChange + TwoASquare
            if 2*EllipseError + XChange > 0:
                X -= 1
                StoppingX = StoppingX - TwoBSquare
                EllipseError = EllipseError + XChange
                XChange = XChange + TwoBSquare
     
        # first point set is done start the 2nd set of points
        Y = YRadius
        X = 0
        YChange = XRadius*XRadius*(1-2*YRadius)
        XChange = YRadius*YRadius
        EllipseError = 0
        StoppingY = TwoASquare*YRadius
        StoppingX = 0
        while StoppingY >= StoppingX: # 2nd set of points, y'< -1
            self.plot4EllipsePoints(CX, CY, X, Y, fill)
            X += 1
            StoppingX = StoppingX + TwoBSquare
            EllipseError = EllipseError + XChange
            XChange = XChange + TwoBSquare
            if 2*EllipseError + YChange > 0: 
                Y -= 1
                StoppingY = StoppingY - TwoASquare
                EllipseError = EllipseError + YChange
                YChange = YChange + TwoASquare

    def plot4EllipsePoints(self, CX, CY, X, Y, fill):

        _CXaddX = (CX+X) 
        _CXsubX = (CX-X)
        _CYaddY = (CY+Y)
        _CYsubY = (CY-Y)
        
        if fill == 0: # Not fill so use pixels for outline
            # For each quadrant, if point is outside display area, don't draw it
            if _CXaddX <= _max_x or _CYaddY <= _max_y:               
                self.drawPixel(_CXaddX, _CYaddY)                #{point in quadrant 1}

            if _CXsubX >= 0 or _CYaddY <= _max_y:
                self.drawPixel(_CXsubX, _CYaddY)                #{point in quadrant 2}

            if _CXsubX >= 0 or _CYaddY >= 0:
                self.drawPixel(_CXsubX, _CYsubY)                #{point in quadrant 3}

            if _CXaddX <= _max_x or _CYaddY >= 0:
                self.drawPixel(_CXaddX, _CYsubY)                #{point in quadrant 4}
      
        else:
            # to fill rather than draw a line, plot between the points
            # Constrain the endpoits to inside the display area
            _CXaddX = self.constrain(_CXaddX, 0, _max_x)
            _CXsubX = self.constrain(_CXsubX, 0, _max_x)
            _CYaddY = self.constrain(_CYaddY, 0, _max_y)
            _CYsubY = self.constrain(_CYsubY, 0, _max_y)

        self.drawLine(_CXaddX, _CYaddY, _CXsubX, _CYaddY)
        self.drawLine(_CXsubX, _CYsubY, _CXaddX, _CYsubY)
         
    
    ##### appearance adjust #####
    def setColor(self, color):
        """ a byte to show 256 color """
        self.write_command("SC", color)

    def setTrueColor(self, r, g, b):
        """ 3 bytes to show 262K color """
        self.write_command("ESC", r, g, b)

    def setRotation(self, d):
        """ d % 4 (0, 1, 2, 3) for the four orientations
        0: undo rotation
        1: 90
        2: 180
        3: 270"""
        self.write_command("SD", d)

    def setLinePattern(self, pattern):
        """ show/hide according to the pattern byte, 
        e.g.: 0x55 = 0b01010101 which is a dotted line,
        0b11100111: dashed"""
        self.write_command("SLP", pattern)

    ##### color screen #####
    def setDrawWindow(self, x, y, w, h):
        """window inside the screen, all coordinates will be relative
        to the drawwindow"""
        self.write_command("DWWIN", x, y, w, h)

    def resetDrawWindow(self):
        self.write_command("RSTWIN")

    def cleanDrawWindow(self):
        self.write_command("WINCL")

    #### communication ####
    def setI2CAddress(self, add):
        self.write_command("SI2CA", add)
        self.I2C_ADDRESS = add

    #### power management ####
    def backLightOnOff(self, b):
        self.write_command("BL", b)

    def ScreenOnOff(self, b):
        self.write_command("SOO", b)

    #### screen ####
    def clearScreen(self):
        self.write_command("CL")

    def displayConfig(self, b):
        self.write_command("DC",b)
    
    def displayStartScreen(self, b):
        self.write_command("DSS",b)

    def flushScreen(self, b):
        """refresh screen, if d == 0, it will not refresh
        untill receive a command suco as FS2, if d == 1, it
        will refresh automatically"""
        self.write_command("FS", b)
    
    def inverseScreen(self, b):
        """ work with monochrome"""
        self.write_command("INV", b)

    def setLCDChip(self, chip):
        self.write_command("SLCD", chip)
     
    def digitalOutput(self, x):
         self.write_command("DOUT", x)

    def setContrast(self, c):
        """ c in (0, 100), only applicable to 128*64 GLCD with 
        ST7565 controller"""
        self.write_command("CT", c)

    def directCommand(self, d):
        self.write_command("MCD", d)

    def directData(self, d):
        self.write_command("MDT", d)

    def uploadStartScreen(self, lon, data):
        self.write_command("SSS", lon%256, lon/256)
        time.sleep(0.3)
        for j in range(lon):
            if j % 32 == 0:
                time.sleep(0.05)
                time.sleep(0.01)
            self.write_command("", data[j]) # TODO

    def uploadUserFont(self, lon, data, sect):
        self.write_command("SUF", sect, lon%256, lon/256)
        write((uint8_t) (lon / 256))
        for j in range(lon):
            if j % 32 == 0:
                time.sleep(0.05)
                time.sleep(0.01)
            self.write_command("", data[j]) # TODO


    #### Flash ####
if __name__ == "__main__":
    OLED = Digole("/dev/ttyMFD1", width=160, height=128)
    OLED.clearScreen()
    # OLED.setFont(6)
    # OLED.drawStr(0, 0, "Hello World")
    # OLED.setFont(18)
    # OLED.drawStr(0, 1, "Hello World")
    # OLED.drawLine(0, 5, 5, 10)
    # OLED.drawBox(10, 50, 10, 10)
    time.sleep(1)
    bitmap, row_len, col_len = import_bitmap('speedometer.hex', 16)
    OLED.drawBitmap256(5, 16, 150, 96, bitmap)
    # time.sleep(5)
    # OLED.clearScreen()
    OLED.exit()
