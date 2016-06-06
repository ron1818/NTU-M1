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
OLED.clearScreen()
draw_in_quardrant(OLED, draw_gui_1, 3)
# draw_gui_1(OLED)

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
        data_dict={"hrm": ["   ", 105, 52],\
                "speed": ["    ", 62, 82],\
                "cadence": [25, 52]}

        display_data(OLED, **data_dict)
        # OLED.drawStr(105, 52, "   ")
        # OLED.drawStr(62, 82, "    ")
        # OLED.drawStr(25, 52, "   ")
        data_dict["hrm"][0] = HRM.__str__().strip()
        data_dict["speed"][0], data_dict["cadence"][0] = CSC.__str__().strip().split(",")
        # print ", ".join([hrm, speed, cadence])
        display_data(OLED, **data_dict)
        
        if counter == 60:
            write_thingspeak([1, 2, 3], [value[0] for (key, value) in a.iteritems()])
            counter = 0
        counter += 1
        time.sleep(1)
except KeyboardInterrupt:
    OLED.flush()
    HRM.unsubscribe()
    HRM.disconnect()
    CSC.unsubscribe()
    CSC.disconnect()
