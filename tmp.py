from __future__ import print_function, division

import serial
import time
import datetime

import numpy as np
from itertools import product


port = 'COM4'
#   | stimulus duration | light_stim | light_resp |
trials = np.array([trial for trial in product((0,1), (0,1), (0,1))], dtype=bool)

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



def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')

def startup(ser):
    #IDLE while Arduino performs it's setup functions
    print("awaiting arduino: ", end='\b')
    _ = 0;
    while not ser.inWaiting():
        print(r'-\|/'[_%3], end='\b'); _+=1
        time.sleep(.05)
    print(" ONLINE", end=' ')
    # Buffer for 500 ms to let Arduino finish it's setup
    time.sleep(.75)

def run_trial(ser, trial_code):
    # Handshake
    ser.write(chr(trial_code))
    while not ser.inWaiting(): pass
    echo_tc = ord(ser.read(1))

    #params = [ser.readline() for i in range(3)]

    msg = None
    msgs = []
    while msg != '\x00\x00\x00':
        #timestamp the first message
        if msg is None: tstamp = timenow()
        if not ser.inWaiting(): continue
        msg = ser.read(3)
        print(msg)
        msgs.append(msg) # recieve

    #unpack:
    chans = {abs(np.fromstring(m[0], dtype='b')[0]) for m in msgs}
    timings = {k:[] for k in chans}

    for msg in msgs:
        chan, = np.fromstring(msg[0], dtype='b')
        time, = np.fromstring(msg[1:], dtype='i2')
        timings[abs(chan)].append((time, chan > 0))

    trial_results = {k:v for k,v in
                        [l.split(':') for l in
                            ser.read(ser.inWaiting()).split()]}

    return echo_tc, tstamp, timings, trial_results

"""
--------------------------------------------------------------------------------
                        I N I T I A L I S E
--------------------------------------------------------------------------------
"""

#open Serial port
ser_params = {'port':port, 'baudrate':115200, 'timeout':1}

"""
--------------------------------------------------------------------------------
                        R U N     T R I A L
"""
with serial.Serial(**ser_params) as ser:
    'initialisiation'
    startup(ser)
    # makes a list of all the settngs
    # Theses are the adjustable paramaters from USER_variables.h
    time.sleep(1)
    ard_settings = ser.read(ser.inWaiting())

    for (st, ls, lr) in trials:
        trial_code = (st << 2) | (ls << 1) | lr

        out = run_trial(ser, trial_code)
        break
