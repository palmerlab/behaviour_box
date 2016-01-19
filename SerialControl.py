from __future__ import division

import pandas as pd
import csv
import datetime
import time
import os
from shutil import copyfile # for duplicating config!
import sys
import glob
import serial
import argparse
import msvcrt as m
import numpy as np
from numpy.random import shuffle
import random
import re

from itertools import permutations, product
            
import colorama as color # makes things look nice
from colorama import Fore as fc
from colorama import Back as bc     
from colorama import Style


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

p = argparse.ArgumentParser(description="This program controls the Arduino and reads from it too" )

p.add_argument("-i", "--ID", default = "", help = "identifier for this animal/run")
p.add_argument("-w", "--weight", default = 0, help = "weight of the animal in grams")
p.add_argument("-m", "--mode", default = "c", help = "the mode `c`onditioning or `o`perant, by default will look in the config table")
p.add_argument('-f','--freq', nargs = '*', type = int, help = "list of frequencies in Hz (separated by spaces)")
p.add_argument('-r', '--repeats', default = "1000", type = int, help = "the number of times this block should repeat, by default this is 1")

p.add_argument('--datapath', default = "C:/DATA/wavesurfer", help = "path to save data to, by default is 'C:/DATA/wavesurfer/%%YY%%MM%%DD'")
p.add_argument("--port", default = "COM5", help = "port that the Arduino is connected to")
p.add_argument("--verbose", action = 'store_true', help = 'for debug, will print everything if enabled')

p.add_argument('-p','--punish', action = 'store_true', help = 'sets `break_wrongChoice` to True, incorrect licks will end an operant trial early')

p.add_argument('--lickThres', default = 300, type = int, help = 'set `lickThres` in arduino')
p.add_argument('--lcount', default = 2, type = int, help = 'set `minlickCount` in arduino')

runtype = p.add_mutually_exclusive_group()
runtype.add_argument('--dualmethod', default = 'permutation', help = "either permutations or product; product will give 'B' conditions")
runtype.add_argument('--singlestim', action = 'store_true', help = "For anaesthetised experiments, only run a single stimulus")

lickside = p.add_mutually_exclusive_group()
lickside.add_argument("-L", "--left", action = 'store_true')
lickside.add_argument("-R", "--right", action = 'store_true')

trigstate = p.add_mutually_exclusive_group()
trigstate.add_argument('--ITI',  nargs = 2, default = [2,5], type = float, help = "an interval for randomising between trials")
trigstate.add_argument('--triggered',  action = 'store_true', help = "waits for key press to initiate a trial")
trigstate.add_argument('--manfreq',  action = 'store_true', help = "choose left or right trial for each iteration, can be enabled mid run by hitting Ctrl-m")

args = p.parse_args()

verbose = args.verbose # this will be a cmdline parameter
port = args.port # a commandline parameter
ID = args.ID
repeats = args.repeats
datapath = args.datapath
singlestim = args.singlestim
manfreq = args.manfreq
triggered = args.triggered
dualmethod = args.dualmethod
weight = args.weight

leftmode =  args.left
rightmode = args.right

#----- shared paramaters -----
lickThres = args.lickThres
mode = args.mode
punish = args.punish
lcount = args.lcount


"""
--------------------------------------------------------------------
END Arguments
--------------------------------------------------------------------
"""





def bin_array(array, bin_size):
    """
    returns a down sampled array using the mean to interpolate data
    
    Keyword arguments:
    array    -- the array to be down sampled (an numpy.array)
    bin_size -- the width of bins to generate the down 
                sampled array (an integer > 1)
    """
    
    pad_size = math.ceil((array.size/bin_size)*bin_size - array.size)
    array_padded = np.append(array, np.zeroes(pad_size)*np.NaN)
    return np.nanmean(array_padded.reshape(-1,bin_size), axis = 1)
    
