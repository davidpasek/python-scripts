#!/usr/bin/env python
#import time, serial, urllib2, base64, syslog
import sys, time, syslog, serial

###################################################
# Print debug message
###################################################
def print_debug(message):
  global conf_debug
  syslog.syslog(syslog.LOG_DEBUG, str(message))
  if (conf_debug):
    print("Debug: " + str(message))
    
###################################################
# Print info message
###################################################
def print_info(message):
  syslog.syslog(syslog.LOG_INFO, str(message))
  print(str(message))
    
###################################################
# Print error message
###################################################
def print_error(message):
  syslog.syslog(syslog.LOG_ERR, str(message))
  print("Error: " + str(message))
    
###########################################################
# Send command to serial device
# device [serial.Serial Object], command [string] - command
###########################################################
def sendCommand(device,command):
  command = str(command) + "\r"
  print_debug("Serial line - write data: " + command)
  device.write(command.encode())
  time.sleep(0.5)  #give the serial port sometime to receive the data
  numOfLines = 0
  while True:
    response = device.readline()
    if (response != b''):
      print_debug("Serial line - read data: " + response.decode())
    numOfLines = numOfLines + 1
    if (numOfLines >= 5):
      break

###########################################################
# Load config
###########################################################
def load_config():
  # conf_debug ... False/True, False - no debug messages | True - print debug messages
  global conf_debug

  # conf_serialLine ... device handler to serial line - for example /dev/ttyU0
  global conf_serialLine

  conf_debug = True
  conf_serialLine = "/dev/ttyU0"

###################################################
# Main handler
###################################################
def main():
  # Initialize syslog 
  syslog.openlog(sys.argv[0], syslog.LOG_PID, syslog.LOG_LOCAL0);

  # Load configuration
  print_info("Loading configuration")
  load_config();

  # Wattson
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
  
  ser.open()
  ser.flushInput()  #flush input buffer, discarding all its contents
  ser.flushOutput() #flush output buffer, aborting current output

  if ser.isOpen():
    print_info("Get Wattson serial number ...")
    sendCommand(ser,"nows")
  else:
    print_error("cannot open serial port ")

main()
