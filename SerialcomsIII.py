from __future__ import division

import datetime
import time
from time import sleep
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
    help="""prints debug info from arduino""")
parser.add_argument('-b', '--block', type=int, default = 20, 
    help="Number of iterations to count d_prime")
parser.add_argument('-f', '--frequencies', nargs="+", 
    type=int, default = config.frequency_block,
    help="a list of integer frequencies to be sent to flutter controller")
parser.add_argument("--datadir", 
    help="path to save log file; defaults to `.\\YYMMDD\\`")
                                            
args = parser.parse_args()


def random_block(frequency_block = ['0Hz', '5Hz', '10Hz', '25Hz', '50Hz', '100Hz']):
	
        return np.random.shuffle(block)

        
def print_GREEN(x):
    print colorama.FORE.GREEN, x, colorama.Style.RESET_ALL
    return x       
        
def print_YELLOW(x):
    print colorama.FORE.YELLOW, x, colorama.Style.RESET_ALL
    return x
        
def print_CYAN(x, v = False):
    if v: print colorama.FORE.CYAN, x, colorama.Style.RESET_ALL
    return x
        
def print_RED(x):
    print colorama.FORE.RED, x, colorama.Style.RESET_ALL
    return "warning:\t%s" %x
    

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
    frequencies = args.frequencies

    if frequencies: 
        tmp_frequencies = []
        
        for f in combinations(frequencies, 2): 
            tmp_frequencies.append(f)
        
        frequencies = tmp_frequencies
        del tmp_frequencies

        block = len(frequencies) * 5 #set the block proportional to the number of frequencies to be tested
        

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

        shuffle(frequencies)


        print colorama.Fore.MAGENTA + "frequencies:\t",
        for i in xrange(len(frequencies)): print frequencies[i], "Hz\t",
        print colorama.Style.RESET_ALL

            #frequency input to stimbox  = "f dddd dddd"
        
        t = 0

        stimboxCOMS.write("f %d %d" %frequencies[t])
        log.write(get_info(simboxCOMS))
        
        behaviourCOMS.write("m%d" %mode)
        log.write(get_info(behaviourCOMS), lines = 2)
        
        behaviour_log()
            

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

df.head = ['modeString', 'waterCount', 'trial_delay', 
    'istimeout', 'stimTrial', 'response', 'lickCount']
    
df.head = ["frequency", on_Period ", off_Period", count", Timer"]

"""
    

    
def behaviour_log(logfile):
    
    while True:
        
        inline = behaviourCOMS.readline()
        
        if inline:
            if inline.startswith("#"):
                logfile.write(print_CYAN(inline, verbose))
            else:
            
                logfile.write(print_YELLOW(inline))
                
                behaviourDF = pd.read_table(StringIO(table), 
                    sep = "\t").convert_objects(convert_numeric=True)

    return pass
    
    

def check_input():
    
    if m.kbhit():
        c = m.getch()
        if c == '\xe0': c = m.getch()
        
        if c = '\x1b':
            sys.exit(0)
        
        else:    
            mode = raw_input("type command: ")
            c = ''
            return mode
    else:
        return False

def create_logfile(DATADIR = ""):
    
    date = datetime.date.today().strftime('%y%m%d')
    
    if not DATADIR: DATADIR = os.path.join(os.getcwd(), date)
    
    if not os.path.isdir(DATADIR):
        os.mkdir((DATADIR))
    
    filename = "%s_%s_%s.log" %(port,id,date)
    logfile = os.path.join(DATADIR, filename)
    print logfile.replace("\\", "\\\\")
    
    return logfile

def timenow(): 
    return str(datetime.datetime.now().time().strftime('%H:%M:%S'))
    
def get_data(table):
    df = pd.read_table(StringIO(table), sep = "\t", comment ="#")
    df = df[df['modeString'].contains("operant|conditioning", regex=True)]
    df = df.dropna(axis = 1)
    df = df.convert_objects(convert_numeric=True)
    return df

def z_transform(x): 
    return norm.ppf(x)

def calc_dprime(df):

    N = len(df)
    if N < 0:
        print colorama.Fore.RED + colorama.Style.BRIGHT + "DF too small for d prime"
        return "nan", "nan", "nan"
        
    hits = len(df[df.response == 1][df.stimTrial == 1])
    miss = len(df[df.response == 0][df.stimTrial == 1])
    true_neg = len(df[df.response == 0][df.stimTrial == 0]) 
    false_pos = len(df[df.response == 1][df.stimTrial == 0])

    try: pHit = (hits / len(df[df.stimTrial == 1])) #P('response'| stimulus present)
    except: pHit = 1/(2*N)
    try: pFAl = (false_pos / len(df[df.stimTrial == 0])) #P('response'| stimulus present)
    except: pFAl = 1/(2*N)

    if (pHit == 0): pHit =  1 - 1/(2*N)
    if (pFAl == 0): pFAl =  1 - 1/(2*N)
    if (pHit == 1): pHit =  1/(2*N)
    if (pFAl == 1): pFAl =  1/(2*N)      

    try: 
        d_prime = z_transform(pHit) - z_transform(pFAl)
        return pHit, pFAl, d_prime
    
    except: 
        return "nan", "nan", "nan"
  
def main(port, id = "-", do_dprime =False, verbose=False, block = 20):
    
    table = ""
    
         
        
        mode = ""
                       
                        table = table + line
                        if (len(df) > 0) and not (len(df)%block):
                            
                            df = get_data(table)
                            pHit, pFAl, d_prime = calc_dprime(df)
                            table = ""
                                
                       
                    line = "%s\t%s\t%s\t%s" %(timenow(),port,id, line)
                    if colourline:
                        colourline = "%s\t%s\t%s\t%s" %(timenow(),port,id, colourline)
                    else: colourline = "%s\t%s\t%s\t%s" %(timenow(),port,id, line) 
                    
                    print colorama.Fore.YELLOW + colorama.Style.BRIGHT + colourline,
                    f.write(line)
                    
                
                

                print colorama.Style.RESET_ALL,
                
        
        #except:
        #    ser.close()
        #    print timenow() + "\tclosed port " + port
        #    f.write(timenow() + "\tclosed port " + port + "\n")
        

def get_info(port, lines = 1):
    
    info = ""
    for l in xrange(lines):

        inline = port.readline()

        if inline.startswith("#"):
            info = info + "#%s\t%s\t%s" %(timenow(), port, id, inline)
        else: 
            inline = "%s\t%s\t%s" %(timenow(), port, id, inline)
            print colorama.Fore.YELLOW, inline
            info = info + inline
            
        if (l == lines) and (port.inWaiting()):
            info = info + get_info(port, 1)
    
    if verbose: print verbose, info
    
    return info

        
        
if __name__ == '__main__':
    
    colorama.init()
    
    port = args.port
    id = args.id
    do_dprime = args.dprime
    verbose = args.verbose
    block = args.block
    frequencies = args.frequencies
    if frequencies: block = len(frequencies) * 5 #set the block proportional to the number of frequencies to be tested
    
    os.system("cls")
    
    print id, do_dprime
    
    main(port, id, do_dprime, verbose, block)
        


