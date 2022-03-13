#!/usr/bin/env python
import time, serial, urllib2, base64, syslog

# Print debug message
def print_debug(message):
    global conf_debug
    syslog.syslog(syslog.LOG_DEBUG, str(message))
    if (conf_debug):
        print("Debug: " + str(message))

# Print info message
def print_info(message):
    syslog.syslog(syslog.LOG_INFO, str(message))
    print(str(message))

# Print error message
def print_error(message):
    syslog.syslog(syslog.LOG_ERR, str(message))
    print("Error: " + str(message))

# Send command to serial device
# device [serial.Serial Object], command [string] - AT command
def sendCommand(device,command):
    command = str(command) + "\r\n"
    print_debug("Serial line - write data: " + command)
    device.write(command)
    time.sleep(0.5)  #give the serial port sometime to receive the data
    numOfLines = 0
    while True:
        response = device.readline()
        if (response != b''):
            print_debug("Serial line - read data: " + response)
        numOfLines = numOfLines + 1
        if (numOfLines >= 5):
            break

# Load config
def load_config():
    # conf_debug ... False/True, False - no debug messages | True - print debug messages
    global conf_debug

    # conf_serialLine ... device handler to serial line - for example /dev/ttyU0 or /dev/tty.usbserial-A6003MBV

    conf_debug = True
    conf_serialLine = "/dev/tty.usbserial-A6003MBV"
    

# Main handler
def main():
    load_config()

    ser = serial.Serial()
    ser.port = conf_serialLine
    ser.baudrate = 19200
    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    ser.parity = serial.PARITY_NONE #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    #ser.timeout = None          #block read
    #ser.timeout = 0             #non-block read
    ser.timeout = 1             # timeout 1 second for read
    ser.writeTimeout = 1     #timeout 1 second for write
    ser.xonxoff = False     #disable software flow control
    ser.rtscts = False     #disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control

    try:
        ser.open()
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput()#flush output buffer, aborting current output

        if ser.isOpen():
            try:
                print_info("Get Wattson serial number ...")
                sendCommand(ser,"nows\r\n")
                time.sleep(2)

            except Exception, e1:
                print_error("error communicating...: " + str(e1))
        else:
            print_error("cannot open serial port ")

    except Exception, e:
        print_error("Exception:" + str(e))
        exit()

    finally:
        print_info('Close the line\n')
        if ser.isOpen():
            ser.close()

main()
