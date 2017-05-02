import argparse

# create the argument parsing object
p = argparse.ArgumentParser(description="This program controls the Arduino " 
                                           "and reads from it too"
                                            )

# construct a dictionary of program parameters
kwargs = {
    ("-i", "--ID", ) : {
                    'default' : "_", 
                    'help' : "identifier for this animal/run",
                    },

    ("-w", "--weight", ) : {
                    'default' : 0, 
                    'help' : "weight of the animal in grams",
                    },

    ("-m", "--mode",) : { 
                    'default' : "o", 
                    'help' : "the mode `h`abituaton or `o`perant, "
                            "by default will look in the config table",
                    },          
                    
    ('--repeats', ) : {
                    'default' : 500, 
                    'type' : int, 
                    'help' : "the number of times this block should repeat, " 
                            "by default this is 1",
                    },
                    
    ('-p', '--punish', ) : {
                    'action' : 'store_false', 
                    'help' : "sets `break_wrongChoice` to True, " 
                            "incorrect licks will end an operant "
                            "trial early",
                    },

    ("--verbose", ) : {
                    'action' : 'store_true', 
                    'help' : "for debug this will print everything if enabled",
                    },

    ('-lt', '--lickThres', ) : {
                    'default' : 2, 
                    'type' : float, 
                    'help' : 'set `lickThres` in arduino',
                    },
                    
    ('-lc', '--lcount', ) : {
                    'default' : 2, 
                    'type' : int, 
                    'help' : 'set `minlickCount` in arduino'
                    },

    ('-nlp', '--noLick', ) : {
                    'default' : 1500, 
                    'type' : int, 
                    'help' : 'set `t_noLickPer` in arduino'
                    },

    ('-td', '--trialDur', ) : {
                    'default' : 0,
                    'type' : float,
                    'help' : 'set minimum trial duration'
                    },
                    
    ('--t_stimONSET',) : {
                    'default' : 2000, 
                    'type' : int, 
                    'help' : 'sets the time after trigger to run the first stimulus'
                    },

    ('-rdel', '--t_rDELAY', ) : {
                    'default' : 50, 
                    'type' : int, 
                    'help' : 'set start time of reward epoch'
                    },
                    
    ('-rdur', '--t_rDUR', ) : {
                    'default' : 800, 
                    'type' : int, 
                    'help' : 'set end time of reward epoch'
                    },
                    
    ('-to', '--timeout', ) : {
                    'default' : 2.5,
                    'type' : float,
                    'help' : 'set the timeout duration for incorrect licks'
                    },
                    
    ('-ltr', '--lickTrigReward', ) : {
                    'action' : 'store_true', 
                    'help' : 'flag to allow licks to trigger the reward immediatly'
                    },
                    
    ('-rng', '--reward_nogo', ) : {
                    'action' : 'store_true', 
                    'help' : 'flag to allow a water delivery following no lick of a no go stim'
                    },
  
    ('-noise', ) : {
                    'action' : 'store_true', 
                    'help' : 'plays a noise during trials'
                    },

    ('--ITI', ) : {
                    'nargs' : 2, 
                    'default' : [5,8], 
                    'type' : float, 
                    'help' : "an interval for randomising between trials",
                    },    
                    
    ('--trials', ) : {
                    'nargs' : '*', 
                    'default' : [200,0], 
                    'type' : int, 
                    'help' : "durations to run on each trial",
                    },

    ('-restore', ) : {
                     'action': 'store_true',
                     'help' : "Use to look up previous settings in the comms.ini file",
                    },

    ('--datapath', ) : {
                    'default' : r"datapath", 
                    'help' : "path to save data to, " 
                            "by default it is the current directory + 'datapath'",
                    },
  
    ('-af', '--audio') :{
                    'action' : 'store_true',
                    'help' : "provides audio feedback during the trials"
                               " this is not to be confused with the noise"
                               " played to simulate / mask the scanners"
                    },
                    
    ("--port", ) : {
                    'default' : None,
                    'type' : str,
                    'help' : "port that the Arduino is connected to",
                    },
}

# load the argument parser with the parameters specified
for k, v in kwargs.iteritems():
    p.add_argument(*k, **v)

# read the command line arguments
args = p.parse_args()
