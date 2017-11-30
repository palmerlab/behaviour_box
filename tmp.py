from __future__ import print_function, division

import serial
import time
import datetime

import numpy as np
from numpy.random import shuffle
from itertools import product

"""===========================================================================++
                         C O N F I G U R A T I O N                            ||
   ===========================================================================++
"""

Stim       = (1,)    # use to `(1,)` or `(0,)` for always on, or always off
Light_stim = (0,)    # use to `(1,)` or `(0,)` for always on, or always off
Light_resp = (0,)    # use to `(1,)` or `(0,)` for always on, or always off

repeats = 5           # number of times to run through trials


port = 'COM6'         # port arduino is connected to
STOP = '\x00\x00\x00' # DONT TOUCH THIS
"""===========================================================================++
                         M A I N    F U N C T I O N                           ||
   ===========================================================================++
"""

def main():
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

        for i in range(repeats):
            shuffle(trials)

            j = 0
            while j < len(trials):
                # pack the 3 bits into a single number
                st, ls, lr = trials[j]
                trial_code = (st << 2) | (ls << 1) | lr

                trial_data = settings.copy()

                'run the trial'
                _ = run_trial(ser, trial_code)
                echo_tc, tstamp, timings, trial_results = _

                if trial_results['response'] == 'e': continue

                trial_data.update(trial_results)
                trial_data['code'] = echo_tc
                trial_data['time'] = tstamp
                trial_data['block'] = i
                trial_data['trial'] = j

                df_long.append(trial_data)
                df_sparse.append(timings)
                j += 1
			
	return settings, df_sparse, df_long, i,j

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

def run_trial(ser, trial_code):
    # Handshake
    ser.write(chr(trial_code))
    while not ser.inWaiting(): pass
    echo_tc = ord(ser.read(1))

    #params = [ser.readline() for i in range(3)]

    msg = None
    msgs = []
    while msg != STOP:
        #timestamp the first message
        if msg is None: tstamp = timenow()
        if not ser.inWaiting(): continue
        msg = ser.read(3)
        if msg == STOP: break
        print(msg)
        msgs.append(msg) # recieve

    #channames = [bulbTrig, stimulusPin, buzzerPin, speakerPin, statusLED,
                    #lightPin, lickSens, waterPort]
    chans = [4, 5, 6, 7, 13, 2, 14, 10, ]
    timings = {k:[] for k in chans}

    for msg in msgs:
        chan, = np.fromstring(msg[0], dtype='b')
        t, = np.fromstring(msg[1:], dtype='u2')
        timings[abs(chan)].append((t, chan > 0))

    trial_results = read_dict(ser)

    return echo_tc, tstamp, timings, trial_results

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
            k,v = msg.strip().split(':')
            _dict[k] = v
    return _dict

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')

	
if __name__ == '__main__':
	print('party time')
	main();
