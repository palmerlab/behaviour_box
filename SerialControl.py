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

import numpy as np # bread and butter
from numpy.random import random_integers, shuffle
import pandas as pd # on the fly data analysis
from StringIO import StringIO
from scipy.stats import norm #on the fly calculations
from itertools import combinations_with_replacement as combinations
import colorama # makes things look nice

from config import *
from SerialFUNCTIONS import *
      

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



"lickThres"      // 5V / 1024
"trial_delay"    // ms
"t_noLickPer"    // ms
"t_stimONSET[0]" // ms
"t_stimONSET[1]" // ms
"stimDUR"        // ms
"t_rewardSTART"  // ms
"t_rewardEND"    // ms
"t_trialEND"     // ms
"waterVol"       // ms
                 // ms
"ON"             // ms
"OFF[0]"         // ms
"OFF[1]"         // ms


"mode"           // 'c' or 'o'
"rewardCond"     // 'L', 'R', 'B', 'N'
"verbose"        // true


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
parser.add_argument('-bp','--behaviourPORT', default = behaviourPORT
                    help="Serial Port that behaviour box is connected to, defaults to COM5")
parser.add_argument('-i', '--id', 
                    help="animal ID")
parser.add_argument('-m', '--mode', default = mode, 
                    help="mode to send to behaviour box.")
parser.add_argument('-dp', '--dprime', action='store_false', 
                    help="calculate the d_prime, true by default")
parser.add_argument('-v', '--verbose', action='store_true', 
                    help="prints debug info from arduino")
parser.add_argument('-b', '--block', type=int, default = 20, 
                    help="Number of iterations to count d_prime")
parser.add_argument('-f', '--freq', nargs="+", 
                    type=int, default = frequency_block,
                    help="a list of integer freq to be sent to flutter controller")
parser.add_argument("--datadir", 
                    help="path to save log file; defaults to `.\\YYMMDD\\`")

parser.add_argument("--trial_delay"   , default = boxparams["trial_delay"   ])                    
parser.add_argument("--t_noLickPer"   , default = boxparams["t_noLickPer"   ])                    
parser.add_argument("--t_stimONSET[0]", default = boxparams["t_stimONSET[0]"])                    
parser.add_argument("--t_stimONSET[1]", default = boxparams["t_stimONSET[1]"])                    
parser.add_argument("--stimDUR"       , default = boxparams["stimDUR"       ])                    
parser.add_argument("--t_rewardSTART" , default = boxparams["t_rewardSTART" ])                    
parser.add_argument("--t_rewardEND"   , default = boxparams["t_rewardEND"   ])                    
parser.add_argument("--t_trialEND"    , default = boxparams["t_trialEND"    ])                    
parser.add_argument("--lickThres"     , default = boxparams["lickThres"     ])                    
parser.add_argument("--waterVol"      , default = boxparams["waterVol"      ])                    
parser.add_argument("--ON"            , default = boxparams["ON"            ])                    
parser.add_argument("--OFF[0]"        , default = boxparams["OFF[0]"        ])                    
parser.add_argument("--OFF[1]"        , default = boxparams["OFF[1]"        ])                    
parser.add_argument("--mode"          , default = boxparams["mode"          ])                    
parser.add_argument("--rewardCond"    , default = boxparams["rewardCond"    ])                    
                                                                  
                                            
args = parser.parse_args()



"""

MAIN FUNCTION HERE

"""

if __name__ =="__main__":
    os.system("cls")

    colorama.init()
        
    #get all arguments
    behaviourPORT = args.behaviourPORT
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
    behaviourCOMs = serial.Serial(baudrate = 9600, timeout = 0.05, port = behaviourPORT)
    try: behaviourCOMs.open()
    except: 
        print_RED("No communications on", behaviourPORT)
        behaviourCOMs = False
        sys.exit(0)

            
    logfile = create_logfile(datadir)        

    with open(logfile, 'a') as log:
        
        if behaviourCOMs: 
            log.write("#%s\tstimbox OPEN port %s\n" %(timenow(),behaviourPORT))
            print_CYAN("#%s\tbehaviour OPEN port %s\n" %(timenow(),behaviourPORT), verbose)
    
    
    
    while True:

        cmds = check_input()
        log.write(get_info(behaviourCOMS, verbose))
        
        
        
    ##repeat  per block
    
        for k in boxparams.keys():
            behaviourCOMS.write("%s:%s" %(k, boxparams[k]))
            log.write(get_info(behaviourCOMS))
        
    
        for b in xrange(block):
        
            boxparams_old = boxparams
            
            shuffle(freq)


            print colorama.Fore.MAGENTA + "freq:\t",
            for i in xrange(len(freq)): print freq[i], "Hz\t",
            print colorama.Style.RESET_ALL

                #frequency input to stimbox  = "%d:%d&%d%d"
            for t in xrange(len(freq)):
                t = 0

                # behaviour box: parse frequency
                # frequency is converted from Hz to an off period in ms 
                # (the box then coverts this to us)
                boxparams["OFF[0]"] = 10e3/freq[t][0]) - 5
                boxparams["OFF[1]"] = 10e3/freq[t][1]) - 5
                
                #based on frequencies send the reward contingency to
                # the behaviour box
                # 0 results in no reward on this trial
                if freq[t][0] and freq[t][1]:
                    if freq[t][0] > freq[t][1]:
                        boxparams['rewardCond'] = 'R'
                    else:
                        boxparams['rewardCond'] = 'L'
                else if freq[t][0] or freq[t][1]:
                    #use either port
                    boxparams['rewardCond'] = 'B'
                else:
                    # no reward
                    boxparams['rewardCond'] = 'N'

                for k in boxparams.keys():
                    if boxparams_old[k] != boxparams[k]:
                        behaviourCOMS.write("%s:%s" %(k, boxparams[k]))
                        log.write(get_info(behaviourCOMS))
        
        behaviour_log()