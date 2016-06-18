echo 254 > /sys/class/gpio/export
echo 222 > /sys/class/gpio/export
echo 214 > /sys/class/gpio/export
echo low > /sys/class/gpio/gpio214/direction
echo high > /sys/class/gpio/gpio254/direction
echo in > /sys/class/gpio/gpio222/direction
echo mode1 > /sys/kernel/debug/gpio_debug/gpio182/current_pinmux
echo high > /sys/class/gpio/gpio214/direction 
