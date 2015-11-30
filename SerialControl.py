from __future__ import division

import pandas as pd
import csv
import datetime
import time
import os
import sys
import glob
import serial
import argparse
import msvcrt as m
import numpy as np
from numpy.random import shuffle
import AndrewSignalDetection as sig

from itertools import combinations_with_replacement as combinations
      
      
import colorama as c # makes things look nice
from colorama import Fore as fc
from colorama import Back as bc     
from colorama import Style

from style import colour      


c.init()
date = datetime.date.today().strftime('%y%m%d')


def bin_array(array, bin_size):
    
    pad_size = math.ceil((array.size/bin_size)*bin_size - array.size)
    array_padded = np.append(array, np.zeroes(pad_size)*np.NaN)
    return np.nanmean(array_padded.reshape(-1,bin_size), axis = 1)
    


def goto_interpreter():
    
    if m.kbhit():
        c = m.getch()
        if c == '\xe0': c = m.getch()
        
        if c == '\x1b':
            sys.exit(0)
        
        else:    
            mode = raw_input(">>> ")
            exec(mode)
            return

def num(s):
    try:
        return int(s)
    except ValueError:
        try: 
            return float(s)
        except ValueError:
            return s
        

def unpack_table(filename):

    reader = csv.reader(open(filename, 'r'), delimiter = "\t")
    d = {}
    for row in reader:
       k, v = row
       d[k] = v
    
    return d

def timenow(): 
    return str(datetime.datetime.now().time().strftime('%H:%M:%S'))      
      
def get_line(port, verbose):
    
    inline = port.readline()

    if inline.startswith("#"):
        inline = "#%s\t%s\t%s" %(timenow(), port, ID, inline)
        if verbose: print colour(inline, fc.CYAN, Style.BRIGHT)
    else: 
        inline = "%s\t%s\t%s" %(timenow(), port, ID, inline)
        print colour(inline, fc.YELLOW)
    
    return inline      

def colour (x, fc = c.Fore.WHITE, bc = c.Back.BLACK, style = c.Style.NORMAL):
    return "%s%s%s%s%s" %(fc, bc, style, x , c.Style.RESET_ALL)

def Serial_monitor(logfile):
    
    line = ser.readline()
    
    if line:
        
        fmt_line = "%s\t%s\t%s\t%s" %(timenow(), port, ID, line)
        
        if line.startswith("#"): 
            fmt_line = "#" + fmt_line
            if verbose: print colour(fmt_line, fc.CYAN, Style.BRIGHT)
        
        elif line[0] != "#": 
            
            print colour("%s\t%s\t%s" %(timenow(), port, ID), fc.WHITE),
            print colour(line, fc.YELLOW, Style.BRIGHT)
            
        logfile.write(fmt_line)
        
    return line

        

def update_bbox(params):

    for k in params.keys():
        ser.writelines("%s:%s" %(k, params[k]))
        time.sleep(0.2)
        

def create_logfile(DATADIR = ""):
    
    date = datetime.date.today().strftime('%y%m%d')
    
    if not DATADIR: DATADIR = os.path.join(os.getcwd(), date)
    
    if not os.path.isdir(DATADIR):
        os.mkdir((DATADIR))
    
    filename = "%s_%s_%s.log" %(port,ID,date)
    logfile = os.path.join(DATADIR, filename)
    print logfile.replace("\\", "\\\\")
    
    return logfile

        
"""
    ------------
    Arguments
    ------------
"""
verbose = True # this will be a cmdline parameter
port = "COM5" # a commandline parameter
ID = ""
           

params_i = unpack_table('config.tab')           
freq = np.loadtxt('frequencies.tab', skiprows = 1)

#generate the frequency pairs
tmp_freq = []        

for f in combinations(freq, 2): 
    tmp_freq.append(f)
freq = tmp_freq

del tmp_freq

#set the block proportional to the number of freq to be tested
block = len(freq) * 5 

freq = np.array(freq)

ser = serial.Serial()
ser.baudrate = 115200
ser.timeout = 1
ser.port = port

try: 
    ser.open()
    print colour("\nWe are a GO", fc.GREEN)
except: 
    print colour("No communications on %s" %port, fc.RED, Style.BRIGHT)
    sys.exit(0)



params = params_i

logfile = create_logfile()



