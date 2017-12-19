"""===========================================================================++
                                I M P O R T S                                 ||
   ===========================================================================++
"""
from __future__ import print_function, division

import string
import serial
import time
import datetime
import json
import os
import sys

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

datapath = '.'        # location to save files
fname = ''            # name to append to the files

ITI = 2, 5            # range of the inter trial interval
port = 'COM7'         # port arduino is connected to

mode = 'o'
"""-------------------------- hidden globals --------------------------------"""

STOP = '\x00\x00\x00' # DONT TOUCH this is the bbox termination pattern

chan_dict = {4: 'bulbTrig',  5: 'stimulusPin',  6: 'buzzerPin',
             7: 'speakerPin', 13: 'statusLED',  2: 'lightPin',
             14: 'lickSens', 10: 'waterPort'}

today = datetime.date.today().strftime('%y%m%d')

"""===========================================================================++
                         M A I N    F U N C T I O N S                         ||
   ===========================================================================++
"""

def main(ID='', port=port, datapath=datapath, fname=fname, mode=mode, **kwargs):
    if not os.path.exists(datapath):
        os.makedirs(datapath)

    if not fname:
        fname = '_'.join((ID, today))

        ser_params = {'port':port, 'baudrate':115200, 'timeout':1}

    with serial.Serial(**ser_params) as ser:
        'initialisiation'
        settings = startup(ser)
        # makes a list of all the settngs
        # Theses are the adjustable paramaters from USER_variables.h

        if mode == 'o':
            operant(ser, settings=settings, datapath=datapath, fname=fname, **kwargs)
        elif mode == 'h':
            habituation(ser, datapath=datapath, fname=fname, settings=settings, ID=ID, **kwargs)
    return

def operant(ser, settings={}, repeats=repeats, ITI=ITI,
         Stim=Stim, Light_stim=Light_stim, Light_resp=Light_resp,
         port=port, datapath=datapath, fname=fname, **kwargs):

     #   | stimulus duration | light_stim | light_resp |
     _gt = product(Stim, Light_stim, Light_resp)
     trials = np.array([trial for trial in _gt], dtype=bool)
     print('ready go')
     for i in range(repeats):

         shuffle(trials)
         j = 0
         while j < len(trials):
             # pack the 3 bits into a single number
             st, ls, lr = trials[j]
             trial_code = (st << 2) | (ls << 1) | lr

             trial_data = settings.copy()

             '''run the trial'''

             tc, tstamp, timings, result = run_trial(ser, trial_code, **settings)

             if result['response'] == 'e': continue

             trial_data.update(result)
             trial_data['code'] = tc
             trial_data['time'] = tstamp
             trial_data['block'] = i
             trial_data['trial'] = j
             trial_data['mode'] = 'operant'

             sp = '/'.join((datapath, fname + '.yaml'))
             with open(sp, 'a') as f:
                 print('---', file=f)
                 [print(k,':',v, file=f) for k,v in trial_data.items()]
                 print('...', file=f)

             sp = '/'.join((datapath, fname + '.json'))
             with open(sp, 'a') as f:
                 s = json.dumps(timings)
                 print(tstamp, file=f)
                 print(s, file=f)

             print(j, trial_data['response'],)
             j += 1
             a,b = ITI
             _ = (b-a) * np.random.random() + a
             time.sleep(_)

def habituation(ser, datapath=datapath, fname=fname,  settings={}, ID='', **kwargs):
    c_water = 0
    ser.write('h')
    while not ser.inWaiting(): pass
    echo_tc = ord(ser.read(1))

    trial_data = settings.copy()

    '''run the trial'''
    while True:
        tstamp, timings = run_habituation(ser)
        c_water += 10

        sp = '/'.join((datapath, fname + '.json'))
        with open(sp, 'a') as f:
            s = json.dumps(timings)
            print(tstamp, file=f)
            print(s, file=f)

        sp = '/'.join((datapath, fname + '_habit.csv'))
        with open(sp, 'a') as f:
            print(tstamp, '~', c_water,'uL')
            print(ID, tstamp, c_water, sep = ',', file=f)

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

def run_habituation(ser):

    start_time = time.time()

    msg = None
    msgs = []
    _ = 0;
    while True:#msg != STOP:
        #timestamp the first message
        if msg is None: tstamp = timenow()
        if not ser.inWaiting(): print('-+*+-'[_%4], end='\b'); _+=1; continue

        msg = ser.read(3)
        if msg == STOP: break
        print(r'-\|/'[_%3], end='\b'); _+=1
        #print(msg)
        msgs.append(msg) # recieve

    timings = package_sparse(msgs)

    return tstamp, timings

def run_trial(ser, trial_code, trialDUR = 0, **kwargs):
    # Handshake
    ser.write(chr(trial_code))
    while not ser.inWaiting(): pass
    echo_tc = ord(ser.read(1))

    trialDUR = int(trialDUR)
    if trialDUR > 5: trialDUR = 5

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
        if msg == STOP: break
        print(r'-\|/'[_%3], end='\b'); _+=1
        #print(msg)
        msgs.append(msg) # recieve

        # check the time
        dur = (time.time() - start_time) * 1000
        if dur >= trialDUR: break

    timings = package_sparse(msgs)
    results = read_dict(ser)

    return echo_tc, tstamp, timings, results

def startup(ser):
    #IDLE while Arduino performs it's setup functions
    print("awaiting arduino: ", end='\b')
    _ = 0;
    while not ser.inWaiting():
        print(r'-\|/'[_%3], end='\b'); _+=1
        time.sleep(.05)
    print(" ONLINE")
    # Buffer for 500 ms to let Arduino finish it's setup
    time.sleep(2)
    ser.readline()

    return read_dict(ser)

def read_dict(ser):
    msg = None
    _dict = {}
    while msg != STOP:
        if not ser.inWaiting(): continue
        msg = ser.readline()
        if msg == STOP: break
        else:
            msg = msg.replace(STOP, '')
            try:

                k,v = msg.strip().split(':')
                _dict[k] = v
            except ValueError:
                pass
                #_dict['unparsed'] = "'" + msg.strip() + "'"
    return _dict

def package_sparse(msgs):

    timings = {chan_dict[k]:[] for k in chan_dict}

    for msg in msgs:
        chan, = np.fromstring(msg[0], dtype='b')
        t, = np.fromstring(msg[1:], dtype='u2')
        timings[chan_dict[abs(chan)]].append((int(t), int(chan > 0)))

    return timings

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')

if __name__ == '__main__':
    print('party time')

    kwargs = vars(args) # grab the commandline arguments into a dictionary,

    try:
        main(**kwargs);     # and feed to main
    except KeyboardInterrupt:
        quit()
