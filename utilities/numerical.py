
def num(s):
    """ 
    First attempts to convert string s to an integer. 
    If that gives a ValueError then it attempts to return s 
    as a float. Finally if s cannot be converted to a float or 
    an int, the string is returned unchanged.
    """
    try:
        return int(s)
    except ValueError:
        try: 
            return float(s)
        except ValueError:
            return s
            
def na_printr(s):
    "prints nans as strings if necessary"
    try: return "%3d" %s
    except: return "%03s" %s

    
import csv

def unpack_table(filename):
    """
    Reads a transposed csv, 
    Where the first column contains the header
    """
    
    reader = csv.reader(open(filename, 'r'), delimiter = "\t")
    d = {}
    for row in reader:
       k, v = row
       d[k] = v
    
    return d
