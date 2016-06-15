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
                    'action' : 'store_false', 
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
    
    ('--t_stimDELAY',) : {
                    'default' : 150, 
                    'type' : int, 
                    'help' : 'sets the time between succesive stimuli'
    },
                    
    ('-rdel', '--t_rDELAY', ) : {
                    'default' : 100, 
                    'type' : int, 
                    'help' : 'set start time of reward epoch'
                    },
                    
    ('-rdur', '--t_rDUR', ) : {
                    'default' : 2000, 
                    'type' : int, 
                    'help' : 'set end time of reward epoch'
                    },
                    
    ('-to', '--timeout', ) : {
                    'default' : 1.5,
                    'type' : float,
                    'help' : 'set the timeout duration for incorrect licks'
                    },

    ('--freq', ) : {
                    'nargs' : '+', 
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