def menu():
    """
    a sort of REPL
    """
    c = "\x00"
    
    global manfreq
    global punish
    global triggered
    global lickThres
    global lcount
    global mode
    global leftmode
    global rightmode
    
    while True:
        while m.kbhit():
            c = m.getch()
            if c == '\xe0': c = c + m.getch()
        
        #menu:::
        
            if c in ("\r"):
                return
            
            # Toggle condition
            elif c in ("\t"):
                if mode == "c": mode = "o"
                elif mode == "o": mode = "c"
                print "Training mode:\t%s" %mode
                return
                
            # Toggle manual
            elif c in ("M","m"): #m,Ctrl-m
                manfreq = not manfreq
                print "Manual mode:\t%s" %manfreq
                log.write("Manual mode:\t%s\n" %manfreq)
                return
            
            elif c in '\xe0K':
                leftmode = True
                rightmode = False
                print "left mode:\t%s" %leftmode
                return
            
            elif c in '\xe0M':
                rightmode = True
                leftmode = False
                print "right mode:\t%s" %rightmode
                return
            
            elif c in ('\xe0P', '\xe0H'):
                leftmode = False
                rightmode = False
                print "random mode:\t", not (leftmode or rightmode)
                return
            
            # Toggle punishment
            elif c in ("P", "p", "\x10"):
                punish = not punish
                print "Punish for wrong lick:\t%s" %punish
                log.write("Punish for wrong lick:\t%s\n" %punish)
                return
            
            # Go to triggered mode
            elif c in ("T", "t", "\x14"):
                triggered = not triggered
                print "Triggered mode:\t%s" %manfreq
                log.write("Triggered mode:\t%s\n" %manfreq)
                return
            
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
            
            else:
                print "options: P T M < > ? h [ ] \\ \t"
        
        
def na_printr(s):
    try: return "%3d" %s
    except: return "%03s" %s
        
def num(s):
    """ 
    First attempts to convert string s to an integer. 
    If that gives a ValueError then it attempts to return s 
    as a float. Finally if s cannot be converted to a float or 
    an int, the string is returned unchanged.
    """
    try:
        return int(s)
    except ValueError:
        try: 
            return float(s)
        except ValueError:
            return s
        
def colour (x, fc = color.Fore.WHITE, bc = color.Back.BLACK, style = color.Style.NORMAL):
    return "%s%s%s%s%s" %(fc, bc, style, x , color.Style.RESET_ALL)

def unpack_table(filename):

    reader = csv.reader(open(filename, 'r'), delimiter = "\t")
    d = {}
    for row in reader:
       k, v = row
       d[k] = v
    
    return d

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')      
      
def today():
    """provides today's date as a string in the form YYMMDD"""
    return datetime.date.today().strftime('%y%m%d')
      
def get_line(port, verbose):
    
    inline = port.readline()
    
    if inline: inline = inline.strip()
    
    if inline.startswith("#"):
        inline = "#%s\t%s\t%s" %(timenow(), port, ID, inline)
        if verbose: print colour(inline, fc.CYAN, style = Style.BRIGHT)
    else: 
        inline = "%s\t%s\t%s" %(timenow(), port, ID, inline)
        print colour(inline, fc.YELLOW)
    
    return inline      

def Serial_monitor(logfile, show = True):
    
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
            
        logfile.write(fmt_line + "\n")
        
    return line

def update_bbox(params):
    """
    Communicates the contents of the dict `params` through
    the serial communications port. 
    
    data is sent in the form: `dict[key] = value`  --> `key:value`
    
    TODO: make this more general by putting `ser` as a parameter
    """
    for k in params.keys():
        ser.writelines("%s:%s" %(k, params[k]))
        if verbose: print "%s:%s" %(k, params[k])
        
        time.sleep(0.2)
        
def create_datapath(DATADIR = "", date = today()):
    """
    
    """
    
    if not DATADIR: DATADIR = os.path.join(os.getcwd(), date)
    else: DATADIR = os.path.join(DATADIR, date)
    
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

def manual_response_check(logfile):

    response = None
    response_time = None

    if m.kbhit():
        key = ord(m.getch())
        response_time =  timenow()
        if key == 224: #Special keys (arrows, f keys, ins, del, etc.)
            key = ord(m.getch())
            if key == 75: #Left arrow
                response = "L"
            elif key == 77: #Right arrow
                response = "R"
            else:
                response = "-"

        line = "%s\tManual declared response at:%s" %(timenow(), response)

        print colour(line, fc.MAGENTA, style = Style.BRIGHT)

        logfile.write(line+"\n")

    return [response], [response_time]    
 

