"""
Configuration settings

TODO: make all editable in commandline options!
TODO: output these within logfile

"""

behaviourPORT = "COM5"
stimboxPORT = "COM4"

mode = 'c' # a char, either 'c' or 'o'

frequency_block = [0, 5, 10, 25, 50, 100]


boxparams = {
    trial_delay	  500
	t_noLickPer	  0
	t_stimONSET[0]	 4000
	t_stimONSET[1]	 5000
	stimDUR	  500
	t_rewardSTART	  6000
	t_rewardEND	  9000
	t_trialEND	  10000
	lickThres	  450
	waterVol	  10
	ON	  1
	OFF[0]	  5
	OFF[1]	  5
	mode	  'c'
	rewardCond	  ''
}
