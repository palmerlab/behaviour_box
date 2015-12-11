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
import random
import AndrewSignalDetection as sig

from itertools import product
      
      
import colorama as c # makes things look nice
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

"""




"""
    ------------
    Arguments
    ------------
"""

p = argparse.ArgumentParser(description="This program controls the Arduino and reads from it too" )

p.add_argument("-v", "--verbose", action='store_true', help = 'for debug, will print everything if enabled')
p.add_argument("-p", "--port", default = "COM5", help = "port that the Arduino is connected to")
p.add_argument("-i", "--ID", default = "", help = "identifier for this animal/run")
p.add_argument("-m", "--mode", default = "", help = "the mode `c`onditioning or `o`perant, by default will look in the config table")
p.add_argument('-f','--freq', nargs='*', type=int, help="list of frequencies in Hz (separated by spaces)")
p.add_argument('-r', '--repeats', default = "1", type=int, help="the number of times this block should repeat, by default this is 1")
p.add_argument('--datapath', default = "", help = "path to save data to, by default is '.\\YYMMDD'")
p.add_argument('--singlestim', action='store_true', help = "For anaesthetised experiments, only run a single stimulus")

arg_group = p.add_mutually_exclusive_group()
arg_group.add_argument('--ITI',  nargs='+', default = [5], type=float, help="an interval for randomising between trials")
arg_group.add_argument('--triggered',  action='store_true', help="waits for key press to initiate a trial")

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
    
def goto_interpreter():
    """
    
    """
    if m.kbhit():
        c = m.getch()
        if c == '\xe0': c = m.getch()
        
        if c == '\x1b':
            sys.exit(0)
        
        else:    
            mode = raw_input(">>> ")
            exec(mode)
            print _
            return

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
        
def colour (x, fc = c.Fore.WHITE, bc = c.Back.BLACK, style = c.Style.NORMAL):
    return "%s%s%s%s%s" %(fc, bc, style, x , c.Style.RESET_ALL)


def unpack_table(filename):

    reader = csv.reader(open(filename, 'r'), delimiter = "\t")
    d = {}
    for row in reader:
       k, v = row
       d[k] = v
    
    return d

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return str(datetime.datetime.now().time().strftime('%H:%M:%S'))      
      
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

def Serial_monitor(logfile):
    
    line = ser.readline()
    
    if line:
        
        fmt_line = "%s\t%s\t%s\t%s" %(timenow(), port, ID, line.strip())
        
        if line.startswith("#"): 
            fmt_line = "#" + fmt_line
            if verbose: print colour(fmt_line, fc.CYAN, style = Style.BRIGHT)
        
        elif line[0] != "#": 
            
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
        #print "%s:%s" %(k, params[k])
        time.sleep(0.2)
        

def create_datapath(DATADIR = ""):
    """
    
    """
    date = datetime.date.today().strftime('%y%m%d')
    
    if not DATADIR: DATADIR = os.path.join(os.getcwd(), date)
    else: DATADIR = os.path.join(DATADIR, date)
    
    if not os.path.isdir(DATADIR):
        os.mkdir((DATADIR))
    
    print colour("datapath: \n\t", fc = fc.GREEN, style=Style.BRIGHT),
    print colour(DATADIR.replace("\\", "\\\\"), fc = fc.GREEN, style=Style.BRIGHT)
    
    return DATADIR        

        
def create_logfile(DATADIR = ""):
    """
    
    """
    date = datetime.date.today().strftime('%y%m%d')
    
    filename = "%s_%s_%s.log" %(port,ID,date)
    logfile = os.path.join(DATADIR, filename)
    print colour("Saving log in: \n\t", fc = fc.GREEN, style=Style.BRIGHT),
    print colour(".\\$datapath$\\%s" %filename, fc = fc.GREEN, style=Style.BRIGHT)
    
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
            elif key == 72 or key == 80: #Up or Down
                response = "-"

        line = "%s\tManual declared response at:%s" %(timenow(), response)

        print colour(line, fc.MAGENTA, style = Style.BRIGHT)

        logfile.write(line+"\n")

    return [response], [response_time]    

"""

