from __future__ import division

import pandas as pd
import datetime
import time
import os
import sys
import serial

import msvcrt as m
import numpy as np
from numpy.random import shuffle
import random

from itertools import product

import colorama as color # makes things look nice
from colorama import Fore as fc
from colorama import Back as bc     
from colorama import Style

from utilities.args import args
from utilities.numerical import num, na_printr, unpack_table

"""
1. The program starts
2. The program opens communications with available serial ports
3. The program starts a block
4. The program shuffles the stimuli (frequecies list)
5. The program transmits the frequenices to the stimbox
    -The stimbox cues the stimuli in memory
6. The program initiates a trial by sending a mode flag to
   the behaviour box.
   - The behaviour box runs one trial at a time; waiting
      for a flag from Serial each time
   - This means that inter-trial intervals must be controlled
     by the Serial controller. (this program)
   - This means this program must know when there is a timeout
     or not
7. The program records the output from behaviorCOMs into a
   behaviourdf.
8. The program repeats sending mode flags until all stimuli have
   been presented.
9. The program calculates d_prime|any_stimuls; d`|rising; d`|falling

--------------------------------------------------------------------
Arguments
--------------------------------------------------------------------
"""

verbose = args.verbose                # this will be a command line parameter
port = args.port                      # a command line parameter
ID = args.ID                          # the identity number of the animal
repeats = args.repeats                # number of repetitions
datapath = args.datapath              # a custom location to save data
weight = args.weight                  # the weight of the animal
trial_num = args.trial_num            # deprecated; for use if this continues a set of trials
trialDur = args.trialDur              # nominally the time to idle before resetting
blanks = args.blanks
bias_correct = args.bias_correct
ITI = args.ITI
freq = args.freq

leftmode =  args.left
rightmode = args.right

#----- shared paramaters -----
lickThres = int((args.lickThres/5)*1024)
mode = args.mode
punish = args.punish
timeout = args.timeout
lcount = args.lcount
noLick = args.noLick

t_stimONSET = args.t_stimONSET
t_stimDUR = args.t_stimDUR
t_rewardDEL = args.t_rDELAY
t_rewardDUR = args.t_rDUR

