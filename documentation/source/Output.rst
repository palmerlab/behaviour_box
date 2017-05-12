##############
Output Format
##############

The following table shows the output generated from running SerialComms.py
with these parameters::

    >> SerialComms.py -i G3 -af -lt 1 -lc 2 -noise -nlp 1000 
    ..  -rdur 800 -rdel 50 --trials 0 25 50 100 150 200 -td 5 
    ..  -to 2 --ITI 2 8 

.. csv-table:: 
    :header-rows: 1
    :widths: auto
    
    ,ID,Water,audio,block,comment,lickThres,lickTrigReward,minlickCount,mode,post_count,pre_count,punish_tone,response,rew_count,reward_nogo,t_noLickPer,t_rewardDEL,t_rewardDUR,t_stimDUR,t_stimONSET,t_trialDUR,time,timeout,trialType,trial_noise,trial_num
    0,G3,0,1,0,,204,0,2,o,0,0,0,-,0,0,1000,50,800,25,2000,5000,18:29:43,2,G,TRUE,0
    1,G3,0,1,0,,204,0,2,o,0,0,0,R,0,0,1000,50,800,0,2000,5000,18:30:08,2,N,TRUE,1
    2,G3,1,1,0,,204,0,2,o,6,2,0,H,11,0,1000,50,800,50,2000,5000,18:30:19,2,G,TRUE,2
    3,G3,0,1,0,,204,0,2,o,,,0,e,,0,1000,50,800,,2000,5000,18:30:28,2,G,TRUE,3
    4,G3,1,1,0,,204,0,2,o,11,0,0,H,10,0,1000,50,800,200,2000,5000,18:30:38,2,G,TRUE,4
    5,G3,0,1,0,,204,0,2,o,,,0,e,,0,1000,50,800,,2000,5000,18:30:48,2,G,TRUE,5
    
The .csv file that gets generated contains a table of variables, that may be
relevant to analysis.

+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Variable         | value                                                                                                                                                                              |
+==================+====================================================================================================================================================================================+
| ID               | The identity string for this animal                                                                                                                                                |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Water            | Either 0 for no water delivered, or 1 to indicate water was given                                                                                                                  |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| audio            | Either 0 to indicate audio cues not used on this trial, or 1 to indicate the use of audio cues                                                                                     |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| block            |  An integer value that keeps track of which group of trials this trial is part of (increments by 1 after all of the iterable values are exhausted and the session gets repeated)   |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| comment          |  Space for trial relevant comments                                                                                                                                                 |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| lickThres        |  The internal value the Arduino uses as the lick threshold. Multiply by 5 / 1024 to get the threshold in volts                                                                     |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| lickTrigReward   | Either 0 indicating if the reward is delivered at the end of the response period, or 1 to indicate that the animal is rewarded immediately after licking.                          |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| minlickCount     |  The number of licks required on this trial in order to count as a response to the Arduino.                                                                                        |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| mode             |  Either ‘o’ for an operant trial or ‘h’ for a habituation trial                                                                                                                    |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| post\_count      |  The number of licks counted after the stimulus                                                                                                                                    |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| pre\_count       |  The number of licks counted in the period before the stimulus                                                                                                                     |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| punish\_tone     |  0 or 1 indicating if a tone is used to punish a false alarm                                                                                                                       |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| response         |  The character code of the animals response. One of {‘H’: hit, ‘f’: false alarm, ‘R’: correct rejection, ‘e’: early lick (trial broken), ‘-’: miss}.                               |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| rew\_count       |  Number of licks detected in the response period                                                                                                                                   |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t\_noLickPer     | This is the number of milliseconds before the stimulus in which licks would cause the trial to be cut short.                                                                       |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t\_rewardDEL     |  The amount of time delayed between the end of the stimulus and the onset of the response period.                                                                                  |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t\_rewardDUR     | The width of the response period in milliseconds.                                                                                                                                  |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t\_stimDUR       |  The duration in milliseconds that the stimulus was on for on this trial                                                                                                           |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t\_stimONSET     |  The time the stimulus came on, relative to the beginning of the trial, in milliseconds.                                                                                           |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t\_trialDUR      |  The duration of this trial in milliseconds.                                                                                                                                       |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| time             | Time on the PC that this trial began (in 24 hour format)                                                                                                                           |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| timeout          | The number of seconds specified for the timeout period                                                                                                                             |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| trialType        | The type of trial. Either ‘G’ for a go trial, or ‘N’ for a no-go trial                                                                                                             |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| trial\_noise     | A Boolean value indicating if the masking noise was played on this trial.                                                                                                          |
+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+



In this example the parameters specified yield the following trial conditions:

* ``-i G3`` (or ``--ID G3``): 
    specifies an identifier for this animal, 
    this identifier is then used in the filename of the generated output.
    ie: G3_YYMMDD.csv

* ``-af`` (or ``--audio``): 
    specify that audio cues are to be used in this trial.
    Lick events produce a brief click when detected and the reward period, 
    reward event, and punishment are all signalled by different tones.

*  ``-lt 1``:
    Sets the threshold of the lick detection to be 1 V. Rising edges exceeding
    the lick threshold value will be counted as lick events.

* ``-lc 2``:
    Specifies the number of licks that are required in order for the Arduino to
    count a response. At least this number of licks are required in the response
    period in order to trigger a reward or a punishment. In addition, this
    is the number of licks necessary to break a trial before the stimulus is 
    delivered.

* ``-noise``:
    Specifies that a masking noise should be played from the PC speakers. This
    noise plays during the trial in order to simulate the sounds of the laser 
    scanning mirrors on non-imaging trials.

* ``-nlp 1000``:
    Specifies the no lick period in milliseconds. This is the number of 
    milliseconds before the stimulus in which licks will cause the trial to be
    cut short.
    
*  ``-rdur 800``:
    Specifies the time in milliseconds to listen for licks after the stimulus.
    That is, the width of the response period in milliseconds.

*  ``-rdel 50``:
    Specifies the time to wait after the end of the stimulus before the response
    period becomes active. Also in milliseconds.

* ``--trials 0 25 50 100 150 200``:
    Specifies 6 durations for the stimulus. The program will shuffle through
    this list for a set number of repeats 
    (by default 500, see :ref:`adjust-defaults`)

* ``-td 5`` :
    Specifies that the trial has a duration of 5 seconds. The recording trigger
    will remain in the ``HIGH`` voltage state for this duration, unless a trial
    is interrupted by early licking.

* ``-to 2``:
    Specifies a timeout of 2 seconds. In the event that the animal responds to
    the no-go trial this is the amount of time they must withhold additional 
    licks for the next inter-trial interval to begin. Additional licks within 
    this period will reset the time out.

* ``--ITI 2 8``:
    Specifies an inter-trial interval of between 2 and 8 seconds. The exact time
    to wait between any particular two trials is random, between theses two
    bounds.
