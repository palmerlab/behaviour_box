Andrew's Behaviour Box
=======================

This is the collection of files I use to run my behavioural experiments.
It runs a routine described by the following diagram

![Flow of the behavioural paradigm](.\Flow_diagram.svg)

Recent Update:

Adds auditory option and allows the frequencies / off times to be controlled online



# SerialController.py


1. The program starts
2. The program opens communications with available serial port
    The program waits until it gets the arduino is active, and prints all output
    until the ready signal is transmitted. Which is `-- Status: Ready --`
    
3. The program starts a block
5. The program transmits the dict `params`, which holds all parameters 
    for a single trial. The condition values get updated; based on the
    frequencies being sent, all contents of `params` are transmitted to
    the behaviour controller.
    
6. The program prints the frequencies and the condition to the screen and a
   random timeout is started.
6. The program initiates a trial by sending a literal `"GO"` to the 
   behaviour box.
   - The behaviour box runs one trial, with the parameters set previously

7. The program records the output from behaviorCOMs into a
   dict, which later will be converted to a data frame for analysis.

8. The program repeats sending mode flags until all stimuli combinations have
   been run through.



# Behaviour_box.ino

This program delivers sensory stimulation and opens water 
valve when the animal touches the licking sensor within a 
certain time window.

Setup connections:
------------------

|  DIGITAL  | output            | variable        |
| --------- | ----------------- | --------------- |
| pin 2     | recording trigger | `recTrig`       |
| pin 3     | stimulus          | `stimulusPin`   |
| pin 8     | speaker           | `speakerPin`    |
| pin 10    | left water valve  | `waterValve[0]` |
| pin 11    | right water valve | `waterValve[1]` |
| --------- | ----------------- | --------------- |

| ANALOG    | input             |                 |
| --------- | ----------------- | --------------- |
| A0        | left  lick sensor | `lickSens[0]`   |
| A1        | right lick sensor | `lickSens[1]`   |
| --------- | ----------------- | --------------- |

Table: connections to lick controller
  
Start program:
--------------


The arduino program is a little complicated; but in principle a simple
setup. The main method is `runTrial` which on initialisation:

1. Waits a period of ms defined by `trial_delay`. In this period the timer counts
   up to zero; and the sensors detect licks. 10 ms before zero, a pulse is sent to
   the `recTrig` to trigger the recording
2. Next two periods of `ActiveDelay` are intialised in sequence. Two are used 
   so that if I decide the set a `noLickPer` time, I can have that come on a
   short time after the trigger. `ActiveDelay` has the condition `break_on_lick`
   as it's second argument. If `true` the program will exit the function before
   it reaches the time that it is set to delay until.
3. Two stimuli are delivered, separated by an `ActiveDelay` method.
4. After another `ActiveDelay` the program enters the `TrialReward` period, if
   `rewardCond` is not `'N'`, which stands for neither port giving water. During
   the `TrialReward` phase, if the `mode` is `c` then water is dispensed 
   immediately from the associated port.
5. The program delays again, and then exits the `runTrial` function. Resulting in
   the program sending the ready string to the Serial controller.

Now also includes a mode switch. Using `<tab>` you can switch between
operant and habituation modes. In habituation the animal is delivered
a pair of randomly selected stimuli, which match the reward condition
when it licks the water ports. Following the stimulus delivery a reward
is dispensed on the port that the animal licked. 
In this mode an  upper limit on the number of contiguous successful
trials on the same side is used (Thanks @Conrad Lee). A counter
keeps track of the number of licks, and if the counter reaches 10
the associated port becomes inactive. Licking the other port subtracts
1 from the counter. In this way the animal must balance it's attention on
both ports.
   
In addition to the basic functionality the program also features modules that
do the following:

`t_now(t_init)`
: Returns the number of milliseconds since `t_init`. `t_init` is a global
    unsigned long. It takes the value of `millis()` at the start of a run;
    which in turn is the number of milliseconds since the Arduino was turned on.
  
`senseLickChange(bool sensor)`  
: `sensor`
    is a Boolean, because I only have implemented two lick sensors, which can
    be 0 or 1, for the left and right sensors respectively. This function
    reads the value of the analog input defined by `lickSens[sensor]`. If this
    is greater than the threshold the function returns true, and sets the
    `lickRep[sensor]` pin to ON.
  
    In addition this function includes a line to set the speaker to be ON or OFF
    at random. This is how the auditory masking noise is produced. 
    A consequence of this is that each state the controller gets in has
    a different timbre. The obvious solution is to use a PC speaker to go to
    `youtube>10 hours of white noise` instead of this tangled solution!
    
`getSerialInput()`
: Returns data from the serial port as a string. `while Serial.available()`

`getSepIndex(string, sep)`
: Returns the first index at which the character `sep` is found in `string`.
    If no separator is present this function will return 0. 
    
    (Possible source of bugs, it would be better to uses -1 and to check that
    the output is valid on call!)

`flutter(off)`
: This function runs single square pulse on `stim_pin` which is high
    for the duration `on`, defined in microseconds. The `off` value gives
    a delay in which the pin is in low state such that by stringing multiple 
    of these together I can generate a square wave.
    
`ActiveDelay(wait, break_on_lick = false, verbose = true)`
: Returns true if a lick is detected in the period defined by `wait`. `wait` is
    some time relative to the time that the trial started (`t_init`).
    
    if `break_on_lick` is set true, this function will return before the end 
    of the delay period.
    
    TODO: It would be best to make the return value depend on whether or not
    an early break has happened!

`preTrial(verbose = true)`
: While the trial has not started 
    1. update the time
    2. check for licks
    4. trigger the recording by putting recTrig -> HIGH
    5. flash the LED each second.

`UpdateGlobals(input)`
: This function parses an `input` string and uses it to set the value
   of global paramaters. If the input is of the form `variablename : value`
   `variablename` will be updated to be equal to `value`


`TrialReward()`
: This function returns a character corresponding to the lick status
    
    - 'L'
    : correct hit on left port              
                                               
    - 'R'
    : correct hit on right port             
                                               
    - 'l'
    : incorrect lick on left port           
                                               
    - 'r' 
    : incorrect lick on right port          
                                               
    - '-' 
    : unknown; in conditioning this         
         function exits before the animal has  
         a chance to respond                   
                                               
    - 'M'
    : No lick detected during reward period 

    
    
