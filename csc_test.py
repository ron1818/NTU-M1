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

bluetooth_adr = sys.argv[1]
tool = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' -I -t random')
tool.expect('\[LE\]>')
print "Preparing to connect. You might need to press the side button..."
tool.sendline('connect')
# test for success of connect
tool.expect('Connection successful')
print "connect successful"
tool.sendline('char-read-uuid 0x2902')
tool.expect('0x0018')
print "found 0x0018"
tool.sendline('char-write-req 0x0018 0100')
# tool.expect('successfully')
# print "successfully"
while True:
    tool.expect('Notification handle = .*')

    rval = tool.after.split()
    wheel_rev = int(reduce(lambda x,y:x+y, rval[9:5:-1]), 16)
    last_wheel_event = int(reduce(lambda x,y:x+y, rval[11:9:-1]), 16)
    crank_rev = int(reduce(lambda x,y:x+y, rval[13:11:-1]), 16)
    last_crank_event = int(reduce(lambda x,y:x+y, rval[15:13:-1]), 16)

    print "wheel rev %d, last wheel event %d, crank rev %d, last crank event %d"\
    % (wheel_rev, last_wheel_event, crank_rev, last_crank_event)


