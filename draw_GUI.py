from Digole_OLED_serial import *

# connection
OLED = Digole("/dev/ttyMFD1", width=160, height=128)
# clear screen
OLED.clearScreen()
# set font
OLED.setFont(18)
# set mode
OLED.setMode("C")

OLED.write_command("BGC", 0x00)

# draw left circle
OLED.setColor(0xDD)
# set background color
OLED.write_command("BGC", 0xDD)
OLED.drawCircle(40, 55, 40, 1)
OLED.setColor(0x1c)
OLED.drawStr(25, 40, "RPM")
# draw right circle
OLED.setColor(0x6B)
OLED.drawCircle(120, 55, 40, 1)
OLED.write_command("BGC", 0x6B)
OLED.setColor(0x1c)
OLED.drawStr(105, 40, "BPM")
# draw center circle
OLED.setColor(0xE1)
OLED.drawCircle(78, 80, 40, 1)
OLED.write_command("BGC", 0xE1)
OLED.setColor(0x1c)
OLED.drawStr(62, 70, "Km/h")

