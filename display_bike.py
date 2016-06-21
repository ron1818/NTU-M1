#! /usr/bin/env python
import time
# import random
from Digole_OLED_serial import *
from BLE import *
import draw_GUI
from draw_GUI import *
import thingspeak
from fall_detection import fall_detection_sys

def write_thingspeak(field_id, field_var):
    """ write certain fields to thingspeak, no loop """
    channel = thingspeak.channel()
    channel.update(field_id, field_var)

# connection
OLED = Digole("/dev/ttyMFD1", width=160, height=128)
# fall detection
# global speed, distance, t0, t1
draw_GUI.t0 = time.time()
draw_GUI.t1 = time.time()
draw_GUI.distance = 0
draw_GUI.speed = 0.0

perform_dict_empty = {"1BPM": ["     ", 0x6B, 80+42, 82-39],\
              "3KPH": ["     ", 0xE1, 80, 82+5],\
              "2RPM": ["    ", 0x03, 80-42, 82-39]}
perform_dict = perform_dict_empty
# draw framework
OLED.clearScreen()
draw_in_quardrant(OLED, display_perform, 3, 0.5, 18, **perform_dict)
draw_in_quardrant(OLED, display_alert, 4, 0.5, 0)

# connect BLE
HRM = HeartRate("D0:F1:73:6F:94:D9", debug=True) 
# HRM = HeartRate(sys.argv[1], debug=True) 
HRM.main()

CSC = CSC("E9:E3:B8:EC:D4:64", debug=True)
# CSC = CSC(sys.argv[2], debug=True)
CSC.main()
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
        # empty display data

        draw_in_quardrant(OLED, display_trip, 2, 0.5, 18)
        draw_in_quardrant(OLED, display_timedate, 1, 0.5, 18)
        draw_in_quardrant(OLED, display_data, 3, 0.5, 18, 24, 8, **perform_dict_empty)
        # print(isfall.next())

        perform_dict["1BPM"][0] = HRM.__str__().strip()
        perform_dict["3KPH"][0], perform_dict["2RPM"][0] = CSC.__str__().strip().split(",")

        draw_GUI.speed = int(perform_dict["1BPM"][0])

        draw_in_quardrant(OLED, display_data, 3, 0.5, 18, 24, 8, **perform_dict)
        isfall=fall_detection_sys(11)
        draw_in_quardrant(OLED, display_alert, 4, 0.5, isfall)
        
        if counter == 60:
            write_thingspeak([1, 2, 3], [value[0] for (key, value) in perform_dict.iteritems()])
            counter = 0
        counter += 1
        time.sleep(1)
except KeyboardInterrupt:
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)
    OLED.flush()
    HRM.unsubscribe()
    HRM.disconnect()
    CSC.unsubscribe()
    CSC.disconnect()
