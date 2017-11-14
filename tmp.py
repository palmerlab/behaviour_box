from __future__ import print_function, division

import serial
import time

import numpy as np
from itertools import product

port = 'COM4'

"""
--------------------------------------------------------------------------------
                        I N I T I A L I S E
--------------------------------------------------------------------------------
"""

#open Serial port
ser = serial.Serial(port = port, baudrate = 115200, timeout = 1,)

#IDLE while Arduino performs it's setup functions
print("awaiting arduino: ", end='\b')
_ = 0;
while not ser.inWaiting():
    print(r'-\|/'[_%3], end='\b'); _+=1
    time.sleep(.05)
print(" ONLINE", end=' ')

# Buffer for 500 ms to let Arduino finish it's setup
time.sleep(.5)

# Read in debug info? In the redo there will be none of this,
while ser.inWaiting():
    line = ser.readline()
print(line)

#Serial monitor
#line = ser.readline()

"""
--------------------------------------------------------------------------------
                    [TODO]    R E A D    S E T U P
"""



"""
--------------------------------------------------------------------------------
                        R U N     T R I A L
"""

#   | stimulus duration | light_stim | light_resp |
trials = np.array([trial for trial in product((0,1), (0,1), (0,1))],
                    dtype = bool)


# construct a command string: trial type / light_0 / light_1
# note that in Jay's protocol the stimulus is either on or off, so
# we can therefore hard code the stimulus duration
# we send a string

"""
Trial Codes:
           St  Ls  Lr
    0       0   0   0
    1       0   0   1
    2       0   1   0
    3       0   1   1
    4       1   0   0
    5       1   0   1
    6       1   1   0
    7       1   1   1

    0 0 0 0   0 0 0 0

where St = Stim; Ls = Light_stim; Lr = Light_response
"""

for (st, ls, lr) in trials:

    trial_code = (st << 2) | (ls << 1) | lr


    print(trial_code, end=':')
    ser.write(chr(trial_code))

    msg = None

    try:
        while msg != 0:
        # # send trial_code as a byte
            msg = ser.read(4)
            msg, = np.fromstring(msg, dtype='i4')
            print(msg, end=' ') # recieve
    except:
        pass

ser.close()
