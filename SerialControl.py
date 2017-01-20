from __future__ import division

import datetime
import ConfigParser
import time
import os
import sys
import msvcrt as m
import random

import serial
import numpy as np
import pandas as pd
from numpy.random import shuffle

from itertools import product

import colorama as color # makes things look nice
from colorama import Fore as fc
from colorama import Back as bc     
from colorama import Style

from utilities.args import args
from utilities.numerical import num, na_printr, unpack_table

import sounddevice as sd



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
ITI = args.ITI
ratio = args.ratio
restore = args.restore
trials = args.trials

#----- shared paramaters -----
lickThres = int((args.lickThres/5)*1024)
mode = args.mode
punish = args.punish
timeout = args.timeout
lcount = args.lcount
noLick = args.noLick
lickTrigReward = args.lickTrigReward
reward_nogo = args.reward_nogo

t_stimONSET = args.t_stimONSET
t_rewardDEL = args.t_rDELAY
t_rewardDUR = args.t_rDUR
trial_noise = args.noise

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
    global noLick
    global trialDur
    global timeout
    global t_rDELAY
    global t_rDUR
    global t_stimDUR
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
                comment = raw_input("Comment: ") + ''
                with open(logfile, 'a') as log:
                    log.write("Comment:\t%s\n" %comment)
                print "Choose...\r",

            #leftkey
            elif c in '\xe0K':
                t_stimDUR = 100.0
                print "stimDUR:\t%s\r" %t_stimDUR,
            
            # right key
            elif c in '\xe0M':
                t_stimDUR = 600.0
                print "stimDUR:\t%s\r" %t_stimDUR,
            
            elif c in ('\xe0P', '\xe0H'):
                t_stimDUR = 0
                print "stimDUR:\t%s\r" %t_stimDUR,
            
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
                print "input rdur:%i : set the reward duration"
                print "input rdel:%i : set the reward delay"
                print "-----------------------------"
                print color.Style.RESET_ALL, '\r',

            else:
                print "SPACE or ENTER to unpause"

    params = {
           'break_wrongChoice'         :    int(punish) if lcount > 0 else 0, # don't punish the animal if not counting licks
           'lickThres'                 :    lickThres,
           'minlickCount'              :    lcount,
           'mode'                      :    mode,
           't_noLickPer'               :    noLick,
           'timeout'                   :    int(timeout),
           't_stimDUR'                 :    t_stimDUR,
           'trialType'                 :    'N' if t_stimDUR in (600, 0) else 'G' ,
    }
    
    return update_bbox(ser, params, logfile, trial_df)

def write_out_config(params):

    write = ( 'mode',
              'lickThres',
              'break_wrongChoice',
              'punish_tone',
              'minlickCount',
              't_noLickPer',
              'timeout',
              't_stimONSET',
              't_rewardDEL',
              't_rewardDUR'
              )
    
    with open('comms.ini','r+') as cfgfile:
        Config = ConfigParser.ConfigParser()
        Config.read('comms.ini')

        if ID not in Config.sections():
            Config.add_section(ID)
        for key, value in params.iteritems():
            if key not in write:
                continue
            if type(value) == str:
                Config.set(ID, key, '"%s"' %value)
            else:
                Config.set(ID, key, value)
        Config.write(cfgfile)

def ConfigSectionMap(section, Config):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def restore_old_config():
    with open('comms.ini','r+') as cfgfile:
        Config = ConfigParser.ConfigParser()
        Config.read('comms.ini')

    print Config.sections()
    if ID in Config.sections():
        print 'previous config found for', ID
        exec_string = []
        for name, value in ConfigSectionMap(ID, Config).iteritems():
            print name, ':', value
            exec_string.append('global {name}\n'.format(name = name, value = value) +
                               '{name} = {value}\n'.format(name = name, value = value))
        exec('\n'.join(exec_string))
    else:
        print 'No previous paramaters found'

def band_limited_noise(min_freq, max_freq, samples=1024, samplerate=1):
    freqs = np.abs(np.fft.fftfreq(samples, float(1)/samplerate))
    f = np.zeros(samples)
    idx = np.where(np.logical_and(freqs>=min_freq, freqs<=max_freq))[0]
    f[idx] = 1
    return fftnoise(f)

