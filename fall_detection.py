
# from wiringx86 import GPIOEdison as GPIO
import time
import subprocess

def fall_detection_sys(fallIn=5):
    """ pin 5: gpio13,
        pin 11: gpio43"""

    if fallIn == 11:
        a = subprocess.check_output("cat /sys/class/gpio/gpio43/value", shell=True)
    else:
        a = subprocess.check_output("cat /sys/class/gpio/gpio13/value", shell=True)
    return int(a[0])
    

def fall_detection_wiringx86(fallIn=5):
    # Create a new instance of the GPIOEdison class.
    # Setting debug=True gives information about the interaction with sysfs.
    gpio = GPIO(debug=False)

    # print 'Setting up pins %d ...' % (fallIn)


    # Set pin 5 to be used as an input GPIO pin.
    gpio.pinMode(fallIn, gpio.INPUT)

    # print 'Reading from pin %d now...' % fallIn
    try:
        while(True):
            # Read the state of the button
            state = gpio.digitalRead(fallIn)

            # If the button is pressed turn ON pin 13
            if state == 1:
                # print "fall"
                yield 1

            # If the button is not pressed turn OFF pin 13
            else:
                # print "no fall"
                yield 0

    # Kill the loop with Ctrl-C.
    except KeyboardInterrupt:
        # Leave the led turned off.
        # print '\nCleaning up...'

        # Do a general cleanup. Calling this function is not mandatory.
        gpio.cleanup()

if __name__ == "__main__":
    while True:
        print fall_detection_sys(11)
        time.sleep(1)
