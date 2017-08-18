import argparse

p = argparse.ArgumentParser(description="This program controls the Arduino "
                                           "and reads from it too"
                                            )

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
                    'default' : 1000,
                    'type' : int,
                    'help' : 'set `t_noLickPer` in arduino'
                    },

    ('-td', '--trialDur', ) : {
                    'default' : 10,
                    'type' : float,
                    'help' : 'set minimum trial duration in seconds'
                    },

    ('--t_stimONSET',) : {
                    'default' : 4000,
                    'type' : int,
                    'help' : 'sets the time after trigger to run the first stimulus'
                    },

    ('-rdel', '--t_rDELAY', ) : {
                    'default' : 0,
                    'type' : int,
                    'help' : 'set start time of reward epoch in ms'
                    },

    ('-rdur', '--t_rDUR', ) : {
                    'default' : 1500,
                    'type' : int,
                    'help' : 'set duration time of response epoch in ms'
                    },

    ('-to', '--timeout', ) : {
                    'default' :0,
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
                    'default' : [3,5],
                    'type' : float,
                    'help' : "an interval for randomising between trials",
                    },

    ('--trials', ) : {
                    'nargs' : '*',
                    'default' : ['G','N'],
                    'type' : str,
                    'help' : "list of types of trial in the form N or G",
                    },

    ('-ratio', ) : {
                    'nargs' : 3,
                    'default' : [1,1,0],
                    'type' : int,
                    'help' : "number of go, nogo, and blank trials respectively",
                    },
    ('-restore', ) : {
                     'action': 'store_true',
                     'help' : "Use to look up previous settings in the comms.ini file",
                    },

    ("-N", '--trial_num', ) : {
                    'default' : 0,
                    'type' : int,
                    'help' : 'trial number to start at',
                    },

    ('--datapath', ) : {
                    'default' : r"R:\Dani\test_behavior_box",
                    'help' : "path to save data to, "
                            "by default is "
                            r"R:\Dani\test_behavior_box\%%YY%%MM%%DD",
                    },
    ('-af', '--audio') :{
                    'action' : 'store_true',
                    'help' : "provides audio feedback during the trials"
                               " this is not to be confused with the noise"
                               " played to simulate / mask the scanners"
                    },

    ("--port", ) : {
                    'default' : "COM5",
                    'help' : "port that the Arduino is connected to",
                    },
}

for k, v in kwargs.iteritems():
    p.add_argument(*k, **v)

args = p.parse_args()
