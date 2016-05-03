# TRI_STATE_ALL buffer  
echo -n "214" > /sys/class/gpio/export  
# Pin 0 - Rx  
echo -n "130" > /sys/class/gpio/export # rx (input)  
echo -n "248" > /sys/class/gpio/export # output enable  
echo -n "216" > /sys/class/gpio/export # pullup enable  
#Pin 1 - TX  
echo -n "131" > /sys/class/gpio/export # tx (output)  
echo -n "249" > /sys/class/gpio/export # output enable  
echo -n "217" > /sys/class/gpio/export # pullup enable  
  
echo low > /sys/class/gpio/gpio214/direction # Set the TRI_STATE_ALL to low before doing any changes  
  
echo low > /sys/class/gpio/gpio248/direction  
echo in > /sys/class/gpio/gpio216/direction  
  
echo mode1 > /sys/kernel/debug/gpio_debug/gpio130/current_pinmux # mode1 is used to set the UART interface in Edison  
echo in > /sys/class/gpio/gpio130/direction  
  
echo high > /sys/class/gpio/gpio249/direction  
echo in > /sys/class/gpio/gpio217/direction  
  
echo mode1 > /sys/kernel/debug/gpio_debug/gpio131/current_pinmux # mode1 is used to set the UART interface in Edison  
echo out > /sys/class/gpio/gpio131/direction  
  
echo high > /sys/class/gpio/gpio214/direction # Set the TRI_STATE_ALL to high after the changes are applied  
