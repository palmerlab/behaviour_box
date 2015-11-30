"""

Helper functions for `SerialControl.py`

"""

def z_transform(x): 
    return norm.ppf(x)

def dprime(response, stimulus):
    """
    
    takes a binary response array and a matching binary
    stimulus array and returns a dictionary containing
    
    p(hit|stimulus), p(hit|no stimulus), and d`
    
    """

    return_dict = {'pHit':0, 'pFAl':0, 'd_prime':0}
    
    df = pd.DataFrame({'response' : response, 'stimulus' : stimulus})

    N_tot = len(df)
    N_stim_false = len(df[df.stimTrial == 0])
    N_stim_true = len(df[df.stimTrial == 1])
    
    if N < 0:
        print colorama.Fore.RED + colorama.Style.BRIGHT + "DF too small for d prime"
        return "nan", "nan", "nan"
    
    # len(df) returns length of the dataframe index,
    # this calculates the number of hits, misses, true_negs, and true_pos
    hits = len(df[df.response == 1][df.stimTrial == 1]) 
    miss = len(df[df.response == 0][df.stimTrial == 1])
    true_neg = len(df[df.response == 0][df.stimTrial == 0]) 
    false_pos = len(df[df.response == 1][df.stimTrial == 0])
    
    #determine the probabilities of hits and false alarms
    try: pHit = (hits / N_stim_false) #P('response'| stimulus present)
    except: pHit = 1/(2*N)
    try: pFAl = (false_pos / N_stim_false) #P('response'| stimulus present)
    except: pFAl = 1/(2*N)
    
    if (pHit == 0): pHit =  1 - 1/(2*N)
    if (pFAl == 0): pFAl =  1 - 1/(2*N)
    if (pHit == 1): pHit =  1/(2*N)
    if (pFAl == 1): pFAl =  1/(2*N)      

    try: d_prime = z_transform(pHit) - z_transform(pFAl)
    except: d_prime = 'nan' 
        
    return {
            'pHit': pHit, 
            'pFAl': pFAl, 
            'd_prime': d_prime
            'hits': hits,
            'miss': miss,
            'true_neg': true_neg,
            'false_pos': false_pos
            'N': N_tot,
            'n_stim_true': N_stim_true,
            'n_stim_false': N_stim_false
            }
    