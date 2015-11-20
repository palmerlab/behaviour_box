from __future__ import division

import datetime
import time
import os
import sys
import glob
import serial
import msvcrt as m

import sys, serial, argparse
import numpy as np
from numpy.random import random_integers
from time import sleep
from collections import deque
import pandas as pd
from StringIO import StringIO

import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from scipy.stats import norm
import os
import sys
import msvcrt as m
import argparse
import warnings
warnings.simplefilter(action = "ignore", category = UserWarning)

import colorama
colorama.init()


parser = argparse.ArgumentParser(description="Open up Serial Port and log communications")
parser.add_argument('-p', '--port', help='''The port, ie COMX, to open. 
                                            The fastest way to start the program.
                                            If left empty the program will scan the serial ports
                                            for a device that sends the String "Arduino"; this takes a  
                                            few seconds!''')
parser.add_argument('-i', '--id', help="""animal ID""")
parser.add_argument('-dp', '--dprime', action='store_true', help="""animal ID""")
parser.add_argument('-v', '--verbose', action='store_true', help="""prints debug info from arduino""")
parser.add_argument('-b', '--block', type=int, default = 20, help="Number of iterations to count d_prime")
p.add_argument('-f', '--frequencies' nargs="+", type=int, help="a list of integer frequencies to be sent to flutter controller")
                                            
args = parser.parse_args()


def random_block(frequency_block = ['0Hz', '5Hz', '10Hz', '25Hz', '50Hz', '100Hz']):
	
        return np.random.shuffle(block)
		









def get_data(table):
    df = pd.read_table(StringIO(table), sep = "\t", comment ="#")
    df = df[df['modeString'].contains("operant|conditioning", regex=True)]
    df = df.dropna(axis = 1)
    df = df.convert_objects(convert_numeric=True)
   
    return df

def timenow(): 
    return str(datetime.datetime.now().time().strftime('%H:%M:%S'))
    
def z_transform(x): 
    return norm.ppf(x)

def calc_dprime(pHit, pFAl):
    try: 
        d_prime = z_transform(pHit) - z_transform(pFAl)
        return d_prime
    
    except: 
        return "nan"

def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            
            s.timeout = 1
            s.open()
            time.sleep(1)
            line = s.readline()
            
            if  'Arduino' in line:
                result.append(port)
            
            s.close()
        except (OSError, serial.SerialException):
            pass
    return result
  
def timenow(): 
    return str(datetime.datetime.now().time().strftime('%H:%M:%S'))
  
def main(port, id = "-", do_dprime =False, verbose=False, block = 20):
    
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.timeout = 0.05
    ser.port = port
    ser.open()
    
    date = datetime.date.today().strftime('%y%m%d')
    DATADIR = os.path.join(os.getcwd(), date)

    if not os.path.isdir(DATADIR):
        os.mkdir((DATADIR))
    
    filename = "%s_%s_%s.log" %(port,id,date)
    outfile = os.path.join(DATADIR, filename)
    print outfile.replace("\\", "\\\\")

    table = ""
    with open(outfile, 'a') as f:
         
        f.write(timenow() + "opened port " + port + "\n")
        mode = ""
        
        #try:
        while True:
            print "\r", timenow(), "\r",

            if m.kbhit():
                c = m.getch()
                if c == '\xe0': c = m.getch()
                if c != '\x1b':
                    mode = raw_input("type command: ")
                    c = ''
                else: 
                    break
            else:
                line = ser.readline()
                
                if line.startswith("\t"):
                    line = "#%s\t%s\t%s\t%s" %(timenow(),port,id,line)
                    f.write(line)
                    if verbose: print colorama.Fore.CYAN + colorama.Style.NORMAL + line,
                    
                elif line:
                    colourline = ""
                    if do_dprime:
                        try:
                            table = table + line
                            if (len(df) > 0) and not (len(df)%block):
                                
                                df = get_data(table)
                                
                                N = len(df)
        
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

                                d_prime = calc_dprime(pHit, pFAl)
                                
                                colourline = line + colorama.Fore.GREEN + colorama.Style.BRIGHT + "\t%2.3f\t%2.3f\t%2.3f" %(pHit, pFAl, d_prime)
                                line = line + "\t%2.3f\t%2.3f\t%2.3f" %(pHit, pFAl, d_prime)
                                
                                table = ""
                                
                        except: 
                            print colorama.Fore.RED + colorama.Style.BRIGHT + "Can't do dprime calculation on this Serial Port"
                    
                    line = "%s\t%s\t%s\t%s" %(timenow(),port,id, line)
                    if colourline:
                        colourline = "%s\t%s\t%s\t%s" %(timenow(),port,id, colourline)
                    else: colourline = "%s\t%s\t%s\t%s" %(timenow(),port,id, line) 
                    
                    print colorama.Fore.YELLOW + colorama.Style.BRIGHT + colourline,
                    f.write(line)
                    
                
                elif mode: 
                    ser.write(mode)
                    f.write("#" + timenow()+"\t"+mode)
                    mode = ""

                print colorama.Style.RESET_ALL,
                
        
        #except:
        #    ser.close()
        #    print timenow() + "\tclosed port " + port
        #    f.write(timenow() + "\tclosed port " + port + "\n")
        
if __name__ == '__main__':
    
    port = args.port
    id = args.id
    do_dprime = args.dprime
    verbose = args.verbose
    block = args.block
    frequencies = args.frequencies
    if frequencies: block = len(frequencies) * 5 #set the block proportional to the number of frequencies to be tested
    
    os.system("cls")
    
    print id, do_dprime
    
    ser = serial.Serial()
    ser.baudrate = 9600
    
    if not port: 
        print "Available Arduino ports:"
        print(serial_ports()) 
    
    else:
        main(port, id, do_dprime, verbose, block)
        
"""

df.head = [modeString, trial_no, waterCount, trial_delay, istimeout, stimTrial, response, lickCount]

"""

