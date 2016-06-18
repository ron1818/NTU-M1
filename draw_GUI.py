from Digole_OLED_serial import *
import time

def scale_font(OLED, scale, font):
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


def display_perform(OLED, scale=1, font=18, **data_dict):
    """ three circles, two at the top, one at the bottom,
    top ones are for RPM and BPM,
    bottom one is for Km/h"""
    # scale font
    scale_font(OLED, scale, font)

    radius = 35
    xoffset = 12
    yoffset = 8
    # set mode
    OLED.setMode("C")

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)

    for key, value in data_dict.iteritems():
        data, col, x, y = value
        # draw circle at center defined by x, y and col by col
        OLED.setColor(col)
        # set background color
        # OLED.write_command("BGC", col)
        # draw circle
        OLED.drawCircle(int(x*scale), int(y*scale), int(radius*scale), 1)
        # display head
        OLED.write_command("BGC", col)
        OLED.setColor(0x1c)
        OLED.drawStr(int((x-xoffset)*scale), int((y-yoffset)*scale), key[1:])
        OLED.write_command("BGC", 0x00)

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)


def display_trip(OLED, scale=1, font=18, stopflag=False):
    """ display trip time and trip distance,
    including autostop """
    tripx, tripy, triph, tripl = 1, 1, 20, 100
    xoffset, yoffset = 4, 18
    tripcol, distcol = 0x4F, 0x68

    scale_font(OLED, scale, font)
    # set mode
    OLED.setMode("C")

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)

    # draw upper rectangle
    OLED.setColor(tripcol)
    # draw upper rectangle
    OLED.fillRoundRect(int(tripx*scale), int(tripy*scale), int(tripl*scale), int(triph*scale))
    # set background color
    OLED.write_command("BGC", tripcol)
    # font color
    OLED.setColor(0x1c)

    # time elapsed
    global t0, t1, distance, speed
    t_old = t1
    if stopflag == False:
        t1 = time.time()

    m, s = divmod(t1-t0, 60)
    h, m = divmod(m, 60)
    # print "%d:%02d:%02d" % (h, m, s)
    OLED.drawStr(int((tripx+xoffset)*scale), int((tripy+yoffset)*scale), "%02d:%02d:%02d" % (h, m, s))
    
    # draw lower rectangle
    OLED.setColor(distcol)
    OLED.fillRoundRect(int(tripx*scale), int((tripy+yoffset+xoffset)*scale), int(tripl*scale), int((triph+xoffset+yoffset)*scale))
    OLED.write_command("BGC", distcol)
    # font color
    OLED.setColor(0x1c)
    

    # trip accumulated
    if stopflag == False:
        distance += (t1-t_old) * speed / 3.6 / 1000.0

    OLED.drawStr(int((tripx+xoffset)*scale), int((tripy+yoffset*2+xoffset)*scale), "{:.2f}".format(distance))

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)


def display_data(OLED, scale=1, font=18, **data_dict):
    """ display data into their positions,
    data_dict: key: data_name, [value, x, y] """
    # scale font
    scale_font(OLED, scale, font)

    xoffset = 12
    yoffset = 8

    # set mode
    OLED.setMode("C")

    for key, value in data_dict.iteritems():
        data, col, x, y = value
        OLED.write_command("BGC", col)
        OLED.setColor(0x1c)
        OLED.drawStr(int((x-xoffset)*scale), int((y+yoffset)*scale), data)
        OLED.write_command("BGC", 0x00)

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)


def display_timedate(OLED, scale=1, font=18):
    """ display time and date, also time elapsed """
    datex, datey = 1, 18
    yoffset = 18

    # scale font
    scale_font(OLED, scale, font)

    # time in wk dd-mm-yy format
    OLED.drawStr(int(datex*scale), int(datey*scale), time.strftime("%a %d-%m-%y"))
    OLED.drawStr(int(datex*scale), int((datey+yoffset)*scale), time.strftime("%H:%M:%S"))


def display_alert(OLED, scale=1, isfall=0):
    """ display fall signal, green for OK, red for fall """
    if isfall:
        OLED.setColor(0x40)
        OLED.write_command("BGC", 0x40)
    else:
        OLED.setColor(0x1D)
        OLED.write_command("BGC", 0x1D)

    OLED.drawCircle(int(80*scale), int(44*scale), int(15*scale),1)

    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)


def draw_in_quardrant(OLED, draw_fn, quardrant=2, *args, **kwargs):
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
        
    draw_fn(OLED, *args, **kwargs)

if __name__ == "__main__":
    # connection
    OLED = Digole("/dev/ttyMFD1", width=160, height=128)
    OLED.clearScreen()
    t0 = time.time()
    t1 = time.time()
    distance = 0
    speed = 5.0
    perform_dict={"1BPM": ["   ", 0x6B, 80+42, 82-34],\
                  "3KPH": ["    ", 0xE1, 80, 82],\
                  "2RPM": ["   ", 0xDD, 80-42, 82-34]}
    # display_perform(OLED, **perform_dict)
    # display_data(OLED, **perform_dict)
    draw_in_quardrant(OLED, display_perform, 3, 0.5, 18, **perform_dict)
    draw_in_quardrant(OLED, display_alert, 4, 0.5, 0)
    while True:
        draw_in_quardrant(OLED, display_trip, 2, 0.5, 18)
        draw_in_quardrant(OLED, display_timedate,1, 0.5, 18)
        draw_in_quardrant(OLED, display_data, 3, 0.5, 18, **perform_dict)
        # draw_in_quardrant(OLED, display_alert, 4, 0.5, 1)
        time.sleep(1)
