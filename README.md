# Behaviour_box

Sorry it's a mess,

I'm a Neuroscientist not a software engineer

This is code to run my experiments


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
