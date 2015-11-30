Sorry it's a mess,

I'm a Neuroscientist not a software engineer

This is code to run my experiments


#SerialController.py

1. The program starts
2. The program reads `config.tab` and `Frequencies.tab`,
    
    `config.tab` contains the details for a single run, 
    each line in the format `variablename : value`
    
    `Frequencies.tab` contains the block of frequencies that will be shuffled, in Hz. 
    The first line is a header with the title `frequency`, that gets ignored
    
2. The program opens communications with available serial port
    The program waits until it gets the arduino is active, and prints all output
    until the ready signal is transmitted. Which, because I played too much 
    command and conquer as a kid is `--Welcome Back Commander`
    
3. The program starts a block
4. The program shuffles the stimuli (frequencies list)

5. The program transmits the frequencies to the behaviour box,
    The dict `params` holds all parameters for a single trial (from `config.tab`)
    The condition values get updated; based on the frequencies being sent,
    all contents of `params` are transmitted to the behaviour controller.
    
6. The program prints the frequencies and the condition to the screen and a
   random timeout is started.
6. The program initiates a trial by sending a literal `"GO"` to the 
   behaviour box.
   - The behaviour box runs one trial, with the parameters set previously

7. The program records the output from behaviorCOMs into a
   dict, which later will be converted to a data frame for analysis.

8. The program repeats sending mode flags until all stimuli combinations have
   been run through.
   
TODO:

9. The program calculates d\`|any_stimuls; d\`|rising; d\`|falling







# Behaviour_box.ino

This program delivers sensory stimulation and opens water 
valve when the animal touches the licking sensor within a 
certain time window.

Setup connections:
------------------
  
--------- ----------------- ------------  
DIGITAL   output            variable
--------- ----------------- ------------
pin 2     recording trigger `recTrig`  
pin 4     stimulus TTL      `whiskStim`
pin 6     speaker for cues  `tonePin`
pin 8     syringe pump TTL  `waterValve`
pin 9     vacuum tube valve `vacValve`
pin 13    lick report       `licking`
--------- ----------------- ------------

ANALOG IN   input
---------   -----------------  ------------
A0          piezo lick sensor  lickSens
---------   -----------------  ------------
Table: connections to lick controller
  
Start program:
--------------
Trial intervals will randomized between 'minITI' and 'maxITI'. 
During a trial, the animal has to wait a stimulation without 
licking (no-lick period, 'nolickPer').
If it licks during no-lick period, the time of stimulation 
will be postponed by giving a time out (randomized between 
'minTimeOut' and 'maxTimeOut').
When a stimulation is delivered (stimulus duration: 'stimDur'), 
the animal need to respond (touch the sensor) within a certain 
time window ('crPer') to get a water reward.
Delayed licking after the time window will not be rewarded. 
Opening duration of the water valve is defined by 'valveDur'.
A TTL trigger for recording will be delivered 
'baseLineTime' (1 s in default setting) before the stimulus.