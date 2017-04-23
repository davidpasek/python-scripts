#!/usr/bin/env python
import time, serial, urllib2, base64, syslog

# Print debug message
def print_debug(message):
    global debug
    syslog.syslog(syslog.LOG_DEBUG, str(message))
    if (debug):
        print("Debug: " + str(message))

# Print info message
def print_info(message):
    syslog.syslog(syslog.LOG_INFO, str(message))
    print(str(message))

# Print error message
def print_error(message):
    syslog.syslog(syslog.LOG_ERR, str(message))
    print("Error: " + str(message))

# Send AT command to serial devicea
# device [serial.Serial Object], command [string] - AT command
def sendATcommand(device,command):
    command = str(command) + "\r\n"
    print_debug("write data: " + command)
    device.write(command)
    time.sleep(0.5)  #give the serial port sometime to receive the data
    numOfLines = 0
    while True:
        response = device.readline()
        if (response != b''):
            print_debug("read data: " + response)
        numOfLines = numOfLines + 1
        if (numOfLines >= 5):
            break

# Send Pulse to ControlByWeb X-310
# ip [string] - IP address, username [string], password [string], relay [int] - 1,2,3,4
def sendCBWpulse(ip,username,password,relay):
    # Pulse Relay1 - http://ip_address/state.xml?relay1State=2
    # Pulse Relay2  - http://ip_address/state.xml?relay2State=2
    print_info("Send pulse to CBW " + ip + " - Relay " + str(relay))
    url = "http://" + ip + "/state.xml?relay" + str(relay) + "State=2"
    print_debug(url)
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)

# Return true if phone number is authorized to open gate
def is_authorized(phone_number):
    for n in conf_authorized_phone_numbers:
        if (phone_number == n):
            return True
    return False

# Load config
def load_config():
    # dryrun ... False/True, False - execute real actions | True - don't perform real actios
    global dryrun
    # debug ... False/True, False - no debug messages | True - print debug messages
    global debug
    # Authorized phone numbers
    global conf_authorized_phone_numbers
    # ControlByWeb config
    global conf_cbw_ip
    global conf_cbw_username
    global conf_cbw_password

    dryrun = True
    debug = True
    conf_authorized_phone_numbers = ['+420602525736']
    conf_cbw_ip = '192.168.4.5'
    conf_cbw_username = 'cbw'
    conf_cbw_password = '3377'

# Main handler
def main():
    load_config()

    ser = serial.Serial()
    ser.port = "/dev/ttyU0"
    ser.baudrate = 9600
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
                print_info("Modem initialization ...")
                sendATcommand(ser,"atz\r\n")
                time.sleep(2)
                sendATcommand(ser,"at+clip=1\r\n")
                time.sleep(2)

                print_info("Waiting for incoming call ...")
                while True:
                    data = ser.readline()
                    if (data != b''):
                        print_debug("read data: " + data)
                    if (data == b'RING\r\n'):
                        print_info("Incoming call ...")
                    if (data[:6] == b'+CLIP:'):
                        # Identify caller
                        clip=data[7:]
                        parts = clip.split(",")
                        caller_phone_number = parts[0]
                        caller_phone_number = caller_phone_number.lstrip('"');
                        caller_phone_number = caller_phone_number.rstrip('"');
                        print_info("Caller phone number ... " + caller_phone_number)
                        if (is_authorized(caller_phone_number)):
                            print_info("Pulse fence relay for " + caller_phone_number)
                            # relay1-garage, relay2-fence
                            if not dryrun:
                                sendCBWpulse(conf_cbw_ip,conf_cbw_username,conf_cbw_password,2)
                            else:
                                print_info("Dry run.")
                        else:
                            print_info("Phone number " + caller_phone_number + " is not authorized to open gate")
                        sendATcommand(ser,"ath\r\n")
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
