#!python2

from __future__ import division

import datetime
import time
import os
import sys
import msvcrt as m          #library for dealing with keyboard events
import random

import numpy as np          #efficient array managment
import pandas as pd         #data analysis pacakge for handling data frames
from numpy.random import shuffle

import colorama as color # makes things look nice

from utilities.args import args

from utilities.numerical import *
from utilities.colorama_wrapper import *
from utilities.data_directories import *
from utilities.serial_wrapper import *
from utilities.config_loader import *
from utilities.audio import *

import sounddevice as sd


#--------------------------------------------------------------------
#         Arguments
#--------------------------------------------------------------------

verbose    =     args.verbose       # this will be a command line parameter
port       =     args.port          # a command line parameter
ID         =     args.ID            # the identity number of the animal
repeats    =     args.repeats       # number of repetitions
datapath   =     args.datapath      # a custom location to save data
weight     =     args.weight        # the weight of the animal
trialDur   =     args.trialDur      # nominally the time to idle before resetting
ITI        =     args.ITI
restore    =     args.restore
trials     =     args.trials

#----- shared paramaters -----
lickThres  =     int((args.lickThres/5)*1024)
mode       =     args.mode
punish     =     args.punish
timeout    =     args.timeout
lcount     =     args.lcount
noLick     =     args.noLick
lickTrigReward = args.lickTrigReward
reward_nogo = args.reward_nogo

t_stimONSET =   args.t_stimONSET
t_rewardDEL =   args.t_rDELAY
t_rewardDUR =   args.t_rDUR
trial_noise =   args.noise
audio       =   args.audio

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

    #This is a hacky way of updating the variables
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

            elif c in ("C", "c"): #m,Ctrl-m
                comment = raw_input("Comment: ") + ''
                with open(logfile, 'a') as log:
                    log.write("Comment:\t%s\n" %comment)
                print "Choose...\r",

            #leftkey
            elif c in ('\xe0K',):
                t_stimDUR = 100.0
                print "stimDUR:\t%s\r" %t_stimDUR,

            # right key
            elif c in ('\xe0M',):
                t_stimDUR = 600.0
                print "stimDUR:\t%s\r" %t_stimDUR,

            elif c in ('\xe0P', '\xe0H'):
                t_stimDUR = 0
                print "stimDUR:\t%s\r" %t_stimDUR,

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
                print fLIGHTBLUE_EX, "\r",
                print "-----------------------------"
                print "options       :"
                print "  ...   H     : This menu"
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
                print "-----------------------------"
                print sRESET_ALL, '\r',

            else:
                print "SPACE or ENTER to unpause"

    params = {
           'lickThres'                 :    lickThres,
           'minlickCount'              :    lcount,
           'mode'                      :    mode,
           't_noLickPer'               :    noLick,
           'timeout'                   :    int(timeout),
           't_stimDUR'                 :    t_stimDUR,
           'trialType'                 :    'N' if t_stimDUR in (600, 0) else 'G' ,
    }

    return update_bbox(ser, params, logfile, trial_df, ID = ID, verbose = verbose)

def habituation_run(df):
    #THE HANDSHAKE
    # send all current parameters to the arduino box to run the trial
    params = {
                'mode'          : mode,
                'lickThres'     : lickThres,
                't_stimDUR'     : 200,
    }

    params = update_bbox(ser, params, logfile, ID = ID, verbose = verbose)

    print colour("trial count\n"
                 "----- -----", (fMAGENTA, sBRIGHT))

    while mode == 'h':

        trial_df = {}
        line = Serial_monitor(ser, logfile, show = verbose, ID = ID, verbose = verbose).strip()

        trial_df['time'] = timenow()

        trial_df.update(Continuous_monitor_arduino(ser, logfile = logfile, ID = ID, verbose = verbose))
        menu()

        with open(df_file, 'w') as datafile:

            #update the dictionary
            trial_df.update(params)

            #convert to pandas dataframe
            trial_df = pd.DataFrame(trial_df, index=[trial_num])

            #update the global dataframe
            df = df.append(trial_df, ignore_index = True)

            #save the changes
            df.to_csv(datafile)

        #print out the times of each water delivery
        hab_df = df[df['mode'] == 'h']
        print colour("%s\t10 ul" %(timenow()), style = (sBRIGHT,))

