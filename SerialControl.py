from __future__ import division

import datetime
import time
import os
import sys
import glob
import serial
import argparse
import msvcrt as m
import warnings
warnings.simplefilter(action = "ignore", category = UserWarning)

import numpy as np
from numpy.random import random_integers, shuffle
from collections import deque
import pandas as pd
from StringIO import StringIO
from scipy.stats import norm
from itertools import combinations_with_replacement as combinations
import colorama

import config
import SerialFUNCTIONS
      

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




modeString = "operant1";
t_noLickPer = 0;   // ms
t_stimSTART = 4000;   // ms
t_stimEND = 4500;     // ms
t_rewardSTART = 5000; // ms
t_rewardEND = 7000;   // ms
t_trialEND = 10000;   // ms
minITI = 3000;        // ms
maxITI = 6000;        // ms
maxTimeOut = 0;    // ms
minTimeOut = 0;    // ms



"""

        

"""

df.head = ['modeString', 'waterCount', 'trial_delay', 
    'istimeout', 'stimTrial', 'response']

behaviourbox should report:
        L%d:R%d true false
        L0000:R2000:L50000:R30000
    
    
df.head = ["frequency", on_Period ", off_Period", count", Timer"]

"""

parser = argparse.ArgumentParser(description="Open up Serial Port and log communications")
parser.add_argument('-bp','--behaviourPORT', default = config.behaviourPORT
    help="Serial Port that behaviour box is connected to, defaults to COM5")
                                            
parser.add_argument('-sp', '--stimboxPORT', default= config.stimboxPORT
    help="Serial Port that stimbox is connected to, defaults to COM4")
                                            
parser.add_argument('-i', '--id', 
    help="animal ID")
parser.add_argument('-m', '--mode', default = config.mode, 
    help="mode to send to behaviour box.")
parser.add_argument('-dp', '--dprime', action='store_false', 
    help="calculate the d_prime, true by default")
parser.add_argument('-v', '--verbose', action='store_true', 
    help="prints debug info from arduino")
parser.add_argument('-b', '--block', type=int, default = 20, 
    help="Number of iterations to count d_prime")
parser.add_argument('-f', '--freq', nargs="+", 
    type=int, default = config.frequency_block,
    help="a list of integer freq to be sent to flutter controller")
parser.add_argument("--datadir", 
    help="path to save log file; defaults to `.\\YYMMDD\\`")
                                            
args = parser.parse_args()



"""

MAIN FUNCTION HERE

"""

if __name__ =="__main__":
    os.system("cls")

    colorama.init()
        
    #get all arguments
    behaviourPORT = args.behaviourPORT
    stimboxPORT = args.stimboxPORT
    id = args.id
    do_dprime = args.dprime
    verbose = args.verbose
    block = args.block
    freq = args.freq

    if freq: 
        tmp_freq = []
        
        for f in combinations(freq, 2): 
            tmp_freq.append(f)
        
        freq = tmp_freq
        del tmp_freq

        #set the block proportional to the number of freq to be tested
        block = len(freq) * 5 
        
        freq = np.array(freq)
        

    datadir = args.datadir

    #open Serial ports
    stimboxCOMs = serial.Serial(baudrate = 9600, timeout = 0.05, port = stimboxPORT)
    try: 
        stimboxCOMs.open()
        
    except: 
        print_RED("No communications on", stimboxPORT)
        stimboxCOMs = False
        
    behaviourCOMs = serial.Serial(baudrate = 9600, timeout = 0.05, port = behaviourPORT)
    try: behaviourCOMs.open()
    except: 
        print_RED("No communications on", behaviourPORT)
        behaviourCOMs = False

            
    logfile = create_logfile(datadir)        

    with open(logfile, 'a') as log:
        
        if stimboxCOMS: 
            log.write("#%s\tstimbox OPEN port %s\n" %(timenow(),stimboxPORT))
            print_CYAN("#%s\tstimbox OPEN port %s\n" %(timenow(),stimboxPORT), verbose)
            log.write(get_info(stimboxCOMS), lines = 3)
            
        if behaviourCOMs: 
            log.write("#%s\tstimbox OPEN port %s\n" %(timenow(),behaviourPORT))
            print_CYAN("#%s\tbehaviour OPEN port %s\n" %(timenow(),behaviourPORT), verbose)
            log.write(get_info(behaviourCOMS), lines = 3)
            
    ##repeat  per block

        shuffle(freq)


        print colorama.Fore.MAGENTA + "freq:\t",
        for i in xrange(len(freq)): print freq[i], "Hz\t",
        print colorama.Style.RESET_ALL

            #frequency input to stimbox  = "%d:%d&%d%d"
        
        t = 0

        # behaviour box: parse frequency
        stimboxCOMS.write("F%d:%d" %(0, (10e6/freq[t][0]) - 5e3)
        stimboxCOMS.write("F%d:%d" %(1, (10e6/freq[t][1]) - 5e3)
        
        
        #based on frequencies send the reward contingency to
        # the behaviour box
        # 0 results in no reward on this trial
        if freq[t][0] and freq[t][1]:
            if freq[t][0] > freq[t][1]:
                "right"
                behaviourCOMS.write("port:R")
            else:
                behaviourCOMS.write("port:L")
        else if freq[t][0] or freq[t][1]:
            #use either port
            behaviourCOMS.write("port:1")
        
        else:
            # no reward
            behaviourCOMS.write("port:0")
                
        log.write(get_info(simboxCOMS))
        
        behaviourCOMS.write("m%d" %mode)
        log.write(get_info(behaviourCOMS), lines = 2)
        
        behaviour_log()