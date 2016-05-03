#!/usr/bin/env python
# Michael Saunby. April 2013   
# 
# Read temperature from the TMP006 sensor in the TI SensorTag 
# It's a BLE (Bluetooth low energy) device so using gatttool to
# read and write values. 
#
# Usage.
# sensortag_test.py BLUETOOTH_ADR
#
# To find the address of your SensorTag run 'sudo hcitool lescan'
# You'll need to press the side button to enable discovery.
#
# Notes.
# pexpect uses regular expression so characters that have special meaning
# in regular expressions, e.g. [ and ] must be escaped with a backslash.
#

import pexpect
import sys
import time
from heartrate_test import HeartRate

class CSC(HeartRate):
    """ Other functions inherited from parent """
    def __init__(self, bluetooth_adr, perimeter=2055, debug=False):
        sup(CSC, self).__init__(bluetooth_adr, debug)
        self.perimeter = perimeter
        self.current_data = self.past_data = \
               {"wheel_rev": 0,\
                "last_wheel_event": 0,\
                "crank_rev": 0,\
                "last_crank_event": 0}

    def delta(self, current, past, bits=16):
        Delta = current - past
        if Delta < 0:
            Delta += 2**bits
        return Delta

    def cal_speed(self):
        """ wheel rev, wheel last event time,
        speed m/s is perimeter (m) *revolution / delta T (s)
        delta T wraps at 2**16-1: 65535
        wheel_rev wraps at 2**32-1
        """
        current_rev, past_rev = self.current_data["wheel_rev"], \
                self.past_data["wheel_rev"]
        current_time, past_time = self.current_data["last_wheel_event"], \
                self.past_data["last_wheel_event"]
        delta_w_rev = self.delta(current_rev, past_rev, 32)
        delta_w_t = self.delta(current_time, past_time, 16)

        return self.perimeter * \
                delta_w_rev / delta_w_t * 3.6 * 1.024# (km/h)
        # perimeter mm need /1000 and delta t ms need /1024**-1,
        # finally they are canceled by a factor of 1.024

    def cal_cadence(self):
        """crank rev, crank last event time,
        cadence r/m is revolutin / delta T (min),
        delta T wraps at 2**16-1: 65535
        crank_rev wraps at 2**16-1
        """
        current_rev, past_rev = self.current_data["crank_rev"], \
                self.past_data["crank_rev"]
        current_time, past_time = self.current_data["last_crank_event"], \
                self.past_data["last_crank_event"]
        delta_c_rev = self.delta(current_rev, past_rev, 16)
        delta_c_t = self.delta(current_time, past_time, 16)

        return delta_c_rev / \
                (delta_c_t / 1024.0 / 60)  #(rpm)

    def parse_data(self):
        wheel_rev = int(reduce(lambda x,y:x+y, self.rval[9:5:-1]), 16)
        last_wheel_event = int(reduce(lambda x,y:x+y, self.rval[11:9:-1]), 16)
        crank_rev = int(reduce(lambda x,y:x+y, self.rval[13:11:-1]), 16)
        last_crank_event = int(reduce(lambda x,y:x+y, self.rval[15:13:-1]), 16)
        return {"wheel_rev": wheel_rev,\
                "last_wheel_event": last_wheel_event,\
                "crank_rev": crank_rev,\
                "last_crank_event": last_crank_event}
        
    def retrieve_data(self):
        self.past_data = self.current_data
        try:
            pnum = self.con.expect('Notification handle = .*')
        except pexpect.TIMEOUT:
            print "TIMEOUT exception"
            break
        if pnum == 0: # no error
            self.rval = self.con.after.split()
            self.current_data = parse_data(self)
            self.speed, self.cadence = \
                    self.cal_speed, self.cal_cadence
        else:
            return -1

