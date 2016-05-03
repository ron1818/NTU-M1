from Digole_OLED_serial import *

# connection
OLED = Digole("/dev/ttyMFD1", width=160, height=128)
# clear screen
OLED.clearScreen()
# set background color
OLED.write_command("BGC", 0xFF)
# set font
OLED.setFont(18)
# set mode
OLED.setMode("C")

# draw left circle
OLED.setColor(0xDD)
OLED.drawCircle(40, 55, 40, 1)
# draw right circle
OLED.setColor(0x6B)
OLED.drawCircle(120, 55, 40, 1)
# draw center circle
OLED.setColor(0xE1)
OLED.drawCircle(78, 80, 40, 1)

# text color
OLED.setColor(0x1c)
OLED.drawStr(30, 40, "RPM")
OLED.drawStr(110, 40, "BPM")
OLED.drawStr(68, 70, "Km/h")
