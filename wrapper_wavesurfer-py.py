from __future__ import division
import os
import datetime
import h5py #stfio will fuck shit up if it is loaded before h5py
import stfio
import numpy as np
import matplotlib.pyplot as plt
import argparse


def convert_ws_to_stfio(infile, outfile, outpath):

    print outpath
    if not outfile:
        outfile = os.path.split(infile)[1]
        outfile = outfile.split(".")[0] #remove fie ext
        outfile = "stimfit_%s.h5" %outfile
        
    if not outpath:
        outpath = os.path.split(infile)[0]
        outpath = os.path.join(outpath, "ANALYSIS")
    
    if not os.path.isdir(outpath):
        print outpath
        os.makedirs(outpath)
                
    
    f = h5py.File(infile, 'r')

    analogDATA = [] #tmp list to hold the analog data

    for group in f:
        if group != u'header':
            analogDATA.append(f['%s/analogScans' %group].value.astype('float'))

    analogDATA = np.array(analogDATA)
    analogDATA = (analogDATA * (20 / 2**16))
    
    channels = analogDATA.shape[1]
    traces = analogDATA.shape[0]

    unitslist = f['header/Acquisition/AnalogChannelUnits'].value
    nameslist = f['header/Acquisition/ChannelNames'].value

    chlist = []
    for c in xrange(0, channels):

        seclist = []

        for t in xrange(0,traces):
            seclist.append(stfio.Section(analogDATA[t][c]))
        
        chlist.append(stfio.Channel(seclist))
        chlist[c].yunits = unitslist[c]
        chlist[c].name = nameslist[c]


    rec = stfio.Recording(chlist)
    rec.comment = "converted from file"


    #todo: convert datestamp from array in fmt[YYYY, MM, DD, HH, MM, SS]
    dstamp = f['header/ClockAtExperimentStart'].value
    #print dstamp
    
    #to tidy: dstamp is a 2d array when it really is just a 1d array
    rec.date = "%d-%d-%d" %(dstamp[0][0],dstamp[1][0],dstamp[2][0])
    rec.time= "%d-%d-%d" %(dstamp[3][0], dstamp[4][0], dstamp[5][0]) 
    #print rec.time
    #print rec.date
    #datetime.time()
    
    rec.comment = "converted from %s" %file
    rec.dt = (1000 / int(f['header/Acquisition/SampleRate'].value))
    rec.xunits = 'ms'

    rec.write(os.path.join(outpath,outfile))    
    #f.close()

parser = argparse.ArgumentParser(description="Open up Serial Port and log communications")
parser.add_argument("file", help="file to convert")
parser.add_argument("-o", "--outfile", default = "", help="name of output file. infile.h5 by default")
parser.add_argument("-p", "--outpath", default = "", help="output path; is generated if not exists")

args = parser.parse_args()

if __name__ == '__main__':
    infile = args.file
    outfile = args.outfile.replace("\\", "\\\\")
    outpath = args.outpath.replace("\\", "\\\\")
    
    convert_ws_to_stfio(infile, outfile, outpath)
    
    
    
    
    
    
    
###   >>> print(rec.comment)
###   Created with Clampex
###   >>> print(rec.date)
###   2008/1/18
###   >>> print(rec.dt) # sampling interval
###   0.1
###   >>> print(rec.file_description) # no file description in this case
###   
###   >>> print(rec.time)
###   15:08:20
###   >>> print(rec.xunits)
###   ms
###   """
###   A Rcording consists of one or more Channels, which in turn are composed of 
###   one or more Sections. They can be accessed using indexing operators ([]).
###   """
###   >>> len(rec) # Recording consists of 2 Channels
###   2
###   >>> len(rec[0]) # First Channel consists of 13 Sections
###   13
###   >>> len(rec[0][0]) # First Section in first channel contains 146450 data points
###   146450
###   >>> print(rec[0].name) # channel name
###   Current
###   >>> print(rec[1].name)
###   IN 3
###   >>> print(rec[0].yunits) # channel units
###   pA
###   >>> print(rec[1].yunits)
###   C
###   """
###   The time series in a Section can be accessed as a NumPy array:
###   """
###   
###   >>> arr = rec[0][0].asarray()
###   >>> type(arr)
###   <type 'numpy.ndarray'>
###   >>> arr.shape
###   (146450,)
###   """
###   Note that the Section itself is not a NumPy array and therefore needs to be converted as described above before you can do fancy arithmetics:
###   """
###   >>> type(rec[0][0])
###   <class 'stfio.Section'>
###   >>> res = rec[0][0].asarray() + 2.0