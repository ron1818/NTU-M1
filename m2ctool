#!/usr/bin/env node 
 
/*jslint node:true, vars:true, bitwise:true, unparam:true */
/*jshint unused:true */

/*
The MIT License (MIT)

Copyright (c) 2015, m2ag.labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/




var mraa = require('mraa'); //require mraa
var parseArgs = require('minimist'); 



var args = process.argv.slice(2); 

argv = parseArgs(args); 


console.log('MRAA Version: ' + mraa.getVersion()); //write the mraa version to the Intel XDK console
//console.log('Platform Type: ' + mraa.getPlatformType()); 
console.log('Platform Name: ' + mraa.getPlatformName()); 

var t;  //Will hold bus number.
var x;  //Will hold device object.

/*
    Determine which action. If parameters are incorrect give help. 
*/
switch(argv['_'][0]) {
        case 'scan' :
            if(!isValidBus() || argv['_'].length !== 2){
                help('scan'); 
            } else {
                scan(); 
            }
            break; 
        case 'dump' :
            if(!isValidBus() || argv['_'].length < 3){
                help('dump'); 
            } else {
                dump(argv['_'][2], argv['s'] === true, argv['l']); 
            }   
            break; 
        case 'get' :
            if(!isValidBus() || argv['_'].length < 4){
                help('get'); 
            } else {
                get(argv['_'][2], argv['_'][3], argv['s'] === true); 
            }     
            break;
        case 'set' :
            if(!isValidBus() || argv['_'].length < 5){
                help('set'); 
            } else {
                set(argv['_'][2], argv['_'][3], argv['_'][4], argv['s'] === true);
            }  
            break;
        case 'help' :
            if(argv['_'].length === 2){
                help(argv['_'][1]);
            } else {
                help(); 
            }   
            break; 
        default :
            console.log('default'); 
            help(); 
            break;
}
 

function help(type) {
    switch(type){
            case 'all' :
                console.log('m2ctool -- a tool to scan i2c buses on MRAA based systems');
                console.log('Some device info:'); 
                console.log('Intel Edison on mini-breakout board can use i2c bus 1 and 6');
                console.log('Intel Edison on Arduino board can use i2c bus 6'); 
                console.log('Intel Galileo can use i2c bus 0'); 
                console.log('Use of this script is at your own risk\n'); 
                console.log('Topic help is avaialble -- mctools help <scan|dump|get|set>');
            
            case 'scan' :
                console.log('scan for devices on an i2c bus');
                console.log('usage -- m2ctool scan <bus number>\n'); 
                if(type !== 'all') break; 
            case 'dump' : 
                console.log('dump  the registers of a device');
                console.log('usage -- m2ctool dump <bus number> <device address> <optional -s -l length>');
                console.log('where -s is swap byte order and -l is the number of registers to return (255 default)');
                console.log('example -- m2ctool dump 6 0x18 -s -l13\n');                         
                if(type !== 'all') break; 
            case 'get' : 
                console.log('get the value a register of a device');
                console.log('usage -- m2ctool get <bus number> <device address> <register address> <optional -s>'); 
                console.log('where -s is swap byte order\n'); 
                if(type !== 'all') break; 
            case 'set' :
                console.log('set the value of a device register');
                console.log('usage -- m2ctool set <bus number> <device address> <register address> <data>'); 
                //console.log('where -s is swap byte order'); 
                console.log('data should be in hexadecimal format\n'); 
                break; 
            default:  
                help('all'); 
                break; 
    }
}


function get(device , register, swap) {
 
    swap = typeof swap !== 'undefined' ? swap : false ;  
    
    var r; 

    x.address(parseInt(device)); 
    
    r = x.readWordReg(parseInt(register)); 
    if(swap){
        r =  swapbytes(r);     
    }
    
    console.log('0x' + pad(r.toString(16), 4));            
    
}

function set(device , register, data , swap ) {
    
    swap = typeof swap !== 'undefined' ? swap : false ;  
    
    //data = parseHex(data); 

    //if(swap){
    //    data =  swapbytes(data);     
    //}
    
    x.address(parseInt(device)); 
    
    console.log(x.writeWordReg(parseInt(register), parseInt(data))); 
   
}

function scan( ) {
  
    
    console.log("Scanning devices on bus");

    var string = "     "; 

    for(var l = 0 ; l < 16; l++){
        string += "  " + l.toString(16); 
    }

    console.log(string); 
    string = "00:  "; 

    for(var j = 0; j < 120; j++ ){
        x.address(j); 
        

        if( x.readWordReg(0) !== 0 ) {
            string += " " + j.toString(16); 
        } else {
            string += " --"; 
        }

        if(( j > 1 && (j + 1) % 16 === 0) || j == 119 ){
            console.log(string);
            var base = (j + 1)/ 16; 
            string = Math.round(base) +  "0:  " ; 
        }
    }
}

function dump( device , swap, length ) {
    
    length = typeof length !== 'undefined' ? length : 256 ; 
    swap = typeof swap !== 'undefined' ? swap : false ;  
    
    var r; 
    var string = "00: ";
    x.address(parseInt(device)); //Default for MCP9808 is 0x10
    console.log("Dumping device at 0x" + device.toString(16) + ( swap ? " bytes swapped" : "") + "\n");  
    console.log("     0,8  1,9  2,a  3,b  4,c  5,d  6,e  7,f"); 
    
    for(var i = 0; i < length  ;  i++){
        r = x.readWordReg(i); 
        if(swap){
            r =  swapbytes(r);     
        }
        
        string += pad(r.toString(16), 4) + " "; 
        
        if(i > 0 &&  (i + 1) % 8 === 0 || i === (length - 1)) {
            console.log(string);
            string = pad((i+1).toString(16) , 2) + ": " ; 
        }
                
    }   
}



function pad(str, len){
    while(str.length < len){
        str = '0' + str; 
    }
    return str; 
}

function swapbytes(byte){
    return ((byte & 0xFF) << 8) | ((byte >> 8 ) & 0xFF); 
}


function parseHex(hex) {
    
    console.log(hex); 
    return hex.replace(/\\x([a-fA-F0-9]{2})/g, function(a,b){
        return String.fromCharCode(parseInt(b,16));
    });
}

function isValidBus(){
    t = parseInt(args[1]); 
    if(isNaN(t)){
        return(false); 
    } else {
        try{
            x = new mraa.I2c(t);
            return(true); 
        } catch (ex) {
            console.log("No i2c bus found at " + t); 
            return(false); 
        }               
    }
}