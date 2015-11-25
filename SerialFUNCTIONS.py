"""

Helper functions for `SerialControl.py`

"""

def random_block(frequency_block = ['0Hz', '5Hz', '10Hz', '25Hz', '50Hz', '100Hz']):
	
        return np.random.shuffle(block)

        
def print_GREEN(x):
    print colorama.FORE.GREEN, x, colorama.Style.RESET_ALL
    return x       
        
def print_YELLOW(x):
    print colorama.FORE.YELLOW, x, colorama.Style.RESET_ALL
    return x
        
def print_CYAN(x, v = False):
    if v: print colorama.FORE.CYAN, x, colorama.Style.RESET_ALL
    return x
        
def print_RED(x):
    print colorama.FORE.RED, x, colorama.Style.RESET_ALL
    return "warning:\t%s" %x
    

def buffer_data()
    """
    Check if there is data available
    read n bytes equivilent to char int char
    first cahr says which port; the in is the time in
    ms since the trial was triggered; The last char is a
    terminator
    """
    
def behaviour_log(logfile):


    while m.kbhit()==False:
        print timenow(), "\r",
        
        
        inline = behaviourCOMS.readline()
        
        if inline:
            if inline.startswith("#"):
                logfile.write(print_CYAN(inline, verbose))
            else:
            
                logfile.write(print_YELLOW(inline))
                
                behaviourDF = pd.read_table(StringIO(table), 
                    sep = "\t").convert_objects(convert_numeric=True)

    return pass
    
def check_input():
    
    if m.kbhit():
        c = m.getch()
        if c == '\xe0': c = m.getch()
        
        if c = '\x1b':
            sys.exit(0)
        
        else:    
            mode = raw_input("type command: ")
            c = ''
            return mode
    else:
        return False

def create_logfile(DATADIR = ""):
    
    date = datetime.date.today().strftime('%y%m%d')
    
    if not DATADIR: DATADIR = os.path.join(os.getcwd(), date)
    
    if not os.path.isdir(DATADIR):
        os.mkdir((DATADIR))
    
    filename = "%s_%s_%s.log" %(port,id,date)
    logfile = os.path.join(DATADIR, filename)
    print logfile.replace("\\", "\\\\")
    
    return logfile

def timenow(): 
    return str(datetime.datetime.now().time().strftime('%H:%M:%S'))
    
def get_data(table):
    df = pd.read_table(StringIO(table), sep = "\t", comment ="#")
    df = df[df['modeString'].contains("operant|conditioning", regex=True)]
    df = df.dropna(axis = 1)
    df = df.convert_objects(convert_numeric=True)
    return df

def z_transform(x): 
    return norm.ppf(x)

def calc_dprime(df):

    N = len(df)
    if N < 0:
        print colorama.Fore.RED + colorama.Style.BRIGHT + "DF too small for d prime"
        return "nan", "nan", "nan"
        
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

    try: 
        d_prime = z_transform(pHit) - z_transform(pFAl)
        return pHit, pFAl, d_prime
    
    except: 
        return "nan", "nan", "nan"

def get_info(port, lines = 1):
    
    info = ""
    for l in xrange(lines):

        inline = port.readline()

        if inline.startswith("#"):
            info = info + "#%s\t%s\t%s" %(timenow(), port, id, inline)
        else: 
            inline = "%s\t%s\t%s" %(timenow(), port, id, inline)
            print colorama.Fore.YELLOW, inline
            info = info + inline
            
        if (l == lines) and (port.inWaiting()):
            info = info + get_info(port, 1)
    
    if verbose: print verbose, info
    
    return info
