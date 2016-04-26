// Pin-out using I2C
// Raspberry Pi         -- Digole LCD
//         1 - 3.3.v        --  5 VCC
//        3 - SDA0        --    4 DATA     
//        5 - SCL0        --    3 SCK
//        6 - GND            --    1 GND
/*

// Communication set up command
* "SB":Baud (ascII bytes end with 0x00/0x0A/0x0D) -- set UART Baud Rate
* "SI2CA":Address(1 byte <127) -- Set I2C address, default address is:0x27
* "DC":1/0(1byte) -- set config display on/off, if set to 1, displayer will display current commucation setting when power on
// Text Function command
* "CL": -- Clear screen--OK
* "CS":1/0 (1 byte)-- Cursor on/off
* "TP":x(1 byte) y(1 byte) -- set text position
* "TT":string(bytes) end with 0x00/0x0A/0x0D -- display string under regular mode
// Graphic function command
* "GP":x(1byte) y(1byte) -- set current graphic position
* "DM":"C/!/~/&/|/^"(ASCII 1byte) -- set drawing mode--C="Copy",! and ~ = "Not", & = "And", | = "Or", ^ = "Xor"
* "SC":1/0 (1byte) -- set draw color--only 1 and 0
* "LN":x0(1byte) y0(1byte) x1(1byte) y2(1byte)--draw line from x0,y0 to x1,y1,set new pot to x1,y1
* "LT":x(1byte) y(1byte) -- draw line from current pos to x,y
* "CC":x(1byte) y(1byte) ratio(byte) -- draw circle at x,y with ratio
* "DP":x(1byte) y(1byte) Color(1byte) -- draw a pixel--OK
* "DR":x0(1byte) y0(1byte) x1(1byte) y2(1byte)--draw rectangle, top-left:x0,y0; right-bottom:x1,y1
* "FR":x0(1byte) y0(1byte) x1(1byte) y2(1byte)--draw filled rectangle, top-left:x0,y0; right-bottom:x1,y1
*/

#include <stdio.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    int fd;                                                
    char *fileName = "/dev/i2c-1";        // Name of the port we will be using, Rasberry Pi model B (i2c-1)
    int  address = 0x27;                // Address of I2C device
    char buf[100];                                        
    
    if ((fd = open (fileName, O_RDWR)) < 0) {    // Open port for reading and writing
        printf("Failed to open i2c port\n");
        exit(1);
    }
    if (ioctl(fd, I2C_SLAVE, address) < 0) {    // Set the port options and set the address of the device
        printf("Unable to get bus access to talk to slave\n");
        exit(1);
    }    
    if (argc>1)
    {
        sprintf(buf,argv[1]);
        //printf("%s %d %s\n",buf,strlen(buf),buf[strlen(buf)]);
        if ((write(fd, buf, strlen(buf)+1)) != strlen(buf)+1) {    
            printf("Error writing to i2c slave\n");
            exit(1);
        }
    } else {    
        printf(" Simple tool to send commands to Digole graphic adapter\nexamples:\n");                                
        printf(" rpi_lcd \"CLTTHello Word\" - Clear the screen (CL) and prints \"Hello Word\" (TT)\n");                                
        printf(" rpi_lcd \"CC002\" - Draws a cirle at x=30 (0), y=30 (0) with a radio of 32 (2)\n");    //not for Character LCD                                
    }    
    return 0;
}