"""
--------------------------------------------------------------------
END Arguments
--------------------------------------------------------------------
"""
def menu():
    """
    Reads the characters in the buffer and modifies the program
    parameters accordingly
    
    TODO: On pause show current settings
    TODO: Allow an input mechanism to access all possible values
    TODO: make menu accept a dictionary or something and have it 
          return one as well!
            - Use the keys of the dictionary to allow tab 
              completion and scrolling of the inputs as well
                
    """
    print '\r                 \r',
    c = "\x00"
    if not m.kbhit():
        return {}
    
    global punish
    global lickThres
    global lcount
    global mode
    global rewardCond
    global comment
    global leftmode
    global rightmode
    global noLick
    global trialDur
    global single_stim
    global timeout
    global bias_correct
    global t_rDELAY
    global t_rDUR
    paused = True

    while paused:
        while m.kbhit():
            c = m.getch()
            if c == '\xe0': 
                c = c + m.getch()
        

            
            if c in ("\r", " "):
                paused = False
            
            # Toggle condition
            elif c in ("\t"):               
                if mode == "o": 
                    mode = "h"
                elif mode == "h": 
                    mode = "o"
                print "Training mode:\t%s" %mode
                
            elif c in ("C","c"): #m,Ctrl-m
                comment = raw_input("Comment: ")
                with open(logfile, 'a') as log:
                    log.write("Comment:\t%s\n" %comment)
                print "Choose...\r",
                
            elif c in '\xe0K':
                leftmode = True
                rightmode = False
                print "left mode:\t%s" %leftmode
            
            elif c in '\xe0M':
                rightmode = True
                leftmode = False
                print "right mode:\t%s" %rightmode
            
            elif c in ('\xe0P', '\xe0H'):
                leftmode = False
                rightmode = False
                print "random mode:\t", not (leftmode or rightmode)
            
            # Toggle punishment
            elif c in ("P", "p", "\x10"):
                punish = not punish
                #noLick = args.noLick if punish else 0
                print "Punish for wrong lick:\t%s" %punish
                with open(logfile, 'a') as log:
                    log.write("Punish for wrong lick:\t%s\n" %punish)
            
            # adjust the no lick period
            elif c in (":", ";"):
                noLick -= 10
                print "noLick:\t%3d\r" %noLick,
            
            elif c in ("\'", "\""):
                noLick += 10
                print "noLick:\t%3d\r" %noLick,
            
            elif c in ("l", "L"):
                print "noLick:\t%3d\r" %noLick,
                
            # adjust the trial duration
            elif c in ("9", "("):
                trialDur -= 1
                print "trialDur:\t%3d\r" %trialDur,
            
            elif c in ("0", ")"):
                trialDur += 1
                print "trialDur:\t%3d\r" %trialDur,
            
            elif c in ("T", "t"):
                print "TrialDur:\t%3d\r" %trialDur,

            elif c in ("y", "Y"):
                if timeout:
                    timeout = 0
                else:
                    timeout = args.timeout
                print "timeout:\t%3d\r" %timeout,
                
            # adjust minLickCount
            elif c in ("[", "{"):
                lcount -= 1
                print "minLickCount: %3d\r" %lcount,
            
            elif c in ("]", "}"):
                lcount += 1
                print "minLickCount: %3d\r" %lcount,
                
            elif c in ("|", "\\"):
                print "minLickCount: %3d\r" %lcount,

            # update lickThreshold....
            elif c in (",<"):
                lickThres -= 25
                print "lickThres: %4d .... %5.2f V\r" %(lickThres, (lickThres / 1024)*5),
            
            elif c in (".>"):
                lickThres += 25
                print "lickThres: %4d .... %5.2f V\r" %(lickThres, (lickThres / 1024)*5),
                
            elif c in ("/?"):
                print "lickThres: %4d .... %5.2f V\r" %(lickThres, (lickThres / 1024)*5),
            
            elif c in ('s', 'S'):
                single_stim = not single_stim
                print "Single stim:\t", single_stim,
            
            elif c in ('b', 'B'):
                bias_correct = not bias_correct
                print "Bias Correct:\t%s" %bias_correct, "%R|%L:", pc_R, "|", pc_L
                with open(logfile, 'a') as log:
                    log.write("bias_correct:\t%s\n" %bias_correct)
            
            elif 'rdur:' in c:
                val = c.split(':')[1]
                if val.strip().isdigit():
                    t_rDUR = val
                    print "t_rDUR:\t", t_rDUR
                else:
                    print 't_rDUR must be numerals ONLY'
                
            
            elif 'rdel:' in c:
                val = c.split(':')[1]
                if val.strip().isdigit():
                    t_rDELAY = val
                    print "t_rDELAY:\t", t_rDELAY
                else:
                    print 't_rDELAY must be numerals ONLY'

            elif c in ("h"):
                print color.Fore.LIGHTBLUE_EX, "\r",
                print "-----------------------------"
                print "options       :"
                print "  ...   H     : This menu"
                print "  ...   P     : Punish"
                print "  ...   S     : toggle single stimulus"
                print "  ...   < >   : lick threshold" 
                print "  ...   ?     : show threshold" 
                print "  ...   [ ]   : lickcount"
                print "  ...   \\     : show lickcount" 
                print "  ...   tab   : toggle mode"
                print "  ...   : \"   : adjust noLick period"
                print "  ...   L     : show noLick period"
                print "  ...   ( )   : adjust trial duration"
                print "  ...   T     : show trial duration period"
                print "  ...   Y     : toggle timeout (requires punish to take effect)"
                print "  ...   B     : toggle bias correction"
                print "input rdur:%i : set the reward duration"
                print "input rdel:%i : set the reward delay"
                print "-----------------------------"
                print color.Style.RESET_ALL, '\r',
                
            else:
                print "SPACE or ENTER to unpause"
            
    params = {
           'break_wrongChoice'         :    int(punish),
           'lickThres'                 :    lickThres,
           'minlickCount'              :    lcount,
           'mode'                      :    mode,
           't_noLickPer'               :    noLick,
           'timeout'                   :    int(timeout),
    }
    
    return update_bbox(ser, params, logfile, trial_df)

def colour (x, fc = color.Fore.WHITE, bc = color.Back.BLACK, style = color.Style.NORMAL):
    return "%s%s%s%s%s" %(fc, bc, style, x , color.Style.RESET_ALL)

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')      
      
def today():
    """provides today's date as a string in the form YYMMDD"""
    return datetime.date.today().strftime('%y%m%d')

def Serial_monitor(ser, logfile, show = True):
    
    line = ser.readline()
    
    if line:
        
        fmt_line = "%s\t%s\t%s\t%s" %(timenow(), port, ID, line.strip())
        
        if line.startswith("#"): 
            fmt_line = "#" + fmt_line
            if verbose: print colour(fmt_line, fc.CYAN, style = Style.BRIGHT)
        
        elif show: 
            if line.startswith("port") == False:
                print colour("%s\t%s\t%s" %(timenow(), port, ID), fc.WHITE),
                print colour(line.strip(), fc.YELLOW, style =  Style.BRIGHT)
    
        with open(logfile, 'a') as log:    
            log.write(fmt_line + "\n")
        
    return line

