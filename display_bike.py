#! /usr/bin/env python
from Digole_OLED_serial import *
from BLE import *
import thingspeak

def draw_ui(OLED):
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

def write_thingspeak(field_id, field_var):
    """ write certain fields to thingspeak, no loop """
    channel = thingspeak.channel()
    channel.update(field_id, field_var)


# connection
OLED = Digole("/dev/ttyMFD1", width=160, height=128)
draw_ui(OLED)

# connect BLE
HRM = HeartRate(sys.argv[1], debug=True) 
# HRM.main()

CSC = CSC(sys.argv[2], debug=True)
# CSC.main()
HRM.connect()
HRM.subscribe()
CSC.connect()
CSC.subscribe()
OLED.setColor(0xFF)
OLED.write_command("BGC", 0x00)
try:
    OLED.flush()
    counter = 0
    while True:
        OLED.drawStr(105, 52, "   ")
        OLED.drawStr(62, 82, "    ")
        OLED.drawStr(25, 52, "   ")
        hrm = HRM.__str__().strip()
        speed, cadence = CSC.__str__().strip().split(",")
        print ", ".join([hrm, speed, cadence])
        
        OLED.drawStr(105, 52, hrm)
        OLED.drawStr(62, 82, speed)
        OLED.drawStr(25, 52, cadence)

        if counter == 60:
            write_thingspeak([1, 2, 3], [speed, cadence, hrm])
            counter = 0
        counter += 1
        time.sleep(1)
except KeyboardInterrupt:
    OLED.flush()
    HRM.unsubscribe()
    HRM.disconnect()
    CSC.unsubscribe()
    CSC.disconnect()