trial_num = 0
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
    
    while ser.inWaiting(): Serial_monitor(log)
    
    
    # shuffle the frequencies
    
    shuffle(freq)
    
    for t in xrange(len(freq)):
            
        # create an empty dictionary to store data in
        trial_df = {}
        
        
        trial_df['trial_num'] = [trial_num]
        
        
        
        # convert the frequencies into an on off square pulse
        for f in (0,1):
            trial_df['freq%d' %f] = freq[t][f]
            # if the frequency is 0 make the on time = 0
            if freq[t][f] == 0: 
                params['ON[%d]' %f] = 0
                params['OFF[%d]' %f] = 1 # ms
            # off period = (1000 ms / frequency Hz) - 5 ms ~ON period~
            else:
                params['ON[%d]' %f] = 5
                params['OFF[%d]' %f] = (10e3/freq[t][f]) - 5
                
        
        
        # Determine the reward condition
        #     1. f0 > f1 :: lick left
        #     2. f0 < f1 :: lick right
        #     3. f0 == 0 OR f1 == 0, either port is valid
        #     4. f0 == 0 AND f1 == 0, neither port is valid
        
        if freq[t][0] and freq[t][1]:
            if freq[t][0] > freq[t][1]: params['rewardCond'] = 'L'
            if freq[t][0] < freq[t][1]: params['rewardCond'] = 'R'
        
        else:
            if freq[t][0] or freq[t][1]:params['rewardCond'] = 'B'
            else: params['rewardCond'] = 'N'
        
        
        #THE HANDSHAKE
        # send all current parameters to the arduino box to rul the trial
        update_bbox(params)
        
        # log the receipt of the parameters
        while ser.inWaiting():
            
            # get info about licks, strip away trailing white space
            line = Serial_monitor(log).strip()
            
            # store it if it isn't debug or the ready line
            if line[0] != "#" and line[0] != "-":
                var, val = line.split(":\t")
                val = num(val)
                try: trial_df[var].append(val)
                except KeyError: trial_df[var] = [val]
                except AttributeError: trial_df[var] = [trial_df[var], val]
            
        # todo make this a random timer
        for i in range(0,5):
            time.sleep(1)
            print colour(i, fc.MAGENTA, Style.BRIGHT), "\r",
        
        # Send the literal GO symbol
        ser.write("GO")
        
        
        while line.strip() != "--Welcome back Commander":
            
            line = Serial_monitor(log).strip()
            if line:
                if line[0] != "#" and line[0] != "-":
                    var, val = line.split(":\t")
                    val = num(val)
                    try: trial_df[var].append(val)
                    except KeyError: trial_df[var] = [val]
                    except AttributeError: trial_df[var] = [trial_df[var], val]
            
        if trial_df['response']:
            lick_response = np.array(trial_df['port[0]'],trial_df['port[1]'])
            
            np.savetxt("%s_%s_licktimes_trial%04d.tab" %(ID,date, trial_num), 
                lick_response, fmt = "%d", delimiter = "\t", 
                header = "port[0]\tport[1]")
            
            for r in trial_df['response']:
            
                try: 
                    if r in trial_df['port[0]']: lick_response[0][r] = 1
                except: pass
                try: 
                    if r in trial_df['port[1]']: lick_response[1][r] = 1
                except: pass
            
            lick_response[0] = bin_array(lick_response[0], 2000) #compact into 2 s bins
            lick_response[1] = bin_array(lick_response[1], 2000) #compact into 2 s bins
            
            
            if (trial_df['rewardCond'] == 'L') and sum(lick_response[0][2:]):
                trial_df['response'] = 1
            
            elif (trial_df['rewardCond'] == 'R') and sum(lick_response[1][2:]):
                trial_df['response'] = 1
                
            elif (trial_df['rewardCond'] == 'B') and (sum(lick_response[0][2:]) or sum(lick_response[1][2:])):
                trial_df['response'] = 1
                
            elif (trial_df['rewardCond'] == 'N') and (sum(lick_response[0][2:]) or sum(lick_response[1][2:])):
                trial_df['response'] = 0
            
            else: trial_df['response'] = 0
        
        
        
        trial_df = pd.DataFrame(trial_df)
        
        with open('data.tab', 'a') as datafile:
            trial_df.to_csv(datafile, 
                header=(trial_num==0), sep = "\t")
        
        trial_num += 1      

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

"""
"""

MAIN FUNCTION HERE

"""