def update_progress(progress):

    """
    Prints a wicked progress bar to the screen, 
    with the form
    ` [######                                ] 030% `
    """

    line = '  %s  %3d%%\r' %((' '*50), progress) + \
        '  %s]\r' %(' '*50) + \
        ' [%s\r' %('#'*(progress/2))
    
    print line,
    
    if progress == 100: print ""            
        
def manual(freq, t):
    
    """
    Function to manually select a specific condition
    given the keyboard input
    
    Requires freq to be a 2d array with 2 columns and N rows
    ie freq.shape = (N, 2L)
    """
    
    global leftmode
    global rightmode
    
    # all the possible key values for 'L' and 'R' respectively
    character = {
        'L' : ['\x0c', 'l', 'L', '\xe0K'],
        'R' : ['\x12', 'r', 'R', '\xe0M']
    }
    while True:
        if m.kbhit():
            c = m.getch()

            # in the event that an arrow key was pressed
            # check the buffer for the next character
            if c == '\xe0': 
                c = c + m.getch()

            for k in character.keys():
                if c in character[k]:
                    print "manual %s trial\r" %k,
                    
                    if (k == 'L') or leftmode:
                        freq = freq[freq[:,0] > freq[:,1]]
                        leftmode = True
                        
                    elif (k == 'R') or rightmode:
                        freq = freq[freq[:,0] < freq[:,1]]
                        rightmode = True
                    
                    else:
                        leftmode = False
                        rightmode = False
                        
                    shuffle(freq)
                    return freq[0]
                
        
            print "The next random frequency pair\r",
            return freq[t]
    
def init_serialport(port):
    """
    Open communications with the arduino;
    quits the program if no communications are 
    found on port.
    """
    
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.timeout = 1
    ser.port = port

    try: 
        ser.open()
        print colour("\nContact", fc.GREEN, style = Style.BRIGHT)
    except: 
        print colour("No communications on %s" %port, fc.RED, style = Style.BRIGHT)
        sys.exit(0)
    
    return ser
    
"""
---------------------------------------------------------------------
MAIN FUNCTION HERE
---------------------------------------------------------------------
"""    

#namespace.all?    


color.init()

datapath = create_datapath(datapath) #appends todays date to the datapath
logfile = create_logfile(datapath) #creates a filepath for the logfile


#make a unique filename
f = 0
df_file = '%s/%s_%s_%03d.csv' %(datapath, ID, today(), f)
while os.path.isfile(df_file):
    f += 1
    df_file = '%s/%s_%s_%03d.csv' %(datapath, ID, today(), f)

#open the communications line
ser = init_serialport(port)

copyfile('config.tab', '%s/%s_config_%s_%s.tab' %(datapath, ID, today(), timenow().replace(":","")))            
params_i = unpack_table('config.tab')
params = dict(params_i) #create a copy of the original

if args.freq: 
    freq = args.freq
else:
    freq = np.loadtxt('frequencies.tab', skiprows = 1)

#generate the frequency pairs
if singlestim: 
    freq = np.array([freq, np.zeros(len(freq))]).transpose()
    
else:
    tmp_freq = []
    
    if (dualmethod in "permutations") and (dualmethod in "product"):
        print color("Error: dualmethod needs to be either 'permutations' or 'product': got%s" %dualmethod, fc.RED, style = Style.BRIGHT)
    
    elif dualmethod in "permutations":
        for f in permutations(freq, 2): 
            tmp_freq.append(np.array(f))
        freq = tmp_freq
    elif dualmethod in "product":
        for f in product(freq, freq): 
            tmp_freq.append(np.array(f))
        freq = tmp_freq
    
    elif dualmethod in "merge":
        freq = np.array((freq, freq)).transpose()
    
    del tmp_freq

freq = np.array(freq)

trial_num = 0

