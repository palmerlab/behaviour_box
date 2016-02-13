import argparse

p = argparse.ArgumentParser(description="This program controls the Arduino " 
                                           "and reads from it too"
                                            )

p.add_argument("-i", "--ID", 
                default = "", 
                help = "identifier for this animal/run",
                )

p.add_argument("-w", "--weight", 
                default = 0, 
                help = "weight of the animal in grams",
                )

p.add_argument("-m", 
                "--mode", 
                default = "o", 
                help = "the mode `h`abituaton or `o`perant, "
                        "by default will look in the config table",
                )
                
p.add_argument("-r", 
                "--rewardCond", 
                default = '-', 
                help = "can be 'L'eft or 'R'ight; a random condition "
                        "is selected if left empty."
                        " this value sets the port that will be rewarded",
                )                
                
p.add_argument('--repeats', 
                default = 10, 
                type = int, 
                help = "the number of times this block should repeat, " 
                        "by default this is 1",
                )
                
p.add_argument('-p', '--punish', 
                action = 'store_true', 
                help = "sets `break_wrongChoice` to True, " 
                        "incorrect licks will end an operant "
                        "trial early",
                )

p.add_argument("-N", '--trial_num', 
                default = 0, 
                type = int, 
                help = 'trial number to start at',
                )

p.add_argument('--datapath', 
                default = "C:/DATA/Andrew/wavesurfer", 
                help = "path to save data to, " 
                        "by default is "
                        "'C:/DATA/Andrew/wavesurfer/%%YY%%MM%%DD'",
                )
                
p.add_argument("--port", 
                default = "COM5", 
                help = "port that the Arduino is connected to",
                )
                
p.add_argument("--verbose", 
                action = 'store_true', 
                help = "for debug this will print everything if enabled",
                )

p.add_argument('-lt', '--lickThres', 
                default = 0.75, 
                type = int, 
                help = 'set `lickThres` in arduino',
                )
                
p.add_argument('-lc', '--lcount', 
                default = 2, 
                type = int, 
                help = 'set `minlickCount` in arduino'
                )


p.add_argument('--ITI', 
                nargs = 2, 
                default = [2,5], 
                type = float, 
                help = "an interval for randomising between trials",
                )

args = p.parse_args()
