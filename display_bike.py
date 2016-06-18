#! /usr/bin/env python
from Digole_OLED_serial import *
from BLE import *
import draw_GUI
from draw_GUI import *
import thingspeak

def write_thingspeak(field_id, field_var):
    """ write certain fields to thingspeak, no loop """
    channel = thingspeak.channel()
    channel.update(field_id, field_var)

# connection
OLED = Digole("/dev/ttyMFD1", width=160, height=128)
# global speed, distance, t0, t1
draw_GUI.t0 = time.time()
draw_GUI.t1 = time.time()
draw_GUI.distance = 0
draw_GUI.speed = 0.0

perform_dict={"1BPM": ["   ", 0x6B, 80+42, 82-39],\
              "3KPH": ["    ", 0xE1, 80, 82+5],\
              "2RPM": ["   ", 0x03, 80-42, 82-39]}
# draw framework
OLED.clearScreen()
draw_in_quardrant(OLED, display_perform, 3, 0.5, 18, **perform_dict)
draw_in_quardrant(OLED, display_alert, 4, 0.5, 0)

# connect BLE
# HRM = HeartRate("D0:F1:73:6F:94:D9", debug=True) 
# HRM = HeartRate("E9:E3:B8:EC:D4:64", debug=True) 
# HRM.main()

# CSC = CSC("E9:E3:B8:EC:D4:64", debug=True)
# CSC = CSC(sys.argv[2], debug=True)
# CSC.main()
# HRM.connect()
# HRM.subscribe()
# CSC.connect()
# CSC.subscribe()

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
        draw_in_quardrant(OLED, display_data, 3, 0.5, 18, **perform_dict)

        perform_dict["1BPM"][0] = "100"
        perform_dict["3KPH"][0], perform_dict["2RPM"][0] = ["80", "90"]

        draw_GUI.speed = int(perform_dict["3KPH"][0])

        # print ", ".join([hrm, speed, cadence])
        draw_in_quardrant(OLED, display_data, 3, 0.5, 18, **perform_dict)
        
        if counter == 60:
            write_thingspeak([1, 2, 3], [value[0] for (key, value) in perform_dict.iteritems()])
            counter = 0
        counter += 1
        time.sleep(1)
except KeyboardInterrupt:
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)
    OLED.flush()
    # HRM.unsubscribe()
    # HRM.disconnect()
    # CSC.unsubscribe()
    # CSC.disconnect()
