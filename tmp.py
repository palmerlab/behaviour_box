"""===========================================================================++
                                I M P O R T S                                 ||
   ===========================================================================++
"""
from __future__ import print_function, division

import serial
import time
import datetime

import numpy as np
from numpy.random import shuffle
from itertools import product

from utilities.args import args
"""===========================================================================++
                         C O N F I G U R A T I O N                            ||
   ===========================================================================++
"""

Stim       = (1,)     # use to `(1,)` or `(0,)` for always on, or always off
Light_stim = (0,)     # use to `(1,)` or `(0,)` for always on, or always off
Light_resp = (0,)     # use to `(1,)` or `(0,)` for always on, or always off

repeats = 5           # number of times to run through trials

ITI = 2, 5            # range of the inter trial interval
port = 'COM7'         # port arduino is connected to

"""-------------------------- hidden globals --------------------------------"""
STOP = '\x00\x00\x00' # DONT TOUCH this is the bbox termination pattern


"""===========================================================================++
                         M A I N    F U N C T I O N                           ||
   ===========================================================================++
"""

def main(**kwargs):
    #open Serial port
    ser_params = {'port':port, 'baudrate':115200, 'timeout':1}

    df_long = []
    df_sparse = []
    with serial.Serial(**ser_params) as ser:
        'initialisiation'
        settings = startup(ser)
        # makes a list of all the settngs
        # Theses are the adjustable paramaters from USER_variables.h

        #   | stimulus duration | light_stim | light_resp |
        _gt = product(Stim, Light_stim, Light_resp)
        trials = np.array([trial for trial in _gt], dtype=bool)
        print('ready go')
        for i in range(repeats):
            print(i)
            shuffle(trials)

            j = 0
            print('\ntrials :', trials, '\n')
            while j <= len(trials):
                # pack the 3 bits into a single number
                st, ls, lr = trials[j]
                trial_code = (st << 2) | (ls << 1) | lr

                trial_data = settings.copy()

                print('run the trial')

                tc, tstamp, timings, result = run_trial(ser, trial_code, **settings)

                if result['response'] == 'e': print('e'); continue

                trial_data.update(result)
                trial_data['code'] = tc
                trial_data['time'] = tstamp
                trial_data['block'] = i
                trial_data['trial'] = j

                df_long.append(trial_data)
                with open('this.yaml', 'a') as sf:
                    print('---', file=sf)
                    [print(k,':',v, file=sf) for k,v in trial_data.items()]
                df_sparse.append(timings)
                j += 1
                print(j, end = ', ')

	return settings, df_sparse, df_long

'''
save the shit:

dataframe with trial results
[block, trial, time, trial_code, *trial_results]
- ...
- ...
- ...

'''


""" Trial Codes:
           St  Ls  Lr         |
    0       0   0   0         | where St = Stim; Ls = Light_stim;
    1       0   0   1         | Lr = Light_response.
    2       0   1   0         | These settings are sent in an 8 bit character,
    3       0   1   1         | where the payload is on the last 3 bits.
    4       1   0   0         |              * * *
    5       1   0   1         |  0 0 0 0   0 0 0 0
    6       1   1   0         |
    7       1   1   1         |
"""

"""===========================================================================++
                              F U N C T I O N S                               ||
                            in order of importance                            ||
   ===========================================================================++
"""

def run_trial(ser, trial_code, trialDUR = 0, **kwargs):
    # Handshake
    ser.write(chr(trial_code))
    while not ser.inWaiting(): pass
    echo_tc = ord(ser.read(1))

    trialDUR = int(trialDUR)

    #params = [ser.readline() for i in range(3)]
    start_time = time.time()

    msg = None
    msgs = []
    _ = 0;
    while True:#msg != STOP:
        #timestamp the first message
        if msg is None: tstamp = timenow()
        if not ser.inWaiting(): print('-+*+-'[_%4], end='\b'); _+=1; continue

        msg = ser.read(3)
        if msg == STOP: print('STOP'); break
        print(r'-\|/'[_%3], end='\b'); _+=1
        #print(msg)
        msgs.append(msg) # recieve

        # check the time
        dur = (time.time() - start_time) * 1000
        if dur >= trialDUR: print('OUT OF TIME:', dur); break

    #channames = [bulbTrig, stimulusPin, buzzerPin, speakerPin, statusLED,
                    #lightPin, lickSens, waterPort]
    chans = [4, 5, 6, 7, 13, 2, 14, 10, ]
    timings = {k:[] for k in chans}

    for msg in msgs:
        chan, = np.fromstring(msg[0], dtype='b')
        t, = np.fromstring(msg[1:], dtype='u2')
        timings[abs(chan)].append((t, chan > 0))

    results = read_dict(ser)

    return echo_tc, tstamp, timings, results

def startup(ser):
    #IDLE while Arduino performs it's setup functions
    print("awaiting arduino: ", end='\b')
    _ = 0;
    while not ser.inWaiting():
        print(r'-\|/'[_%3], end='\b'); _+=1
        time.sleep(.05)
    print(" ONLINE", end=' ')
    # Buffer for 500 ms to let Arduino finish it's setup
    time.sleep(2)

    return read_dict(ser)

def read_dict(ser):
    msg = None
    _dict = {}
    while msg != STOP:
        if not ser.inWaiting(): continue
        msg = ser.readline()
        if msg == STOP: break
        else:
            print(msg)
            k,v = msg.strip().split(':')
            _dict[k] = v
    return _dict

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')


if __name__ == '__main__':
    print('party time')

    #kwargs = vars(args) # grab the commandline arguments into a dictionary,
    #main(**kwargs);     # and feed to main
