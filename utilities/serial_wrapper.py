import serial               #allows us to open communications with arduino

def init_serialport(port, logfile = None):
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
        print colour("\nContact", fc.GREEN, style = Style.BRIGHT)
        
    except serial.serialutil.SerialException: 
        print colour("No communications on %s" %port, fc.RED, style = Style.BRIGHT)
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
        Serial_monitor(ser, logfile, True)

    return ser

def Serial_monitor(ser, logfile, show = True):
    '''
    Reads from the serial port one line at time.
    '''
    line = ser.readline()

    if line:

        fmt_line = "%s,%s" %(line.strip(), timenow())
        if line.startswith("\t#"): 
            fmt_line = "#" + fmt_line
            if verbose: print colour(fmt_line, fc.CYAN, style = Style.BRIGHT)
        if not line.startswith("-"): 
            #this adds a series of spaces to inset values in the log
            fmt_line = 4*' ' + fmt_line 
        
        elif show: 
            if line.startswith("port") == False: #TODO remove this contingency, I don't think it is necessary
                print colour("%s\t%s\t%s" %(timenow(), port, ID), fc.WHITE),
                print colour(line.strip(), fc.YELLOW, style =  Style.BRIGHT)

        with open(logfile, 'a') as log:
            log.write(fmt_line + "\n")

    return line

def Continuous_monitor_arduino(end_trial_msg = "- Status: Ready", 
                        sep = ':',
                        debug_flags = (("#", "\t#", "- "))):

        '''
        continously loops through messages from the serial monitor
        until the end_trial_msg is recieved.
        messages that are not preceded by debug_flags are stored in a
        dictionary which is returned by this function.
        '''

        trial_dict = {}
        while line.strip() != end_trial_msg:
            # keep running until arduino reports it has broken out of loop
            line = Serial_monitor(ser, logfile, False)
            if line:
                if not line.startswith(debug_flags):
                    var, val = line.strip().split(sep)
                    trial_dict[var] = num(val)
        
        return trial_dict

def update_bbox(ser, params, logfile, trial_df = {}):
    """
    Communicates the contents of the dict `params` through
    the serial communications port. 
    
    data is sent in the form: `parmas[key] = value`  --> `key:value`
    
    trail_df dictionary is updated to include the parameters 
    received from the arduino
    """
    write_out_config(params)
    
    for name, param in params.iteritems():
    
        print fc.YELLOW, color.Style.BRIGHT, name[:2], "\r",
        ser.writelines("%s:%s" %(name, param))
        if verbose: print "%s:%s" %(name, param)
        
        time.sleep(0.1)
        
        while ser.inWaiting():

            line = Serial_monitor(ser, logfile, False)[:-1]
            
            if line[:2] not in ("\t#", "- "):
                var, val = line.strip().split(":")
                trial_df[var] = num(val)
                if var == name:
                    #pass
                    print  "\r", fc.GREEN, "\t", var[:2], val, Style.RESET_ALL , "\r",
                else:
                    print  fc.RED, "\r", var, val, Style.RESET_ALL ,
                    quit()

    return trial_df