#! /usr/bin/env python
from Digole_OLED_serial import *
from BLE import *
from draw_GUI import *
import thingspeak

def write_thingspeak(field_id, field_var):
    """ write certain fields to thingspeak, no loop """
    channel = thingspeak.channel()
    channel.update(field_id, field_var)


# connection
OLED = Digole("/dev/ttyMFD1", width=160, height=128)

# draw framework
draw_gui_1(OLED)

# connect BLE
HRM = HeartRate(sys.argv[1], debug=True) 
# HRM.main()

CSC = CSC(sys.argv[2], debug=True)
# CSC.main()
HRM.connect()
HRM.subscribe()
CSC.connect()
CSC.subscribe()

# keep background color
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
