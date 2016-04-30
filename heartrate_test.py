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
            return int(reduce(lambda x,y:x+y, rval[5:7]), 16)

    def connect(self):
        # connect device
        self.con.sendline('connect')
        # test for success of connect
        self.con.expect('Connection successful')
        if self.debug:
            print "connect successful"

    def subscribe(self):
        # write 0100 to handle to enable notification
        self.char_write_cmd(0x0018, 0100)
        exit_flag = self.con.expect('successfully')

        if exit_flag == 0: # no error
            return 0
    
    def unsubscribe(self):
        self.char_write_cmd(0x0018, 0000)

    def disconnect(self):
        self.con.sendline('disconnect')
        self.con.sendline('exit')
        if self.con.isalive():
                self.con.sendline('exit')

        # wait one second for gatttool to stop
        for i in range(100):
            if not self.con.isalive(): break
            time.sleep(0.01) 
            
        self.con.close()

    def __str__(self):
        try:
            pnum = self.con.expect('Notification handle = .*')
        except pexpect.TIMEOUT:
            print "TIMEOUT exception"
            break
        if pnum == 0: # no error
            self.rval = self.con.after.split()
            return print_heartrate(self)
        else:
            return -1


if __name__ == "__main__":
    HRM = HeartRate(sys.argv[1], debug=True) 
    HRM.connect()
    HRM.subscribe()
    try:
        while True:
            print HRM
    except KeyboardInterrupt:
        HRM.unsubscribe()
        HRM.disconnect()