def fftnoise(f):
    f = np.array(f, dtype='complex')
    Np = (len(f) - 1) // 2
    phases = np.random.rand(Np) * 2 * np.pi
    phases = np.cos(phases) + 1j * np.sin(phases)
    f[1:Np+1] *= phases
    f[-1:-1-Np:-1] = np.conj(f[1:Np+1])
    return np.fft.ifft(f).real

def colour (x, 
    fc = color.Fore.WHITE, 
    bc = color.Back.BLACK, 
    style = color.Style.NORMAL):
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

        fmt_line = "%s,%s" %(line.strip(), timenow())
        if line.startswith("\t#"): 
            fmt_line = "#" + fmt_line
            if verbose: print colour(fmt_line, fc.CYAN, style = Style.BRIGHT)
        if not line.startswith("-"): 
            fmt_line = '    ' + fmt_line
        
        
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
    write_out_config(params)
    
    for name, param in params.iteritems():
    
        print fc.YELLOW, color.Style.BRIGHT, name[:2], "\r",
        ser.writelines("%s:%s" %(name, param))
        if verbose: print "%s:%s" %(name, param)
        
        time.sleep(0.1)
        
        while ser.inWaiting():

            line = Serial_monitor(ser, logfile, False)[:-1]
            
            if line[:2] not in ("\t#", "- "):
                var, val = line.strip().split(":")
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

def habituation_run(df):
    #THE HANDSHAKE
    # send all current parameters to the arduino box to run the trial
    params = {
                'mode'          : mode,
                'lickThres'     : lickThres,
                't_stimDUR'     : 200,
    }

    params = update_bbox(ser, params, logfile)
    
    print colour("trial count\n"
                 "----- -----", fc.MAGENTA, style = Style.BRIGHT)

    while mode == 'h':

        trial_df = {}
        line = Serial_monitor(ser, logfile, show = verbose).strip()

        trial_df['time'] = timenow()

        while line.strip() != "- Status: Ready":
            line = Serial_monitor(ser, logfile, False)
            if line:
                if line[:2] not in ("#", "\t#", "- "):
                    var, val = line.strip().split(":")
                    trial_df[var] = num(val)
            menu()

        if 'Water'  in trial_df.keys():

            with open(df_file, 'w') as datafile:

                for k, v in params.iteritems():
                    trial_df[k] = v

                trial_df = pd.DataFrame(trial_df, index=[trial_num])


                df = df.append(trial_df, ignore_index = True)


                df.to_csv(datafile)

            #Count percent L v R
            hab_df = df[df['mode'] == 'h']
            print colour("%s\t10 ul" %(timenow()), style = Style.BRIGHT)


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
df = pd.DataFrame({'time':[], 'rewardCond':[], 'mode':[], 'response': [], 'outcome':[]})
if os.path.isfile(df_file):
    df = df.append(pd.read_csv(df_file, index_col = 0))
   
df = df.dropna(subset = ['time'])
df = df.drop_duplicates('time')
comment = ""

# making the random condition in this way means 
# there are never more than 3 in a row

# load the old configs
if restore:
    restore_old_config()

