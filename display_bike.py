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
# global speed, distance, t0, t1
t0 = time.time()
t1 = time.time()
distance = 0
speed = 0.0

# draw framework
OLED.clearScreen()
draw_in_quardrant(OLED, display_perform, 3, 0.5, 18)
draw_in_quardrant(OLED, display_alert, 4, 0.5, 0)

# connect BLE
HRM = HeartRate("D0:F1:73:6F:94:D9", debug=True) 
# HRM = HeartRate("E9:E3:B8:EC:D4:64", debug=True) 
# HRM.main()

CSC = CSC("E9:E3:B8:EC:D4:64", debug=True)
# CSC = CSC(sys.argv[2], debug=True)
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
        # empty display data
        data_dict={"hrm": ["   ", 105, 52],\
                "speed": ["    ", 62, 82],\
                "cadence": ["   ", 25, 52]}

        draw_in_quardrant(OLED, display_trip, 2, 0.5, 18)
        draw_in_quardrant(OLED, display_timedate, 1, 0.5, 18)
        draw_in_quardrant(OLED, display_data, 3, 0.5, 18, **data_dict)

        data_dict["hrm"][0] = HRM.__str__().strip()
        data_dict["speed"][0], data_dict["cadence"][0] = CSC.__str__().strip().split(",")

        speed = data_dict["speed"][0]

        # print ", ".join([hrm, speed, cadence])
        draw_in_quardrant(OLED, display_data, 3, 0.5, 18, **data_dict)
        
        if counter == 60:
            write_thingspeak([1, 2, 3], [value[0] for (key, value) in data_dict.iteritems()])
            counter = 0
        counter += 1
        time.sleep(1)
    OLED.setColor(0xFF)
    OLED.write_command("BGC", 0x00)
except KeyboardInterrupt:
    OLED.flush()
    HRM.unsubscribe()
    HRM.disconnect()
    CSC.unsubscribe()
    CSC.disconnect()
