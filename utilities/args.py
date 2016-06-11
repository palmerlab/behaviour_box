import argparse

p = argparse.ArgumentParser(description="This program controls the Arduino " 
                                           "and reads from it too"
                                            )

kwargs = {
    ("-i", "--ID", ) : {
                    'default' : "", 
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
                    'default' : 10, 
                    'type' : int, 
                    'help' : "the number of times this block should repeat, " 
                            "by default this is 1",
                    },
                    
    ('-p', '--punish', ) : {
                    'action' : 'store_true', 
                    'help' : "sets `break_wrongChoice` to True, " 
                            "incorrect licks will end an operant "
                            "trial early",
                    },
    ("--verbose", ) : {
                    'action' : 'store_true', 
                    'help' : "for debug this will print everything if enabled",
                    },

    ("-a", "--auditory", ) : {
                    'action' : 'store_true', 
                    'help' : "switch to auditory stimulus instead of somatosensory",
                    },

    ("-bc", "--bias_correct", ) : {
                    'action' : 'store_true', 
                    'help' : "turn on the bias correction for the random number generator",
                    },
                    
    ("-b", "--blanks", ) : {
                    'action' : 'store_true', 
                    'help' : "include no stim trials",
                    },
                    
    ("-rs", "--right_same", ) : {
                    'action' : 'store_true', 
                    'help' : "define the right port as correct for same stimulus",
                    },
                    
    ("-s", "--single", ) : {
                    'action' : 'store_true', 
                    'help' : "use this flag for a single stimulus only",
                    },

                    
    ('-lt', '--lickThres', ) : {
                    'default' : 0.75, 
                    'type' : float, 
                    'help' : 'set `lickThres` in arduino',
                    },
                    
    ('-lc', '--lcount', ) : {
                    'default' : 2, 
                    'type' : int, 
                    'help' : 'set `minlickCount` in arduino'
                    },

    ('-nlp', '--noLick', ) : {
                    'default' : 1000, 
                    'type' : int, 
                    'help' : 'set `t_noLickPer` in arduino'
                    },
                    
    ('-td', '--trialDur', ) : {
                    'default' : 0,
                    'type' : float,
                    'help' : 'set minimum trial duration'
                    },
                    
    ('-rd', '--t_rewardSTART', ) : {
                    'default' : 3000, 
                    'type' : int, 
                    'help' : 'set start time of reward epoch'
                    },
                    
    ('-rend', '--t_rewardEND', ) : {
                    'default' : 4000, 
                    'type' : int, 
                    'help' : 'set end time of reward epoch'
                    },
                    
    ('-to', '--timeout', ) : {
                    'default' : 1.5,
                    'type' : float,
                    'help' : 'set the timeout duration for incorrect licks'
                    },

    ('--freq', ) : {
                    'nargs' : 2, 
                    'default' : [0,200], 
                    'type' : int, 
                    'help' : "Frequencies or OFF time values to be passed to "
                            "arduino as off_short and off_long",
                    },

    ('--dur', ) : {
                    'nargs' : 2, 
                    'default' : [100,500], 
                    'type' : int, 
                    'help' : "Durations or to be passed to "
                            "arduino as DUR_short and DUR_long",
                    },

    ('--ITI', ) : {
                    'nargs' : 2, 
                    'default' : [1,3], 
                    'type' : float, 
                    'help' : "an interval for randomising between trials",
                    },
                    


    ("-N", '--trial_num', ) : {
                    'default' : 0, 
                    'type' : int, 
                    'help' : 'trial number to start at',
                    },

    ('--datapath', ) : {
                    'default' : "C:/DATA/Andrew/wavesurfer", 
                    'help' : "path to save data to, " 
                            "by default is "
                            "'C:/DATA/Andrew/wavesurfer/%%YY%%MM%%DD'",
                    },
                    
    ("--port", ) : {
                    'default' : "COM5", 
                    'help' : "port that the Arduino is connected to",
                    },
}


for k, v in kwargs.iteritems():
    p.add_argument(*k, **v)


lickside = p.add_mutually_exclusive_group()
lickside.add_argument("-L", "--left", 
                action = 'store_true',
                )
                
lickside.add_argument("-R", "--right", 
                action = 'store_true',
                )

args = p.parse_args()
