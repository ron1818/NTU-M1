Intel Edison setup and learning
===============================

ren ye 2016-04-27

Ubuntu 14.04 LTS

Board connection
----------------
* two usb must be connected to computer
* microswitch must be down
* additional power supply is recommended

Arduino setup
-------------
* download from ardunio.cc for linux x64
* extract to a directory and run ./install.sh
* shortcut is on the desktop

ttyACM0 change ownership
------------------------
```bash
sudo usermod -a -G dialout <username>
sudo chmod a+rw /dev/ttyACM0
```

Serial connection
-----------------
```bash
sudo apt-get install screen
sudo screen /dev/ttyUSB0 115200
<ENTER>
```

New password: root:NTUitive

WiFi connection
---------------
`configure_edison --wifi`

Repository
----------
`vim etc/opkg/base-feeds.conf`

add following into:
```
src/gz all http://repo.opkg.net/edison/repo/all
src/gz edison http://repo.opkg.net/edison/repo/edison
src/gz core2-32 http://repo.opkg.net/edison/repo/core2-32
```

`opkg update`

BLE connection
--------------
###Install Gatttool###

```bash
cd ~
wget https://www.kernel.org/pub/linux/bluetooth/bluez-5.24.tar.xz –	no-check-certificate
tar -xf bluez-5.24.tar.xz
cd bluez-5.24
./configure --disable-systemd –disable-udev
make
make install
export PATH=$PATH:~/bluez-5.24/attrib/
```

###Scanning and discovering BLE devices with bluetoothctl###

First enable Bluetooth on the Intel Edison board.
`rfkill unblock bluetooth`

Launch bluetoothctl.
`bluetoothctl`

Register an agent and set it to default.
```bash
agent KeyboardOnOFF
default-agent
scan on
trust XX:XX:XX:XX:XX:XX
pair XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
info XX:XX:XX:XX:XX:XX

scan off
quit
```

###Use gatttool to read sensor values###
`gatttool -b 34:B1:F7:D5:15:38 -I -t random`

-I or --interactive

```bash
connect
primary
characteristics
char-read-uuid 0x2902
char-write-req 0x0018 0100
```
###ethernet over usb###
`sudo ifconfig usb0 192.168.2.2`

then edison's address is **192.168.2.15** or **edison.local**

*Note*: for first setup, only SSH over usb is enabled. Must run `configure_edison --setup` with
password and Wifi, then can SSH over wifi

###arduino expansion board UART###
`stty -F /dev/ttyMFD1 9600  # Replace "9600" with the baudrate you need`
change baud to 9600

Then, for setting up the gpio pins required for send and received data with the /dev/ttyMFD1 port, run the following commands in Linux terminal:

```bash
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
```

or simply save a `.sh` file and source that beforehand

SSH login without password
----

###Your aim###

You want to use Linux and OpenSSH to automate your tasks. Therefore you need an automatic login from host A / user a to Host B / user b. You don't want to enter any passwords, because you want to call ssh from a within a shell script.

###How to do it###

First log in on A as user a and generate a pair of authentication keys. Do not enter a passphrase:

```bash
a@A:~> ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/home/a/.ssh/id_rsa): 
Created directory '/home/a/.ssh'.
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/a/.ssh/id_rsa.
Your public key has been saved in /home/a/.ssh/id_rsa.pub.
The key fingerprint is:
3e:4f:05:79:3a:9f:96:7c:3b:ad:e9:58:37:bc:37:e4 a@A
Now use ssh to create a directory ~/.ssh as user b on B. (The directory may already exist, which is fine):
```
```bash
a@A:~> ssh b@B mkdir -p .ssh
b@B's password: 
```
Finally append a's new public key to b@B:.ssh/authorized_keys and enter b's password one last time:

```bash
a@A:~> cat .ssh/id_rsa.pub | ssh b@B 'cat >> .ssh/authorized_keys'
b@B's password:
```
From now on you can log into B as b from A as a without password:

```bash
a@A:~> ssh b@B
```

A note from one of our readers: Depending on your version of SSH you might also have to do the following changes:

Put the public key in `.ssh/authorized_keys2`
Change the permissions of `.ssh to 700`
Change the permissions of `.ssh/authorized_keys2 to 640`


References
-----------
https://software.intel.com/en-us/iot/library/edison-getting-started

http://arduino-er.blogspot.sg/2014/08/arduino-ide-error-avrdude-seropen-cant.html

https://software.intel.com/en-us/articles/using-the-generic-attribute-profile-gatt-in-bluetooth-low-energy-with-your-intel-edison

http://www.linuxproblem.org/art_9.html
