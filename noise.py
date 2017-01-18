import sounddevice as sd
import numpy as np
import sys

usage = '''noise.py volume
'''

vol = 0.15
if len(sys.argv) > 1:
    vol = int(sys.argv[1]) / 100.0
else:
    print usage

noise = np.random.rand(44100 * 30) * vol
sd.play(noise, 44100, loop = True)

# Snippet to make a clean exit
try: 
    while True: pass
except: pass