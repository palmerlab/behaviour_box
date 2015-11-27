from __future__ import division

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

from SerialFUNCTIONS import *
      
      
import colorama # makes things look nice
from colorama import Fore as fc
from colorama import Back as bc     
from colorama import Style

from style import colour      




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
       k, v = row[0] , row[1:]
       d[k] = v
    
    return d

def timenow(): 
    return str(datetime.datetime.now().time().strftime('%H:%M:%S'))      
      
def get_line(port, verbose):
    
    inline = port.readline()

    if inline.startswith("#"):
        inline = "#%s\t%s\t%s" %(timenow(), port, id, inline)
        if verbose: print colour(inline, fc.CYAN, Style.BRIGHT)
    else: 
        inline = "%s\t%s\t%s" %(timenow(), port, id, inline)
        print colour(inline, fc.YELLOW)
    
    return inline      

def colour (x, fc = c.Fore.WHITE, bc = c.Back.BLACK, style = c.Style.NORMAL):
    return "%s%s%s%s%s" %(fc, bc, style, x , c.Style.RESET_ALL)

def Serial_monitor():

    tmp_dict = {}
    
    while m.kbhit() == False:
        
        line = port.readline()
        
        if line == "--Welcome back Commander":        
            return tmp_dict
        
        fmt_line = "%s\t%s\t%s" %(timenow(), port, id, line)
        
        if line.startswith("#"): 
            fmt_line = "#" + fmt_line
            if verbose: print colour(fmt_line, fc.CYAN, Style.BRIGHT)
        
        elif line[0] != "#": 
            
            print colour("%s\t%s" %(timenow(), port, id), fc.WHITE),
            print colour(line, fc.YELLOW, Style.BRIGHT)
            
            var, val = line.split(":\t")
        
            try: 
                tmp_dict[var].append(val)
            except:
                tmp_dict[var] = [val]
                
        
        logfile.write(fmt_line)

        

def update_bbox(params):

    for k in params.keys():
        ser.write("%s:%s" %(k, params[k]))
    
    Serial_monitor()
        
    
"""
    ------------
    Arguments
    ------------
"""
verbose = True # this will be a cmdline parameter
port = "COM5" # a commandline parameter
           

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

ser = serial.Serial(baudrate = 9600, timeout = 0.05, port = port)

try: 
    behaviourCOMs.open()
    Serial_monitor()
    
except: 
    print_RED("No communications on", behaviourPORT)
    behaviourCOMs = False
    sys.exit(0)

shuffle(freq)

params['OFF[0]'] = 10e3/freq[t][0] - 5
params['OFF[1]'] = 10e3/freq[t][0] - 5

update_bbox(params)

ser.write("GO")
Serial_monitor()






    
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      

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