try:
    #open a file to save data in
    with open(logfile, 'a') as log:
        
        #IDLE while Arduino performs it's setup functions
        print "\nAWAITING DISPATCH: ",
        t = 0
        while ser.inWaiting() == False:
            print "\rAWAITING DISPATCH: ", t, "\r",
            t += 1
        
        print "\r         DISPATCH: ", t
        
        # Buffer for 500 ms to let arduino finish it's setup
        time.sleep(.5)
        # Log the debug info for the setup
        while ser.inWaiting(): Serial_monitor(log)
        
        # loop for r repeats
        for r in xrange(repeats):
            
            print colour("BLOCK:\t%02d" %r, 
                fc.MAGENTA, style = Style.BRIGHT)
                
            # shuffle the frequencies
            shuffle(freq)
                            
            #This starts a loop that goes through 1 run per frequency combination
            for t in xrange(len(freq)):
            
                # create an empty dictionary to store data in
                trial_df = {
                    'trial_num' : trial_num,
                    'port[0]' : [],
                    'port[1]' : [],
                    'WaterPort[0]': 0,
                    'WaterPort[1]': 0,
                    'ID' : ID,
                    'manfreq' : manfreq,
                    'weight' : weight,
                    'block' : r
                }

               
                #In triggered mode
                while m.kbhit():
                    print "\nChoose...",
                    menu()
                   
                if manfreq:
                    print "Choose condition",
                    
                    trial_freq = manual(freq, t)
                else:
                    trial_freq = freq[t]
                    if leftmode: 
                        trial_freq.sort()
                        trial_freq = trial_freq[::-1]
                    elif rightmode: trial_freq.sort()

                # convert the frequencies into an on off square pulse
                for f in (0,1):
                    trial_df['freq%d' %f] = [trial_freq[f]]
                    # if the frequency is 0 make the on time = 0
                    if trial_freq[f] == 0: 
                        params['ON[%d]' %f] = 0
                        params['OFF[%d]' %f] = 10 # ms
                    # off period = (1000 ms / frequency Hz) - 5 ms ~ON period~
                    else:
                        ON = num(params_i['ON[%d]' %f])
                        params['ON[%d]' %f] = ON
                        OFF = (1000/trial_freq[f]) -  ON
                        params['OFF[%d]' %f] =  OFF if OFF > 0 else 1 
                
                # Determine the reward condition
                #     1. f0 > f1 :: lick left
                #     2. f0 < f1 :: lick right
                #     3. f0 == 0 OR f1 == 0, either port is valid
                #     4. f0 == 0 AND f1 == 0, neither port is valid
                
                if trial_freq[0] and trial_freq[1]:
                    if trial_freq[0] == trial_freq[1]: params['rewardCond'] = 'B'
                    if trial_freq[0] > trial_freq[1]: params['rewardCond'] = 'L'
                    if trial_freq[0] < trial_freq[1]: params['rewardCond'] = 'R'
                
                else:
                    if trial_freq[0] or trial_freq[1]:params['rewardCond'] = 'B'
                    else: params['rewardCond'] = 'N'
                
                print colour("F:%3d %3d C: %s" \
                                %(trial_freq[0], trial_freq[1], params['rewardCond']), 
                                fc.MAGENTA, style = Style.BRIGHT),
                
                #THE HANDSHAKE
                # send all current parameters to the arduino box to run the trial
                
                params['mode'] = mode
                params['lickThres'] = lickThres
                params['break_wrongChoice'] = num(punish)
                params['minLickCount'] = lcount
                
                update_bbox(params)
                
                # log the receipt of the parameters
                while ser.inWaiting():
                    
                    # get info about licks, strip away trailing white space
                    line = Serial_monitor(log, show = verbose).strip()
                    
                    # store it if it isn't debug or the ready line
                    if line[0] != "#" and line[0] != "-":
                        var, val = line.split(":\t")
                        trial_df[var] = num(val)
                
                if (triggered == False) and (manfreq == False):
                    ITI = random.uniform(args.ITI[0], args.ITI[1])
                    #print "go in %d\r"  %ITI,
                    time.sleep(ITI)
                
                elif triggered and (manfreq == False):
                    while m.kbhit() == False:
                        print colour("\r%s waiting for trigger\r" %(timenow()), fc.RED, style = Style.BRIGHT),
                    while m.kbhit():
                        m.getch() #clear the buffer
                    
                #print colour("%s  GO!\r" %timenow(), fc.GREEN, style=Style.BRIGHT),
                    
                trial_df['time'] = timenow()
                
                # Send the literal GO symbol
                ser.write("GO")

                while line.strip() != "-- Status: Ready --":
                    
                    line = Serial_monitor(log, False).strip()
                    if line:
                        if line[0] != "#" and line[0] != "-":
                            var, val = line.split(":\t")
                            val = num(val)
                            if var.startswith("port"): trial_df[var].append(val)
                            else: trial_df[var] = val
                            
                # partitions lick responses into three handy numbers each

                licksL = np.array(trial_df['port[0]'])
                licksR = np.array(trial_df['port[1]'])

                t_f0 = num(params['t_stimONSET[0]'])
                t_f1 = num(params['t_stimONSET[1]'])
                t_post = num(params['t_rewardSTART'])
                
                try: trial_df['left_pre'] = [len(licksL[licksL < t_f0])]
                except: trial_df['left_pre'] = [0]
                try: trial_df['left_stim'] = [len(licksL[(licksL > t_f0) & (licksL < t_post)])]
                except: trial_df['left_stim'] = [0]
                try: trial_df['left_post'] = [len(licksL[licksL > t_post])]
                except: trial_df['left_post'] = [0]
                                                                                    
                try: trial_df['right_pre'] = [len(licksR[licksR < t_f0])]
                except: trial_df['right_pre'] = [0]
                try: trial_df['right_stim'] = [len(licksR[(licksR > t_f0) & (licksR < t_post)])]
                except: trial_df['right_stim'] = [0]
                try: trial_df['right_post'] = [len(licksR[licksR > t_post])]
                except: trial_df['right_post'] = [0]

                del trial_df['port[0]']
                del trial_df['port[1]']
                
                for k in trial_df.keys():
                    if type(trial_df[k]) == list: trial_df[k] = trial_df[k][0]                
               
                """
                #Save the data to a data frame / Save to a file
                """
                    
                with open(df_file, 'w') as datafile:
                    
                    trial_df = pd.DataFrame(trial_df, index=[trial_num])
                    
                    if trial_num == 0:
                        df = trial_df
                    else: 
                        df = df.append(trial_df, ignore_index = True)
                    
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

                    df.to_csv(datafile)
                
                #Print the important data and coloured code for hits / misses
                
                print Style.BRIGHT, '\r',
                for k in ('trial_num', 'mode', 'rewardCond', 'response', 'WaterPort[0]', 'WaterPort[1]','OFF[0]', 'OFF[1]',):
                    N = trial_num
                    
                    
                    if df.correct[N]:
                        print '%s%s:%s%4s' %(fc.WHITE, k, fc.GREEN, str(trial_df[k][N]).strip()),
                    elif df.miss[N]:
                        print '%s%s:%s%4s' %(fc.WHITE, k, fc.YELLOW, str(trial_df[k][N]).strip()),
                    else:
                        print '%s%s:%s%4s' %(fc.WHITE, k,fc.RED, str(trial_df[k][N]).strip()),
                print '\r', Style.RESET_ALL
                
                #calculate percentage success
                
                print "\r", 100 * " ", "\r                ", #clear the line 
                
                hits = df.correct.sum() / df.ID.count()
                
                if df.ID[df.rewardCond.isin(['L','B'])].count():
                     hit_L = df.correct[df.response == 'L'].sum() / df.ID[df.rewardCond.isin(['L','B'])].count()
                else: hit_L = float('nan')
                
                if df.ID[df.rewardCond.isin(['R','B'])].count():
                     hit_R = df.correct[df.response == 'R'].sum() / df.ID[df.rewardCond.isin(['R','B'])].count()
                else: hit_R = float('nan')
                
                if df.ID[df.rewardCond != 'N'].count():
                    misses = (df.miss.sum() / df.ID[df.rewardCond != 'N'].count())*100
                else: misses = float('nan')
                
                wrong = (df.wrong.sum() / df.ID.count())*100
                
                misses = na_printr(misses)
                wrong = na_printr(wrong)
                hits =  na_printr(hits*100)
                hit_L = na_printr(hit_L*100)
                hit_R = na_printr(hit_R*100)
                cumWater = df['WaterPort[0]'].sum() + df['WaterPort[1]'].sum()
                                
                print colour("hits:%03s%%  misses:%0s%%  wrong:%03s%%  R:%03s%%  L:%03s%%  Count:%4d  Water:%3d                         " %(hits, misses, wrong, hit_R, hit_L, df.ID.count(), cumWater),
                                fc = fc.YELLOW, bc = bc.BLUE, style = Style.BRIGHT), '\r',
                
                trial_num += 1
            
except KeyboardInterrupt:
    print "Closing", port
    sys.exit(0)