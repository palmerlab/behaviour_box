"""
Configuration settings

TODO: make all editable in commandline options!
TODO: output these within logfile

"""

behaviourPORT = "COM5"
stimboxPORT = "COM4"

mode = 'c' # a char, either 'c' or 'o'

frequency_block = [0, 5, 10, 25, 50, 100]




'''

"lickThres"      // 5V / 1024
"trial_delay"    // ms
"t_noLickPer"    // ms
"t_stimONSET[0]" // ms
"t_stimONSET[1]" // ms
"stimDUR"        // ms
"t_rewardSTART"  // ms
"t_rewardEND"    // ms
"t_trialEND"     // ms
"waterVol"       // ms
                 // ms
"ON"             // ms
"OFF[0]"         // ms
"OFF[1]"         // ms


"mode"           // 'c' or 'o'
"rewardCond"     // 'L', 'R', 'B', 'N'
"verbose"        // true

'''


boxparams = {
    "trial_delay"   :   500,
    "t_noLickPer"   :     0,
    "t_stimONSET[0]":  4000,
    "t_stimONSET[1]":  5000,
    "stimDUR"       :   500,
    "t_rewardSTART" :  6000,
    "t_rewardEND"   :  9000,
    "t_trialEND"    : 10000,
    "lickThres"     :   450,
    "waterVol"      :    10,
    "ON"            :     1,
    "OFF[0]"        :     5,
    "OFF[1]"        :     5
    "mode"          : 'c',
    "rewardCond"    : 'B',
    "verbose"       : 1
}

if (boxparams['OFF[0]'] > boxparams['OFF[1]']):
    boxparams['rewardCond'] = 'L'

if (boxparams['OFF[1]'] > boxparams['OFF[0]']):
    boxparams['rewardCond'] = 'R'

if (boxparams['OFF[0]'] == 0) or (boxparams['OFF[1]'] == 0):
    boxparams['rewardCond'] = 'B'

if (boxparams['OFF[0]'] == 0) and (boxparams['OFF[1]'] == 0):
    boxparams['rewardCond'] = 'N'
