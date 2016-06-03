from Digole_OLED_serial import *

def draw_gui_1(OLED, scale=1, font=18):
    """ three circles, two at the top, one at the bottom,
    top ones are for RPM and BPM,
    bottom one is for Km/h"""
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
    # set mode
    OLED.setMode("C")

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
    OLED.drawStr(int(62*scale), int(70*scale), "Km/h")
    # set background to black
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)


def draw_gui_2(OLED, draw_fn, quardrant=2):
    """ draw a particular function at the 1/4 quardrant,
    follow cartesian (1,2,3,4) CCW"""

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
    OLED.resetDrawWindow()
    OLED.setDrawWindow(0,0,80,64)
    draw_gui_2(OLED, draw_gui_1, 1)
    draw_gui_2(OLED, draw_gui_1, 3)
