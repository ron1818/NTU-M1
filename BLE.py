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

class HeartRate(object):
    """connect heartrate BLE device to edison and read heart rate """

    def __init__(self, bluetooth_adr, debug=False):

        # connect to gatttool, -I (--interactives) -t random
        self.con = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' -I -t random')
        self.debug = debug

        # expect LE: low energy
        self.con.expect('\[LE\]>')
        if self.debug:
            print "Preparing to connect. You might need to press the side button..."

    def char_write_cmd(self, handle, value):
        cmd = 'char-write-cmd 0x%04x 0%x' % (handle, value)
        if self.debug:
            print cmd
        self.con.sendline(cmd)

    def char_read_uuid(self, uuid, expected):
        cmd = 'char-read-uuid 0x%04x' % uuid
        if self.debug:
            print cmd
        self.con.sendline(cmd)
        if type(expected) is str:
            self.con.expect(expected)
        elif type(expected) is int:
            self.con.expect("0x%04x" % expected)

    def print_heartrate(self):
        if self.rval is not None:
            return int(reduce(lambda x,y:x+y, self.rval[5:7]), 16)

    def connect(self):
        # connect device
        self.con.sendline('connect')
        # test for success of connect
        self.con.expect('Connection successful')
        if self.debug:
            print "connect successful"

    def subscribe(self):
        # write 0100 to handle to enable notification
        self.char_write_cmd(0x0018, 0x0100)
        # exit_flag = self.con.expect('successfully')

        # if exit_flag == 0: # no error
        #     return 0
    
    def unsubscribe(self):
        self.char_write_cmd(0x0018, 0x0000)

    def disconnect(self):
        self.con.sendline('disconnect')
        self.con.sendline('exit')
        if self.con.isalive():
                self.con.sendline('exit')

        # wait one second for gatttool to stop
        for i in range(100):
            if not self.con.isalive(): 
                break
            time.sleep(0.01) 
            
        self.con.close()

    def __str__(self):
        try:
            pnum = self.con.expect('Notification handle = .*')
        except pexpect.TIMEOUT:
            print "TIMEOUT exception"
            
        if pnum == 0: # no error
            self.rval = self.con.after.split()
            return "%3d" % (self.print_heartrate())
        else:
            return "-1"

    def main(self):
        self.connect()
        self.subscribe()
        try:
            while True:
                print self.__str__()
                time.sleep(1)
        except KeyboardInterrupt:
            self.unsubscribe()
            self.disconnect()



class CSC(HeartRate):
    """ Other functions inherited from parent """
    def __init__(self, bluetooth_adr, perimeter=2055, debug=False):
        super(CSC, self).__init__(bluetooth_adr, debug)
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

        if delta_w_t == 0:
            return 0
        else:
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

        if delta_c_t == 0:
            return 0
        else:
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
        
    def __str__(self):
        self.past_data = self.current_data
        try:
            pnum = self.con.expect('Notification handle = .*')
        except pexpect.TIMEOUT:
            print "TIMEOUT exception"
        if pnum == 0: # no error
            self.rval = self.con.after.split()
            self.current_data = self.parse_data()
            speed, cadence = self.cal_speed(), self.cal_cadence()
            return "%2.1f,%3d" % (speed, cadence)
        else:
            return "-1, -1"


    def main(self):
        self.connect()
        self.subscribe()
        try:
            while True:
                print self.__str__()
                time.sleep(1)
        except KeyboardInterrupt:
            self.unsubscribe()
            self.disconnect()


if __name__ == "__main__":
    HRM = HeartRate(sys.argv[1], debug=True) 
    # HRM.main()
    
    CSC = CSC(sys.argv[2], debug=True)
    # CSC.main()
    HRM.connect()
    HRM.subscribe()
    CSC.connect()
    CSC.subscribe()
    try:
        while True:
            print HRM 
            print CSC
            time.sleep(1)
    except KeyboardInterrupt:
        HRM.unsubscribe()
        HRM.disconnect()
        CSC.unsubscribe()
        CSC.disconnect()