try:
    #open a file to save data in
    ser = init_serialport(port, logfile)

    # send initial paramaters to the arduino
    params = {
        'mode'              : mode,
        'lickThres'         : lickThres,
        'minlickCount'      : lcount,
        't_stimONSET'       : t_stimONSET,
    }
    
    trial_df = update_bbox(ser, params, logfile, {} )

    
    if mode == 'h':
        habituation_run(df)
    elif mode == 'o':
        params = {
            'mode'              : mode,
            'lickThres'         : lickThres,
            'break_wrongChoice' : int(punish) if lcount > 0 else 0,   #Converts to binary
            'punish_tone'       : int(0),
            'minlickCount'      : lcount,
            't_noLickPer'       : noLick,
            'timeout'           : timeout,                            #Converts back to millis
            't_stimONSET'       : t_stimONSET,
            't_rewardDEL'       : t_rewardDEL,
            't_rewardDUR'       : t_rewardDUR,
            't_trialDUR'        : trialDur * 1000,                    # converts to millis
            'lickTrigReward'    : int(lickTrigReward),
            'reward_nogo'       : int(reward_nogo),
        }

        trial_df = update_bbox(ser, params, logfile, {} )
        df = df.append(pd.DataFrame(trial_df, index = [df.shape[0]+1]), ignore_index=True)
        
        # loop for r repeats
        for r in xrange(repeats):

            Ngo, Nngo, Nblank = ratio
            
            #trials = [0, 200, 50 , 100, 25, 150]
            #trials = [0, 0,0,200,200,200]
            #trials = [0, ] * 5
            #trials.append(200)
            
            shuffle(trials)
            print trials

            # loop for number of trials in the list of random conditions

            for trial_num, t_stimDUR in enumerate(trials):

                #THE HANDSHAKE
                # send all current parameters to the arduino box to run the trial
                params = {
                    'trialType'         : 'N' if t_stimDUR in (0, ) else 'G' ,
                    't_stimDUR'         : t_stimDUR,
                }
                
                try:
                    #if df.outcome[df.response != 'e'].values[-1] == 'FA':
                    #    params['t_stimDUR'] = 600
                    #if df.outcome[df.response != 'e'].values[-1] == 'CR':
                    #    params['t_stimDUR'] = 200
                    #if df.outcome[df.response != 'e'].values[-1] == 'miss':
                    #    if df.outcome[df.response != 'e'].values[-2] == 'CR' or df.outcome[df.response != 'e'].values[-2] == 'miss':
                    #        params['t_stimDUR'] = 200
                    #if (df.outcome.values[-5:-1] == 'miss').sum() > 3:
                    #    params['minlickCount'] = 0
                    #else:
                    #    params['minlickCount'] = lcount
                    
                    operant_trials = (df.minLickCount >= 1).values
                    good_trials = (df.response != 'e').values
                    hit_trials = (df.outcome == 'hit').values
                    
                    #if t_rewardDUR > 500 and hit_trials[good_trials & operant_trials][-20:-1].sum() > 18:
                    #    print '\ngoing strong'
                    #    t_rewardDUR -= 50
                    #    params['t_rewardDUR'] = t_rewardDUR
                    #elif hit_trials[good_trials & operant_trials][-20:-1].sum() < 10:
                    #    t_rewardDUR = args.t_rDUR
                    #    params['t_rewardDUR'] = t_rewardDUR
                        
                except:
                    pass
                params['trialType'] = 'N' if params['t_stimDUR'] in (0,) else 'G'
                trial_df.update(update_bbox(ser, params, logfile, trial_df))
                

                # create an empty dictionary to store data in
                trial_df.update({
                    'trial_num'      : trial_num,
                    'Water'          : 0,
                    'ID'             : ID,
                    'weight'         : weight,
                    'block'          : r,
                    'comment'        : comment,
                    'hitVmissVblank' : '%s:%s:%s' %(Ngo, Nngo, Nblank),
                    'trial_noise'    : trial_noise,
                    'audio_cues'     : True,
                })

                #checks the keys pressed during last iteration
                #adjusts options accordingly
                
                params.update(menu())
                
                if params['trialType'] == 'N' and lcount == 0:
                    params['minlickCount'] = 1
                    params['break_wrongChoice'] = int(1)
                elif params['trialType'] == 'G' and lcount == 0:
                    params['minlickCount'] = 0
                
                # apply the over-ride to the reward condition
                # if the over-ride has been specified

                trial_df['comment'] = comment


                trial_df.update(update_bbox(ser, params, logfile, trial_df))
                
                print colour("C: %s" %params['trialType'], 
                                fc.MAGENTA, style = Style.BRIGHT),

                trial_df['time'] = timenow()
                
                # Send the literal GO symbol
                start_time = time.time()
            
                ser.write("GO")
                line = Serial_monitor(ser, logfile, show = verbose).strip()
                
                if trial_noise:
                    # noise band to mimic imaging freq 512 * 30 Hz == ~ 15000Hz
                    noise = band_limited_noise(14000, 500000, samples=int(44100*trialDur), samplerate=44100)
                    noise = noise/ noise.min()
                    sd.play(noise*.5, 44100)

                while line.strip() != "- Status: Ready":
                    # keep running until arduino reports it has broken out of loop
                    line = Serial_monitor(ser, logfile, False)
                    if line:
                        if line[:2] not in ("#", "\t#", "- "):
                            var, val = line.strip().split(":")
                            #print  fc.GREEN, "\r", var[:5], val, Style.RESET_ALL , "\r",
                            trial_df[var] = num(val)

                if trial_noise: sd.stop()
                
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

                    df = df.append(pd.DataFrame(trial_df, index=[trial_num]), ignore_index = True)

                    cumWater = df['Water'].cumsum()

                    df['outcome'] = '-'
                    
                    outcome = df.outcome.copy()
                    
                    hit = (df.response == 'H').values
                    miss = (df.response == '-').values
                    correct_reject = (df.response == 'R')
                    false_alarm = (df.response == 'f').values
                    
                    outcome[hit] = 'hit'
                    outcome[correct_reject] = 'CR'
                    outcome[miss] = 'miss'
                    outcome[false_alarm] = 'FA'
                    df['outcome'] = outcome
                    
                    
                    df['cumWater'] = cumWater
                    df['trial_num'] = df.shape[0]
                    
                    #TODO: calculate delta
                    
                    df.to_csv(datafile)
                
                #Print the important data and coloured code for hits / misses  
                print Style.BRIGHT, '\r', 
                
                table = {
                            'trial_num'    : 't', 
                            'trialType'    : 'type',
                            'outcome'      : 'outcome', 
                            'pre_count'    : 'pre_Lick', 
                            'post_count'   : 'post_Lick', 
                            'rew_count'    : 'rew_Lick',
                            #'delta'        : 'lick change', 
                            'Water'        : 'water', 
                            't_stimDUR'    : 'dur',
                }
                
                colors = {
                        'CR'  : Style.DIM + fc.GREEN,
                        'hit' : fc.GREEN,
                        'miss' : fc.YELLOW,
                        'FA' : fc.RED,
                        '-'  : Style.NORMAL + fc.YELLOW
                }
                

                if not pd.isnull(df['t_stimDUR'].iloc[-1]):
                    c = colors[df.outcome.values[-1]]
                    for k, label in table.iteritems():
                        print '%s%s:%s%4s' %(fc.WHITE + Style.BRIGHT, label, c, str(df[k].iloc[-1]).strip()),

                    print '\r', Style.RESET_ALL
                    #calculate percentage success
                    
                    print "\r", 100 * " ", "\r                ", #clear the line 

                comment = ""
                trial_num += 1            
                
                # creates a set trial time if a duration has been flagged
                dur = time.time() - start_time

                if trialDur: #allows fall though for a non trial
                    #print np.isnan(df['OFF[0]'].iloc[-1]).all(),
                    print '\r',
                    while dur < trialDur:
                        dur = time.time() - start_time


                wait = 0
                print Style.BRIGHT, fc.GREEN,
                
                wait = random.uniform(*ITI)
                print fc.CYAN,
                print "\rwait %2.2g s" %wait, Style.RESET_ALL,"\r",
                time.sleep(wait)
                print "             \r",


except KeyboardInterrupt:
    if mode != 'o':
        update_bbox(ser, {'mode': 'o'}, logfile)
    else:
        try:
            print "attempting to create DataFrame"
            trial_df = pd.DataFrame(trial_df, index=[trial_num])
            
            try: 
                df = df.append(trial_df, ignore_index = True)
            except NameError:
                df = trial_df

            cumWater = df['Water'].cumsum()

            
            df['cumWater'] = cumWater               

            df.to_csv(df_file)
        except NameError:
            print "unable to create trial_df does not exist"
        except AttributeError:
            df.to_csv(df_file)
            print "saved df"

        print "Closing", port
        sys.exit(0)