def update_bbox(ser, params, logfile, trial_df = {}):
    """
    Communicates the contents of the dict `params` through
    the serial communications port. 
    
    data is sent in the form: `dict[key] = value`  --> `key:value`
    
    trail_df dictionary is updated to include the parameters 
    received from the arduino
    """
    
    for name, param in params.iteritems():
    
        print fc.YELLOW, color.Style.BRIGHT, name[:2], "\r",
        ser.writelines("%s:%s" %(name, param))
        if verbose: print "%s:%s" %(name, param)
        
        time.sleep(0.1)
        
        while ser.inWaiting():

            line = Serial_monitor(ser, logfile, False).strip()

            if line[0] != "#" and line[0] != "-":
                var, val = line.split(":\t")
                trial_df[var] = num(val)
                if var == name:
                    #pass
                    print  "\r", fc.GREEN, "\t", var[:2], val, Style.RESET_ALL , "\r",
                else:
                    print  fc.RED, "\r", var, val, Style.RESET_ALL ,
                    quit()

    return trial_df

def create_datapath(DATADIR = "", date = today()):
    """
    
    """
    
    if not DATADIR: 
        DATADIR = os.path.join(os.getcwd(), date)
    else: 
        DATADIR = os.path.join(DATADIR, date)
    
    if not os.path.isdir(DATADIR):
        os.makedirs((DATADIR))
    
    print colour("datapath:\t", fc = fc.GREEN, style=Style.BRIGHT),
    print colour(DATADIR, fc = fc.GREEN, style=Style.BRIGHT)
    
    return DATADIR        
  
def create_logfile(DATADIR = "", date = today()):
    """
    
    """
    filename = "%s_%s_%s.log" %(port,ID,date)
    logfile = os.path.join(DATADIR, filename)
    print colour("Saving log in:\t", fc = fc.GREEN, style=Style.BRIGHT),
    print colour("./$datapath$/%s" %filename, fc = fc.GREEN, style=Style.BRIGHT)
    
    return logfile
                    
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

def habituation_run():
    #THE HANDSHAKE
    # send all current parameters to the arduino box to run the trial
    params = {
                'mode'          : mode,
                'lickThres'     : lickThres,
                'right_same'    : int(right_same),  #Converts to binary
                'DUR_short'     : dur_short,
                'DUR_long'      : dur_long,
                'single_stim'   : int(single_stim), #Converts to binary
                't_stimDELAY'   : t_stimDELAY
    }

    params = update_bbox(ser, params, logfile)
    
    print colour("trial count L count R\n"
                 "----- ------- -------", fc.MAGENTA, style = Style.BRIGHT)

    while mode == 'h':

        trial_df = {}
        line = Serial_monitor(ser, logfile, show = verbose).strip()

        trial_df['time'] = timenow()

        while line.strip() != "-- Status: Ready --":
            line = Serial_monitor(ser, logfile, False).strip()
            if line:
                if line[0] != "#" and line[0] != "-":
                    var, val = line.split(":\t")
                    trial_df[var] = num(val)
            menu()

        if 'response'  in trial_df.keys():

            with open(df_file, 'w') as datafile:

                for k, v in params.iteritems():
                    trial_df[k] = v

                trial_df = pd.DataFrame(trial_df, index=[trial_num])

                try: 
                    df = df.append(trial_df, ignore_index = True)
                except NameError:
                    df = trial_df

                df.to_csv(datafile)

            #Count percent L v R
            hab_df = df[df['mode'] == 'h']
            print colour("%s\t%4d" %(timenow(), hab_df.shape[0]), color, style = Style.BRIGHT)

"""
---------------------------------------------------------------------
                       MAIN FUNCTION HERE
---------------------------------------------------------------------
"""    

color.init()

datapath = create_datapath(datapath) #appends todays date to the datapath
logfile = create_logfile(datapath) #creates a filepath for the logfile

#make a unique filename
_ = 0
df_file = '%s/%s_%s_%03d.csv' %(datapath, ID, today(), _)
df = pd.DataFrame({'time':[], 'rewardCond':[], 'mode':[], 'response': []})
if os.path.isfile(df_file):
    df = df.append(pd.read_csv(df_file, index_col = 0))
   
df = df.dropna(subset = ['time'])
df = df.drop_duplicates('time')
comment = ""

requires_L = 0
requires_R = 0

# making the random condition in this way means 
# there are never more than 3 in a row

try:
    #open a file to save data in
    ser = init_serialport(port, logfile)

    # send initial paramaters to the arduino
    params = {
        'mode'              : 'h',
        'lickThres'         : lickThres,
        'break_on_early'    : int(0),
        'minlickCount'      : lcount,
        't_stimONSET'       : t_stimONSET,
    }
    
    trial_df = update_bbox(ser, params, logfile, {} )

    habituation_run()

except KeyboardInterrupt:

    try:
        print "attempting to create DataFrame"
        trial_df = pd.DataFrame(trial_df, index=[trial_num])
        
        try: 
            df = df.append(trial_df, ignore_index = True)
        except NameError:
            df = trial_df

        cumWater = df['WaterPort[0]'].cumsum() + df['WaterPort[1]'].cumsum()

        
        df['cumWater'] = cumWater               

        df.to_csv(df_file)
    except NameError:
        print "unable to create trial_df does not exist"
    except AttributeError:
        df.to_csv(df_file)
        print "saved df"

    print "Closing", port
    sys.exit(0)