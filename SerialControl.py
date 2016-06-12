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
auditory = args.auditory              # a binary, flags auditory (True) or somatosensory (False)
dur_short, dur_long = sorted(args.dur)
blanks = args.blanks
bias_correct = args.bias_correct
ITI = args.ITI

leftmode =  args.left
rightmode = args.right

#----- shared paramaters -----
lickThres = int((args.lickThres/5)*1024)
mode = args.mode
punish = args.punish
timeout = args.timeout
lcount = args.lcount
noLick = args.noLick
right_same = args.right_same
single_stim = args.single
t_rDELAY = args.t_rDELAY
t_rDUR = args.t_rDUR

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
    
    c = "\x00"
    if not m.kbhit():
        return
    
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
            c = raw_input("SPACE or ENTER to unpause: ")
                                
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
    
        print fc.YELLOW, name[:5], 
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
                    print  fc.GREEN, "\r", var[:5], val, Style.RESET_ALL , "\r",
                else:
                    print  fc.RED, "\r", var[:5], val, Style.RESET_ALL ,
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
                'auditory'      : int(auditory),    #Converts to binary
                'right_same'    : int(right_same),  #Converts to binary
                'dur_short'     : dur_short,
                'dur_long'      : dur_long,
                'single_stim'   : int(single_stim), #Converts to binary
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
            right = (hab_df.response == 'R').values[-1]
            left = (hab_df.response == 'L').values[-1]
            if hab_df.response.values[-1] == 'R':
                color = fc.CYAN
            elif hab_df.response.values[-1] == 'L':
                color = fc.RED
            print colour("%4d %7d %7d " %(len(hab_df), left, right), color, style = Style.BRIGHT)
            count_right = (hab_df.response == 'R').sum()
            count_left = (hab_df.response == 'L').sum()
            print colour("sum: %7d %7d " %(count_left, count_right), style = Style.BRIGHT), '\r',
    
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
    
    if mode == 'o':
        
        # loop for r repeats
        for r in xrange(repeats):

            pc_L = 50
            pc_R = 50
            
            if bias_correct and len(df) > 1:
                response_hist = df.response.str.upper().dropna().values[-25:]
                response_hist = response_hist[response_hist != '-']
                N = len(response_hist)
                
                if N:
                    left_licks = (response_hist == 'L').sum()
                    right_licks = (response_hist == 'R').sum()
                                      
                    pc_R = right_licks / N * 100
                    pc_L = left_licks / N * 100
                
                    pc_L = 100 - int(round(pc_L))
                    pc_R = 100 - int(round(pc_R))


            pc_B = 10 * blanks
            pc_L = int(pc_L - pc_B / 2)
            pc_R = int(pc_R - pc_B / 2)

            choice_set = ''.join(('L' * pc_L,
                                 'R' * pc_R, 
                                 '-' * pc_B,
                                ))
            randomCond = random.choice(choice_set)
            
            if not bias_correct and df.shape[0] > 3:                    
                if (df.rewardCond.values[-3:] == 'L').all():
                    randomCond = 'R'
                elif (df.rewardCond.values[-3:] == 'R').all():
                    randomCond = 'L'
       
           
            # Mechanism to prevent more than 5 correct in a row.
            # a softer bias correct mechanism
            if df.shape[0] > 5:

                if (df.response.dropna()[df.response.dropna().str.isupper()].values[-5:] == 'R').all() or requires_L:
                    randomCond = 'L'
                    print  "\t\trequires_L: ", requires_L,
                    if not requires_L:
                        requires_L = 3
                        requires_R = 0
                    else:
                        if df['WaterPort[0]'].astype(bool).values[-1]:
                            requires_L -= 1
                    if (df.response.dropna()[df.response.dropna().str.isupper()].values[-5:] == 'L').sum() > 2:
                        requires_L = 0
                        requires_R = 0
                    
                if (df.response.dropna()[df.response.dropna().str.isupper()].values[-5:] == 'L').all() or requires_R:
                    randomCond = 'R'
                    print  "\t\trequires_R: " , requires_R,
                    if not requires_R:
                        requires_R = 3
                        requires_L = 0
                    else:
                        if df['WaterPort[1]'].astype(bool).values[-1]:
                            requires_R -= 1
                        
                    if (df.response.dropna()[df.response.dropna().str.isupper()].values[-5:] == 'R').sum() > 2:
                        requires_R = 0
                        requires_L = 0
                        
                            
       
            
            print colour("".join(randomCond), fc.CYAN),
            
            # loop for number of trials in the list of random conditions
            for trial_num, rewardCond in enumerate(randomCond):
            
                # create an empty dictionary to store data in
                trial_df = {
                    'trial_num'      : trial_num,
                    'WaterPort[0]'   : 0,
                    'WaterPort[1]'   : 0,
                    'ID'             : ID,
                    'weight'         : weight,
                    'block'          : r,
                    'comment'        : comment,
                    'bias_correct': bias_correct,
                }
                
                #checks the keys pressed during last iteration
                #adjusts options accordingly
                
                menu()
                
                # apply the over-ride to the reward condition
                # if the over-ride has been specified
                if rewardCond == '-':
                    pass
                elif leftmode:
                    rewardCond = 'L'
                elif rightmode:
                    rewardCond = 'R'
                    
                trial_df['comment'] = comment
                            
                #THE HANDSHAKE
                # send all current parameters to the arduino box to run the trial
                params = {
                            'rewardCond'        : rewardCond,
                            'mode'              : mode,
                            'lickThres'         : lickThres,
                            'break_wrongChoice' : int(punish),      #Converts to binary
                            'minlickCount'      : lcount,
                            't_noLickPer'       : noLick,
                            'auditory'          : int(auditory),    #Converts to binary
                            'right_same'        : int(right_same),  #Converts to binary
                            'dur_short'         : dur_short,
                            'dur_long'          : dur_long,
                            'single_stim'       : int(single_stim), #Converts to binary
                            'timeout'           : int(timeout*1000),     #Converts back to millis
                            't_rDELAY'     : t_rDELAY,
                            't_rDUR'     : t_rDUR,
                }
                
                trial_df = update_bbox(ser, params, logfile, trial_df)
                
                print colour("C: %s" %params['rewardCond'], 
                                fc.MAGENTA, style = Style.BRIGHT),

                trial_df['time'] = timenow()
                
                # Send the literal GO symbol
                start_time = time.time()
            
                ser.write("GO")
                line = Serial_monitor(ser, logfile, show = verbose).strip()
                
                while line.strip() != "-- Status: Ready --":
                    # keep running until arduino reports it has broken out of loop
                    line = Serial_monitor(ser, logfile, False).strip()
                    if line:
                        if line[0] != "#" and line[0] != "-":
                            var, val = line.split(":\t")
                            #print  fc.GREEN, "\r", var[:5], val, Style.RESET_ALL , "\r",
                            trial_df[var] = num(val)
                         
                for k in trial_df.keys():
                    if type(trial_df[k]) == list: 
                        trial_df[k] = trial_df[k][0]
               
                """
                THAT WHICH FOLLOWS IS NOT NECESSARY TO RUN A TRIAL??
                """
                """
                #Save the data to a data frame / Save to a file
                """
                    
                with open(df_file, 'w') as datafile:
                    
                    trial_df = pd.DataFrame(trial_df, index=[trial_num])
                    
                    try: 
                        df = df.append(trial_df, ignore_index = True)
                    except NameError:
                        df = trial_df
                    
                    df['correct'] = df.response.isin(['L', 'R'])
                    df['miss'] = df.response[df.rewardCond != 'N'] == '-'
                    df['wrong'] = df.response[df.rewardCond != 'N'].str.islower()
                    
                    hits = df.correct.cumsum()
                    hit_L = df.correct[df.response == 'L'].cumsum()
                    hit_R = df.correct[df.response == 'R'].cumsum()
                    
                    cumWater = df['WaterPort[0]'].cumsum() + df['WaterPort[1]'].cumsum()
                    
                    df['hits'] =  hits
                    df['hit_L'] = hit_R
                    df['hit_R'] = hit_L
                    
                    df['cumWater'] = cumWater
                    df['trial_num'] = df.shape[0]

                    df.to_csv(datafile)
                
                #Print the important data and coloured code for hits / misses  
                print Style.BRIGHT, '\r', 
                
                table = {
                            'trial_num'    : 't', 
                            'mode'         : 'mode', 
                            'rewardCond'   : 'rewCond', 
                            'response'     : 'response', 
                            'count[0]'     : 'L', 
                            'count[1]'     : 'R', 
                            'WaterPort[0]' : 'waterL', 
                            'WaterPort[1]' : 'waterR',
                            'DUR[0]'       : 'DUR0', 
                            'DUR[1]'       : 'DUR1',
                }

                try:
                    if not pd.isnull(df['DUR[0]'].iloc[-1]):
                        for k in ('trial_num', 'rewardCond', 'response', 
                                        'count[0]', 'count[1]', 'WaterPort[0]', 
                                        'WaterPort[1]', 'DUR[0]', 'DUR[1]',):
                            
                            if df.correct.iloc[-1]:
                                print '%s%s:%s%4s' %(fc.WHITE, table[k], fc.GREEN, str(trial_df[k].iloc[-1]).strip()),
                            elif df.miss.iloc[-1]:
                                print '%s%s:%s%4s' %(fc.WHITE, table[k], fc.YELLOW, str(trial_df[k].iloc[-1]).strip()),
                            else:
                                print '%s%s:%s%4s' %(fc.WHITE, table[k],fc.RED, str(trial_df[k].iloc[-1]).strip()),
                        print '\r', Style.RESET_ALL
                        #calculate percentage success
                        
                        print "\r", 100 * " ", "\r                ", #clear the line 
                        
                        hits = (df.dropna(subset=["DUR[0]", "DUR[1]"]).correct.sum() 
                                        / df.dropna(subset=["DUR[0]", "DUR[1]"]).ID.size)
                        
                        if df.ID[df.rewardCond.isin(['L','B'])].count():
                             hit_L = ((df.response == 'L').values.sum() 
                                        / df.rewardCond.isin(['L','B']).values.sum())
                        else: hit_L = float('nan')
                        
                        if df.ID[df.rewardCond.isin(['R','B'])].count():
                             hit_R = ((df.response == 'R').values.sum() 
                                        / df.rewardCond.isin(['R','B']).values.sum())
                        else: hit_R = float('nan')
                        
                        if df.ID[df.rewardCond != 'N'].count():
                            misses = (df.miss.values.sum() / 
                                        df.ID[df.rewardCond != 'N'].values.size)*100
                        else: misses = float('nan')
                        
                        wrong = (df.wrong.dropna().sum() / df.wrong.dropna().size)*100
                        
                        misses = na_printr(misses)
                        wrong = na_printr(wrong)
                        hits =  na_printr(hits*100)
                        hit_L = na_printr(hit_L*100)
                        hit_R = na_printr(hit_R*100)
                        cumWater = df['WaterPort[0]'].sum() + df['WaterPort[1]'].sum()
                                        
                        print colour("hits:%03s%%  misses:%0s%%  wrong:%03s%%  R:%03s%%  L:%03s%%  Count:%4d  Water:%3d           " %(hits, misses, wrong, hit_R, hit_L, df.dropna(subset=["DUR[0]", 'response']).ID.count(), cumWater),
                                        fc = fc.YELLOW, bc = bc.BLUE, style = Style.BRIGHT), '\r',
                    
                except:
                    pass

                comment = ""
                trial_num += 1            
                
                # creates a set trial time if a duration has been flagged
                dur = time.time() - start_time
                if trialDur and not pd.isnull(df['DUR[0]'].iloc[-1]): #allows fall though for a non trial
                    #print np.isnan(df['DUR[0]'].iloc[-1]).all(),
                    print '\r',
                    while dur < trialDur:
                        dur = time.time() - start_time
                        

                wait = 0
                print Style.BRIGHT, fc.GREEN,
                if trial_df['response'].item() not in ('L', 'R', '-'):
                    wait = random.uniform(*ITI)
                    print fc.CYAN,
                if bias_correct:
                    print colour(''.join(('\r'," "*10,"BC: ", str(pc_R),"R",str(pc_L),"L\r")), fc = fc.YELLOW, bc = bc.RED, style = Style.BRIGHT),
                print "\rwait %2.2g s" %wait, Style.RESET_ALL,"\r",
                time.sleep(wait)
                print "             \r",
    
    #HABITUATION
    elif mode == 'h':
        habituation_run()

except KeyboardInterrupt:

    try:
        print "attempting to create DataFrame"
        trial_df = pd.DataFrame(trial_df, index=[trial_num])
        
        try: 
            df = df.append(trial_df, ignore_index = True)
        except NameError:
            df = trial_df
        
        df['correct'] = df.response.str.isupper()
        df['miss'] = df.response[df.rewardCond != 'N'] == '-'
        df['wrong'] = df.response[df.rewardCond != 'N'].str.islower()
        
        hits = df.correct.cumsum()
        hit_L = df.correct[df.response == 'L'].cumsum()
        hit_R = df.correct[df.response == 'R'].cumsum()
        
        cumWater = df['WaterPort[0]'].cumsum() + df['WaterPort[1]'].cumsum()
        
        df['hits'] =  hits
        df['hit_L'] = hit_R
        df['hit_R'] = hit_L
        
        df['cumWater'] = cumWater               

        df.to_csv(df_file)
    except NameError:
        print "unable to create trial_df does not exist"
    except AttributeError:
        df.to_csv(df_file)
        print "saved df"

    print "Closing", port
    sys.exit(0)