"""
---------------------------------------------------------------------
                       MAIN FUNCTION HERE
---------------------------------------------------------------------
"""

color.init()

datapath = create_datapath(datapath) #appends todays date to the datapath
logfile = create_logfile(datapath, port = port, ID = ID) #creates a filepath for the logfile

df_file = '%s/%s_%s_000.csv' %(datapath, ID, today(),)
df = pd.DataFrame({'time':[], 'rewardCond':[], 'mode':[], 'response': [], 'outcome':[]})

#load the previous data if a session was already run for this animal, today
if os.path.isfile(df_file):
    df = df.append(pd.read_csv(df_file, index_col = 0))

df = df.dropna(subset = ['time'])
df = df.drop_duplicates('time')
comment = ""

# load the old configs
if restore:
    restore_old_config(ID)

# If a port hasn't been specified search for arduinos
if not port:
    try:
        port = get_arduino_port()
    except IOError:
        print fRED + "No Arduinos detected!"
        sys.exit(0)

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

    trial_df = update_bbox(ser, params, logfile, ID = ID , verbose = verbose)

    if mode == 'h':
        habituation_run(df)
    elif mode == 'o':
        params = {
            'mode'              : mode,
            'lickThres'         : lickThres,
            'punish_tone'       : int(0),
            'minlickCount'      : lcount,
            't_noLickPer'       : noLick,
            'timeout'           : timeout * 1000,                    #Converts back to millis
            't_stimONSET'       : t_stimONSET,
            't_rewardDEL'       : t_rewardDEL,
            't_rewardDUR'       : t_rewardDUR,
            't_trialDUR'        : trialDur * 1000,                    # converts to millis
            'lickTrigReward'    : int(lickTrigReward),
            'reward_nogo'       : int(reward_nogo),
            'audio'             : int(audio),
        }

        trial_df = update_bbox(ser, params, logfile, {}, ID = ID, verbose = verbose)
        df = df.append(pd.DataFrame(trial_df, index = [df.shape[0]+1]), ignore_index=True)

        # loop for r repeats
        for r in xrange(repeats):

            #trials = [0, 200, 50 , 100, 25, 150]
            #trials = [0, 0,0,200,200,200]
            #trials = [0, ] * 5
            #trials.append(200)

            shuffle(trials)
            print trials

            # loop for number of trials in the list of random conditions
            trial_num = 0
            while trial_num < len(trials):
                t_stimDUR = trials[trial_num]

                #THE HANDSHAKE
                # send all current parameters to the arduino box to run the trial
                params = {
                    'trialType'         : 'N' if t_stimDUR in (0, ) else 'G' ,
                    't_stimDUR'         : t_stimDUR,
                }

                params['trialType'] = 'N' if params['t_stimDUR'] in (0,) else 'G'
                trial_df.update(update_bbox(ser, params, logfile, trial_df, ID = ID, verbose = verbose))

                # create an empty dictionary to store data in
                trial_df.update({
                    'trial_num'      : trial_num,
                    'Water'          : 0,
                    'ID'             : ID,
                    'weight'         : weight,
                    'block'          : r,
                    'comment'        : comment,
                    'trial_noise'    : trial_noise,
                    'audio_cues'     : audio,
                    'response_time'  : 'nan',
                })

                # check the keys pressed during last iteration
                # adjusts options accordingly
                params.update(menu())

                if params['trialType'] == 'N' and lcount == 0:
                    params['minlickCount'] = 1
                    params['break_wrongChoice'] = int(1)
                elif params['trialType'] == 'G' and lcount == 0:
                    params['minlickCount'] = 0

                # apply the over-ride to the reward condition
                # if the over-ride has been specified

                trial_df['comment'] = comment

                trial_df.update(update_bbox(ser, params, logfile, trial_df, ID = ID, verbose = verbose))

                print colour("C: %s" %params['trialType'],
                                 style = (fMAGENTA, sBRIGHT)),

                trial_df['time'] = timenow()

                # Send the literal GO symbol
                start_time = time.time()

                ser.write("GO")
                line = Serial_monitor(ser, logfile, show = verbose, ID = ID, verbose = verbose).strip()

                if trial_noise:
                    # noise band to mimic imaging freq 512 * 30 Hz == ~ 15000Hz
                    noise = band_limited_noise(14000, 500000, samples=int(44100*trialDur), samplerate=44100)
                    noise = noise / noise.min() #normalise so it isn't too loud
                    sd.play(noise, 44100)

                #update the trial dictionary with ouptut from arduino
                trial_df.update(Continuous_monitor_arduino(ser, logfile = logfile, ID = ID, verbose = verbose))

                if trial_noise: sd.stop()

                trial_df = {k: v if type(trial_df[k]) != list else v[0]
                                        for k,v in trial_df.iteritmes()}

                """
                THAT WHICH FOLLOWS IS NOT NECESSARY TO RUN A TRIAL??
                """
                """
                #Save the data to a data frame / Save to a file
                """

                with open(df_file, 'w') as datafile:

                    trial_df['trial_num'] = trial_num

                    # make a quick lookup table of the outcome codes
                    outcome = { 'H' : 'hit', '-' : 'miss',
                                'R' : 'CR', 'f' : 'FA',}
                    try:
                        trial_df['outcome'] = outcome[trial_df['response']]
                    except KeyError:
                        trial_df['outcome'] = 'nan'

                    df = df.append(pd.DataFrame(trial_df, index=[df.shape[0]]), ignore_index = True)

                    cumWater = df['Water'].cumsum()

                    df['cumWater'] = cumWater

                    df.to_csv(datafile)

                #Print the important data and colour code for hits / misses
                print sBRIGHT, '\r',

                table = {
                            'trial_num'    : 't',
                            'trialType'    : 'type',
                            'outcome'      : 'outcome',
                            'pre_count'    : 'pre_Lick',
                            'post_count'   : 'post_Lick',
                            'rew_count'    : 'rew_Lick',
                            'Water'        : 'water',
                            't_stimDUR'    : 'dur',
                }

                colors = {
                        'CR'  : sDIM + fGREEN,
                        'hit' : fGREEN,
                        'miss' : fYELLOW,
                        'FA' : fRED,
                        '-'  : sNORMAL + fYELLOW
                }

                # prints a pretty colourised table of the outcomes
                if not pd.isnull(df['t_stimDUR'].iloc[-1]):
                    c = colors[df.outcome.values[-1]]
                    for k, label in table.iteritems():
                        print '%s%s:%s%4s' %(fWHITE + sBRIGHT, label, c, str(df[k].iloc[-1]).strip()),

                    print '\r', sRESET_ALL
                    #calculate percentage success

                    print "\r", 100 * " ", "\r                ", #clear the line

                # clear the comment field
                comment = ""

                # don't iterate if the animal licked early!
                if df.response.iloc[-1] != 'e': trial_num += 1

                # creates a set trial time if a duration has been flagged
                dur = time.time() - start_time

                if trialDur: #allows fall though for a non trial
                    print '\r',
                    while dur < trialDur:
                        dur = time.time() - start_time

                wait = 0
                print sBRIGHT, fCYAN,

                # implement the inter trial interval
                wait = random.uniform(*ITI)
                print "\rwait %2.2g s" %wait, sRESET_ALL,"\r",
                time.sleep(wait)
                print "             \r",

#implement a clean shut down if ctrl-c is pressed
except KeyboardInterrupt:
    if mode != 'o':
        update_bbox(ser, {'mode': 'o'}, logfile, ID = ID, verbose = verbose)
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
