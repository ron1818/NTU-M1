from Digole_OLED_serial import *
import time

def scale_font(scale, font):
    # set font
    scaled_font = int(font*scale)
    if 0 <= scaled_font < 8:
        scaled_font = 6
    elif 8<= scaled_font < 15:
        scaled_font = 10
    elif 15<= scaled_font < 19:
        scaled_font = 18
    else:
        scaled_font = font # no scale

    OLED.setFont(scaled_font)


def display_perform(OLED, scale=1, font=18):
    """ three circles, two at the top, one at the bottom,
    top ones are for RPM and BPM,
    bottom one is for Km/h"""
    # scale font
    scale_font(scale, font)

    # set mode
    OLED.setMode("C")

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)

    # draw left circle
    OLED.setColor(0xDD)
    # set background color
    OLED.write_command("BGC", 0xDD)
    OLED.drawCircle(int(40*scale), int(55*scale), int(40*scale), 1)
    OLED.setColor(0x1c)
    OLED.drawStr(int(25*scale), int(40*scale), "RPM")
    # draw right circle
    OLED.setColor(0x6B)
    OLED.drawCircle(int(120*scale), int(55*scale), int(40*scale), 1)
    OLED.write_command("BGC", 0x6B)
    OLED.setColor(0x1c)
    OLED.drawStr(int(105*scale), int(40*scale), "BPM")
    # draw center circle
    OLED.setColor(0xE1)
    OLED.drawCircle(int(78*scale), int(80*scale), int(40*scale), 1)
    OLED.write_command("BGC", 0xE1)
    OLED.setColor(0x1c)
    OLED.drawStr(int(62*scale), int(70*scale), "Kph")

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)


def display_trip(OLED, scale=1, font=18, stopflag=False):
    """ display trip time and trip distance,
    including autostop """

    scale_font(scale, font)
    # set mode
    OLED.setMode("C")

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)

    # draw upper rectangle
    OLED.setColor(0xDD)
    # draw upper rectangle
    OLED.fillRoundRect(int(0*scale), int(0*scale), int(80*scale), int(20*scale))
    # set background color
    OLED.write_command("BGC", 0xDD)
    # font color
    OLED.setColor(0x1c)

    # time elapsed
    global t0
    global t1
    t_old = t1
    if stopflag == False:
        t1 = time.time()

    m, s = divmod(t1-t0, 60)
    h, m = divmod(m, 60)
    # print "%d:%02d:%02d" % (h, m, s)
    OLED.drawStr(int(0*scale), int(18*scale), "%02d:%02d:%02d" % (h, m, s))
    
    # draw lower rectangle
    OLED.setColor(0x6B)
    OLED.fillRoundRect(int(0*scale), int(22*scale), int(80*scale), int(42*scale))
    OLED.write_command("BGC", 0x6B)
    # font color
    OLED.setColor(0x1c)
    
    global distance

    # trip accumulated
    if stopflag == False:
        distance += (t1-t_old) * speed / 3.6 / 1000.0

    OLED.drawStr(int(0*scale), int((22+18)*scale), "{:.2f}".format(distance))

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)


def display_data(OLED, scale=1,  **data_dict):
    """ display data into their positions,
    data_dict: key: data_name, [value, x, y] """
    for key, value in data_dict.iteritems():
        data, x, y = value
        OLED.drawStr(data, int(x*scale), int(y*scale))


def display_timedate(OLED, scale=1, font=18):
    """ display time and date, also time elapsed """
    # scale font
    scale_font(scale, font)

    # time in wk dd-mm-yy format
    OLED.drawStr(int(1*scale), int(18*scale), time.strftime("%a %d-%m-%y"))
    OLED.drawStr(int(1*scale), int(36*scale), time.strftime("%H:%M:%S"))



def draw_in_quardrant(OLED, draw_fn, quardrant=2):
    """ draw a particular function at the 1/4 quardrant,
    follow cartesian (1,2,3,4) CCW,
    notice that for the child draw fn, scale must be made"""

    if quardrant == 1:
        OLED.setDrawWindow(80, 0, 80, 64)
    elif quardrant == 2:
        OLED.setDrawWindow(0, 0, 80, 64)
    elif quardrant == 3:
        OLED.setDrawWindow(0, 64, 80, 64)
    else:
        OLED.setDrawWindow(80, 64, 80, 64)
        
    draw_fn(OLED, scale=0.5)

if __name__ == "__main__":
    # connection
    OLED = Digole("/dev/ttyMFD1", width=160, height=128)
    OLED.clearScreen()
    t0 = time.time()
    t1 = time.time()
    distance = 0
    speed = 5.0
    while True:
        draw_in_quardrant(OLED, display_perform, 3)
        draw_in_quardrant(OLED, display_trip, 2)
        draw_in_quardrant(OLED, display_timedate, 1)
        time.sleep(1)