MAIN FUNCTION HERE

"""    
    
    
if __name__ == "__main__":
    try:
        args = p.parse_args()

        verbose = args.verbose # this will be a cmdline parameter
        port = args.port # a commandline parameter
        ID = args.ID
        repeats = args.repeats
        datapath = args.datapath
        singlestim = args.singlestim
        
        c.init()
        
        datapath = create_datapath(datapath) #appends todays date to the datapath
        logfile = create_logfile(datapath) #creates a filepath for the logfile
        
        
        # open communications
        
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
            
        date = datetime.date.today().strftime('%y%m%d')
        
        params_i = unpack_table('config.tab')
        if args.mode: params_i['mode'] = args.mode
        params = params_i
        
        freq = np.loadtxt('frequencies.tab', skiprows = 1)
        if args.freq: freq = args.freq

        #generate the frequency pairs
        if singlestim: 
            freq = np.array([freq, np.zeros(len(freq))])
        else:
            tmp_freq = []        
            for f in product(freq, freq): 
                tmp_freq.append(np.array(f))
            freq = tmp_freq
            del tmp_freq

        #set the block proportional to the number of freq to be tested
        block = len(freq) * 5 
        freq = np.array(freq)
        
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
            
            
            for r in xrange(repeats):
                
                print colour("BLOCK:\t%02d" %r, 
                    fc.MAGENTA, style = Style.BRIGHT)
                    
                # shuffle the frequencies
                shuffle(freq)
                
                
                #This starts a loop that goes through 1 run per frequency combination
                for t in xrange(len(freq)):

                    #TODO: this should be a separate thread!
                    if not args.triggered: goto_interpreter()
                    # create an empty dictionary to store data in
                    trial_df = {}
                    
                    trial_df['trial_num'] = [trial_num]
                    trial_df['port[0]'] = [0]
                    trial_df['port[1]'] = [0]
                    trial_df['response'] = [None]
                    trial_df['response_time'] = [None]
                    
                    # convert the frequencies into an on off square pulse
                    for f in (0,1):
                        trial_df['freq%d' %f] = [freq[t][f]]
                        # if the frequency is 0 make the on time = 0
                        if freq[t][f] == 0: 
                            params['ON[%d]' %f] = 0
                            params['OFF[%d]' %f] = 10 # ms
                        # off period = (1000 ms / frequency Hz) - 5 ms ~ON period~
                        else:
                            params['ON[%d]' %f] = 10
                            params['OFF[%d]' %f] = (1000/freq[t][f]) - 10
                    
                    
                    
                    # Determine the reward condition
                    #     1. f0 > f1 :: lick left
                    #     2. f0 < f1 :: lick right
                    #     3. f0 == 0 OR f1 == 0, either port is valid
                    #     4. f0 == 0 AND f1 == 0, neither port is valid
                    
                    if freq[t][0] and freq[t][1]:
                        if freq[t][0] == freq[t][1]: params['rewardCond'] = 'B'
                        if freq[t][0] > freq[t][1]: params['rewardCond'] = 'L'
                        if freq[t][0] < freq[t][1]: params['rewardCond'] = 'R'
                    
                    else:
                        if freq[t][0] or freq[t][1]:params['rewardCond'] = 'B'
                        else: params['rewardCond'] = 'N'
                    
                    print colour("frequencies:\t%s\t%s\nCondition:\t%s" %(freq[t][0], freq[t][1], params['rewardCond']), fc.MAGENTA, style = Style.BRIGHT)
                    
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
                    #if type(args.ITI) is not int:
                    #    try: ITI = random.uniform(args.ITI[0], args.ITI[1])
                    #    except: ITI = random.uniform(2,5)
                    #else: 
                    if not args.triggered:
                        
                        ITI = args.ITI[0]
                        
                        print "about to go in %d"  %ITI
                        print colour("frequencies:\t%s\t%s\nCondition:\t%s" %(freq[t][0], freq[t][1], params['rewardCond']), fc.MAGENTA, style = Style.BRIGHT)
                        time.sleep(ITI)
                    
                    else:
                        print colour("frequencies:\t%s\t%s\nCondition:\t%s" %(freq[t][0], freq[t][1], params['rewardCond']), fc.MAGENTA, style = Style.BRIGHT)
                        while m.kbhit() == False:
                            print colour("%s waiting for trigger\r" %(timenow()), fc.RED, style = Style.BRIGHT),
                        while m.kbhit():
                            m.getch() #clear the buffer
                        
                    print colour("\nGO!\n%s" %timenow(), fc.GREEN, style=Style.BRIGHT)
                        
                    trial_df['time'] = [timenow()]
                    
                    # Send the literal GO symbol
                    ser.write("GO")

                    while line.strip() != "-- Status: Ready --":
                        
                        line = Serial_monitor(log).strip()
                        if line:
                            if line[0] != "#" and line[0] != "-":
                                var, val = line.split(":\t")
                                val = num(val)
                                try: trial_df[var].append(val)
                                except KeyError: trial_df[var] = [val]
                                except AttributeError: trial_df[var] = [trial_df[var], val]
                            
                                if (trial_df['response'] == [None]) and ("port" in var):
                                    
                                    trial_df['response_time'] = [timenow()]
                                    trial_df['response'] = ["L"] if var == "port[0]" else ["R"]
                                    
                    
                    while trial_df['response'] == [None]:
                        if args.triggered:
                            trial_df['response'], trial_df['response_time'] = manual_response_check(log)
                        else:
                            trial_df['response'] = ["-"]
                            trial_df['response_time'] = ["-"]
                        
                        # manually activate the vacuum?
                        if trial_df['response'] == ["-"]:
                            ser.write("VacOn")
                    
                    # patitions lick responses into three handy numbers each
                    licksL = np.array(trial_df['port[0]'])
                    licksR = np.array(trial_df['port[1]'])

                    t_f0 = num(params['t_stimONSET[0]'])
                    t_f1 = num(params['t_stimONSET[1]'])
                    t_post = params['t_rewardSTART']
                                       
                    try: trial_df['left_pre'] = [licksL[licksL < t_f0].sum()]
                    except: trial_df['left_pre'] = [0]
                    try: trial_df['left_stim'] = [licksL[(licksL > t_f0) & (licksL < t_post)].sum()]
                    except: trial_df['left_stim'] = [0]
                    try: trial_df['left_post'] = [licksL[licksL > t_post].sum()]
                    except: trial_df['left_post'] = [0]
                                                                                        
                    try: trial_df['right_pre'] = [licksR[licksR < t_f0].sum()]
                    except: trial_df['right_pre'] = [0]
                    try: trial_df['right_stim'] = [licksR[(licksR > t_f0) & (licksR < t_post)].sum()]
                    except: trial_df['right_stim'] = [0]
                    try: trial_df['right_post'] = [licksR[licksR > t_post].sum()]
                    except: trial_df['right_post'] = [0]
                             
                    np.savetxt("port[0]_%s_trial%s.tab" %(ID, trial_num), trial_df['port[0]'], fmt = '%d')
                    np.savetxt("port[1]_%strial%s.tab" %(ID, trial_num), trial_df['port[1]'], fmt = '%d')
                    
                    del trial_df['port[0]']
                    del trial_df['port[1]']
                    
                    trial_df['ID'] = [ID]
                    
                    trial_df = pd.DataFrame(trial_df)
                    
                    with open('%s\\data.tab' %date, 'a') as datafile:
                        trial_df.to_csv(datafile, 
                            header=(trial_num==0), sep = "\t",
                            index=False)
                    
                    trial_num += 1
                
    except KeyboardInterrupt:
        sys.exit(0)


