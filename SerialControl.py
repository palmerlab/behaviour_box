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


from config import *
from SerialFUNCTIONS import *
      
      
import colorama # makes things look nice
from colorama import Fore as fc
from colorama import Back as bc     
from colorama import Style

from style import colour      


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

    
"""
    ------------
    Arguments
    ------------
"""
verbose = True # this will be a cmdline parameter
port = "COM5" # a commandline parameter
           
           
while m.kbhit() == False:
    
    get_line(serial, verbose)
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      

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

if __name__ =="__main__":
    os.system("cls")

    colorama.init()
        
    #get all arguments
    behaviourPORT = args.behaviourPORT
    id = args.id
    do_dprime = args.dprime
    
    verbose = args.verbose
    boxparams['verbose'] = verbose
    
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
                boxparams["OFF[0]"] = 10e3/freq[t][0] - 5
                boxparams["OFF[1]"] = 10e3/freq[t][1] - 5
                
                #based on frequencies send the reward contingency to
                # the behaviour box
                # 0 results in no reward on this trial
                if freq[t][0] and freq[t][1]:
                    if freq[t][0] > freq[t][1]:
                        boxparams['rewardCond'] = 'R'
                    else:
                        boxparams['rewardCond'] = 'L'
                elif freq[t][0] or freq[t][1]:
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