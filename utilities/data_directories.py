import os
import datetime

from colorama_wrapper import *

def timenow():
    """provides the current time string in the form `HH:MM:SS`"""
    return datetime.datetime.now().time().strftime('%H:%M:%S')      

def today():
    """provides today's date as a string in the form YYMMDD"""
    return datetime.date.today().strftime('%y%m%d')

def create_datapath(DATADIR = "", date = today()):
    """make a path to save the data based on today's date"""

    if not DATADIR: 
        DATADIR = os.path.join(os.getcwd(), date)
    else: 
        DATADIR = os.path.join(DATADIR, date)
    
    if not os.path.isdir(DATADIR):
        os.makedirs((DATADIR))
    
    print colour("datapath:\t", style = (sBRIGHT, fGREEN)),
    print colour(DATADIR, style = (sBRIGHT, fGREEN))
    
    return DATADIR        

def create_logfile(DATADIR = "", date = today(), port = None, ID = None):
    """make a logfile to save communications, based on today's date"""
    
    filename = "%s_%s_%s.log" %(port,ID,date)
    logfile = os.path.join(DATADIR, filename)
    print colour("Saving log in:\t", style = (sBRIGHT, fGREEN)),
    print colour("./$datapath$/%s" %filename, style = (sBRIGHT, fGREEN))
    
    return logfile
