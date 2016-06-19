echo 43 > /sys/class/gpio/export
echo 262 > /sys/class/gpio/export
echo 241 > /sys/class/gpio/export
echo 259 > /sys/class/gpio/export
echo 227 > /sys/class/gpio/export
echo 214 > /sys/class/gpio/export
echo low > /sys/class/gpio/gpio214/direction
echo high > /sys/class/gpio/gpio262/direction
echo mode0 > /sys/kernel/debug/gpio_debug/gpio43/current_pinmux
echo low > /sys/class/gpio/gpio259/direction
echo in > /sys/class/gpio/gpio227/direction
echo in > /sys/class/gpio/gpio43/direction
echo high > /sys/class/gpio/gpio214/direction

