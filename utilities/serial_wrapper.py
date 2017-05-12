import serial               #allows us to open communications with arduino
import time
import datetime
import sys

from colorama_wrapper import *
from config_loader import *
from numerical import *

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')      

    
def get_arduino_port():

    '''
    This function selects the first arduino that is plugged into the
    serial port. If multiple Arduinos are detected it will select the first and
    warn the user.
    If no arduinos are present it will raise an IOError
    
    The code is from: http://stackoverflow.com/a/40531041/2727632
    '''

    import warnings
    import serial
    import serial.tools.list_ports

    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'Arduino' in p.description
    ]
    if not arduino_ports:
        raise IOError("No Arduino found")
    if len(arduino_ports) > 1:
        warnings.warn('Multiple Arduinos found - using the first')
        print 'Ardunio ports:', *arduino_ports
        

    return arduino_ports[0]

def init_serialport(port, logfile = None, ID = None):
    """
    Open communications with the arduino;
    quits the program if no communications are 
    found on port.
    
    If there are communications the script
    waits 500 ms then reads all incoming
    lines from the Serial port. These two
    lines include the arduino code version 
    and a string that says the arduino is online
    """
    
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.timeout = 1
    ser.port = port

    try: 
        ser.open()
        print colour("\nContact", style = (fGREEN, sBRIGHT))
        
    except serial.serialutil.SerialException: 
        print colour("No communications on %s" %port,  style = (fRED, sBRIGHT))
        sys.exit(0)
    
    #IDLE while Arduino performs it's setup functions
    print "AWAITING ARDUINO: "
    _ = 0
    while not ser.inWaiting():
        if not _%10000:
            print "-"*int(_/10000),"\r",
        _ += 1
    print "\nARDUINO ONLINE"
    
    # Buffer for 500 ms to let Arduino finish it's setup
    time.sleep(.5)
    # Log the debug info for the setup
    while ser.inWaiting(): 
        Serial_monitor(ser, logfile, True, ID = ID)

    return ser

def Serial_monitor(ser, logfile, show = True, ID = None, verbose = None):
    '''
    Reads from the serial port one line at time.
    '''
    line = ser.readline()

    if line:

        fmt_line = "%s,%s" %(line.strip(), timenow())
        if line.startswith("\t#"): 
            fmt_line = "#" + fmt_line
            if verbose: print colour(fmt_line, style = (fCYAN, sBRIGHT))
        if not line.startswith("-"): 
            #this adds a series of spaces to inset values in the log
            fmt_line = 4*' ' + fmt_line 
        
        elif show: 
            print colour("%s\t%s" %(timenow(), ID), style = (fWHITE,)),
            print colour(line.strip(), style = (fYELLOW, sBRIGHT))

        with open(logfile, 'a') as log:
            log.write(fmt_line + "\n")

    return line

def Continuous_monitor_arduino(ser, end_trial_msg = "- Status: Ready", 
                        sep = ':',
                        debug_flags = ("#",),
                        ID = None,
                        verbose = None,
                        logfile = None,
                        ):

    '''
    continously loops through messages from the serial monitor
    until the end_trial_msg is recieved.
    messages that are not preceded by debug_flags are stored in a
    dictionary which is returned by this function.
    '''
    
    line = Serial_monitor(ser, logfile, False, ID = ID, verbose = verbose)
    trial_dict = {}
    while line.strip() != end_trial_msg:
        # keep running until arduino reports it has broken out of loop
        line = Serial_monitor(ser, logfile, False, ID = ID, verbose = verbose)
        if line:
            if any([d in line for d in debug_flags]):
                continue
                
            var, val = line.strip().split(sep)
            trial_dict[var] = num(val)
    
    return trial_dict

def update_bbox(ser, params, logfile, trial_df = {}, ID = None, verbose = None):
    """
    Communicates the contents of the dict `params` through
    the serial communications port. 
    
    data is sent in the form: `parmas[key] = value`  --> `key:value`
    
    trail_df dictionary is updated to include the parameters 
    received from the arduino
    """
    write_out_config(params, ID)
    
    for name, param in params.iteritems():
    
        print fYELLOW, sBRIGHT, name[:2], "\r",
        ser.writelines("%s:%s" %(name, param))
        if verbose: print "%s:%s" %(name, param)
        
        time.sleep(0.1)
        
        while ser.inWaiting():

            line = Serial_monitor(ser, logfile, False, ID = ID, verbose = verbose)[:-1]
            
            if line[:2] not in ("\t#", "- "):
                var, val = line.strip().split(":")
                trial_df[var] = num(val)
                if var == name:
                    #pass
                    print  "\r", fGREEN, "\t", var[:2], val, sRESET_ALL , "\r",
                else:
                    print  fRED, "\r", var, val, sRESET_ALL ,
                    quit()

    return trial_df
