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
  response = ""
  print_debug("Serial line - write data:" + command)
  device.write(command.encode())
  time.sleep(0.5)  #give the serial port sometime to receive the data
  numOfLines = 0
  while True:
    response_c = device.readline()
    if (response_c != b''):
      response_d = response_c.decode()
      response = response_d[1:-2]
      print_debug("Serial line - read data:" + response + "\n")
    numOfLines = numOfLines + 1
    if (numOfLines >= 5):
      break
  return response 

###########################################################
# Convert hex to string
###########################################################
def hex_to_string(hex):
    if hex[:2] == '0x':
        hex = hex[2:]
    string_value = hex.upper();
    return string_value

###########################################################
# Load config
###########################################################
def load_config():
  # conf_debug ... False/True, False - no debug messages | True - print debug messages
  global conf_debug

  # conf_serialLine ... device handler to serial line - for example /dev/ttyU0
  global conf_serialLine

  conf_debug = False
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
  ser.timeout = 0.5             # timeout 1 second for read
  ser.writeTimeout = 0.5     #timeout 1 second for write
  ser.xonxoff = False     #disable software flow control
  ser.rtscts = False     #disable hardware (RTS/CTS) flow control
  ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
  
  ser.open()
  ser.flushInput()  #flush input buffer, discarding all its contents
  ser.flushOutput() #flush output buffer, aborting current output

  if ser.isOpen():
    print_debug("Get Wattson serial number ...")
    serial_number = sendCommand(ser,"nows")
    print_debug(serial_number)

    # NUMBER OF STORED DAYS
    #######################
    print_debug("Get number of days of data stored except the day going on ...")
    days_stored_string = sendCommand(ser,"nowd")
    days_stored = int(days_stored_string, 16)
    today = str(days_stored)
    print_info("Today:" + today)

    # CURRENT POWER USAGE
    #####################
    print_info("Get current power usage ...")
    command = "nowp"
    current_power_usage_hex_string = sendCommand(ser,command)
    power = int(current_power_usage_hex_string, 16)
    print(power)

    # LATEST STORED POWER READINGS
    ##############################
    command = "nowl" + today + "12";
    print_info("Get the latest stored power readings " + command + " ...")
    power_readings_string = sendCommand(ser,command)
    print_debug(power_readings_string)

    power_readings = power_readings_string.split(",")
    for power_hex_str in power_readings:
      if (len(power_hex_str) == 4):
        power = int(power_hex_str, 16)
        print(power)

  else:
    print_error("cannot open serial port ")

main()
