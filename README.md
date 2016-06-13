---
link-citations: true
---

Andrew's Behaviour Box
=======================

Version 2.0 Duration Discrimination
-----------------------------------


This is the collection of files I use to run my behavioural experiments.
Due to continued poor performance I have updated the system to now implement
a stimulus duration discrimination task. As before the animal is to report
if the stimulus is the same or different. The key difference to the
previous version is that the stimulus intensity is locked to it's highest
value and the animal simply needs to tell me the difference in the durations.


It runs a routine described by the following diagram

Operant Mode
------------

![Flow of the behavioural paradigm](./documentation/Flow_diagram.svg)


The operant mode features the following conditions:

1. Randomised selection of left or right trials
    - If a run of three trials of the same type are detected the
        program forces the next trial to be of the other type:
        ie: 'Left - Left - Left - Left' will be replaced by
        'Left - Left - Left - Right' before the fourth trial
        runs. This is in line with @guo_procedures_2014

        This logic is over written if the bias correction is in
        place.
        
    - In addition to the bias correction weighting, another bias
        correction mechanism prevents the animal from having a
        straight run of successes on one side. If 5 rewards are delivered
        on one side, without any delivered on the other side, the system
        will lock off that side. The associated stimulus will not be
        presented until the animal gets at least three rewards from
        the opposite port. This is in line with @guo_procedures_2014



# SerialController.py

```
usage: SerialControl.py [-h] [-b] [-lt LICKTHRES] [--verbose]
                        [--repeats REPEATS] [-a] [--port PORT]
                        [--t_stimDELAY T_STIMDELAY] [--ITI ITI ITI]
                        [-rdur T_RDUR] [--dur DUR DUR] [-m MODE]
                        [--t_stimONSET T_STIMONSET] [--datapath DATAPATH]
                        [-rs] [-i ID] [-bc] [-nlp NOLICK] [-w WEIGHT]
                        [-N TRIAL_NUM] [-td TRIALDUR] [-rdel T_RDELAY] [-p]
                        [-to TIMEOUT] [-s] [-lc LCOUNT] [-L | -R]
```

### Requires

* [Windows 7](https://www.microsoft.com/en-au/software-download/windows7)
* [Pandas](http://pandas.pydata.org)
* [Numpy](http://www.numpy.org/)
* [Pyserial](https://github.com/pyserial/pyserial)
* [Colorama](https://pypi.python.org/pypi/colorama)
* An Arduino running `behaviourbox.ino` connected to the same computer

Optional Arguments:
-------------------

```
optional arguments:
  -h, --help            show this help message and exit
  -b, --blanks          include no stim trials
  -lt LICKTHRES, --lickThres LICKTHRES
                        set `lickThres` in arduino
  --verbose             for debug this will print everything if enabled
  --repeats REPEATS     the number of times this block should repeat, by
                        default this is 1
  -a, --auditory        switch to auditory stimulus instead of somatosensory
  --port PORT           port that the Arduino is connected to
  --t_stimDELAY T_STIMDELAY
                        sets the time between succesive stimuli
  --ITI ITI ITI         an interval for randomising between trials
  -rdur T_RDUR, --t_rDUR T_RDUR
                        set end time of reward epoch
  --dur DUR DUR         Durations or to be passed to arduino as DUR_short and
                        DUR_long
  -m MODE, --mode MODE  the mode `h`abituaton or `o`perant, by default will
                        look in the config table
  --t_stimONSET T_STIMONSET
                        sets the time after trigger to run the first stimulus
  --datapath DATAPATH   path to save data to, by default is
                        'C:/DATA/Andrew/wavesurfer/%YY%MM%DD'
  -rs, --right_same     define the right port as correct for same stimulus
  -i ID, --ID ID        identifier for this animal/run
  -bc, --bias_correct   turn on the bias correction for the random number
                        generator
  -nlp NOLICK, --noLick NOLICK
                        set `t_noLickPer` in arduino
  -w WEIGHT, --weight WEIGHT
                        weight of the animal in grams
  -N TRIAL_NUM, --trial_num TRIAL_NUM
                        trial number to start at
  -td TRIALDUR, --trialDur TRIALDUR
                        set minimum trial duration
  -rdel T_RDELAY, --t_rDELAY T_RDELAY
                        set start time of reward epoch
  -p, --punish          sets `break_wrongChoice` to True, incorrect licks will
                        end an operant trial early
  -to TIMEOUT, --timeout TIMEOUT
                        set the timeout duration for incorrect licks
  -s, --single          use this flag for a single stimulus only
  -lc LCOUNT, --lcount LCOUNT
                        set `minlickCount` in arduino
  -L, --left
  -R, --right
```

See Also [list of rejected arguments](http://xkcd.com/1692/)



Interactive Options
-------------------


key          option     
-----------  -----------------
     H       This menu
     P       Punish
     S       toggle single stimulus
     < >     lick threshold 
     ?       show threshold 
     [ ]     lickcount
     \\      show lickcount 
     tab     toggle mode
     : \"     adjust noLick period
     L       show noLick period
     ( )     adjust trial duration
     T       show trial duration period
     Y       toggle timeout (requires punish to take effect)
     B       toggle bias correction
input `rdel` 
input `rdur` 
-----------  -----------------




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



# behaviourbox.ino

This program delivers sensory stimulation and opens water 
valve when the animal touches the licking sensor within a 
certain time window.

### Requirements

* [Arduino uno Rev3](https://www.arduino.cc/en/Main/ArduinoBoardUno)
    :   Connects to the main computer via USB serial

* stimulus
    :   The stimulus needs to take 3.3V digital signal, and be driven
        by a square wave.

* 2×lick ports
    :   I use peizo electric wafers, specifically a [0.6mm Range Piezo 
        Bender Actuator](http://www.piezodriveonline.com/0-6mm-range-piezo-bender-actuator-ba3502/)
        from PiezoDrive Pty Ltd, (Callaghn NSW)

        - The signal from these are very small. The piezos require a linear
            amplifier so that the arduino can detect the signal they produce.
            I use 2× custom made linear amplifiers that each take 5V DC input
            and output in a range from 0-3V. The amplifiers come are from Larkum
            lab designs.
            
           

Setup connections:
------------------

|  DIGITAL  | output            | variable        |
| --------- | ----------------- | --------------- |
| pin 2     | recording trigger | `recTrig`       |
| pin 3     | stimulus          | `stimulusPin`   |
| pin 8     | speaker           | `speakerPin`    |
| pin 10    | left water valve  | `waterValve[0]` |
| pin 11    | right water valve | `waterValve[1]` |

Table: Digital connections to lick controller

| ANALOG    | input             |                 |
| --------- | ----------------- | --------------- |
| A0        | left  lick sensor | `lickSens[0]`   |
| A1        | right lick sensor | `lickSens[1]`   |

Table: Analog connections to lick controller


Global Variables
----------------

type                   name        value            description
----                   ----        -----            -----------
`const char`{.cpp}     recTrig     `2`{.cpp}        digital pin 2 triggers ITC-18
`const char`{.cpp}     stimulusPin `3`{.cpp}        digital pin 4 control whisker stimulation
`const char`{.cpp}     speakerPin  `8`{.cpp}        digital pin 8 control water valve 
`const char`{.cpp}     statusLED   `13`{.cpp}       led connected to digital pin 13
`const char[2]`{.cpp}  waterPort   `{10,11}`{.cpp}
`const char`{.cpp}     lickRep     `13`{.cpp}
`const char[2]`{.cpp}  lickSens    `{A0,A1}`{.cpp}  the piezos are connected to analog pins 0 and 1


Table: connections      






type                        name            value       description
----                        ----            -----       -----------
`unsigned long`{.cpp}       t_init          
`unsigned int`{.cpp}        t_noLickPer     1000          ms
`unsigned int`{.cpp}        trial_delay     500           ms
`unsigned int`{.cpp}        t_stimONSET     2000          ms
`unsigned int`{.cpp}        t_stimDELAY     150           ms
`unsigned int`{.cpp}        stimDUR         500           ms
`unsigned int`{.cpp}        t_rDELAY        2100          ms
`unsigned int`{.cpp}        t_rDUR          2000          ms
`unsigned int`{.cpp}        timeout         0
    
Table: timing parameters


type            name          value           description
----            ----          -----           -----------
`char`{.cpp}    mode          `'-'`{.cpp}     one of `h`abituation, `o`perant
`char`{.cpp}    rewardCond    `'R'`{.cpp}     a value that is 'L' 'R', 'B' or 'N' to represent lick port to be used
`byte`{.cpp}    minlickCount  `5`{.cpp}       
`byte[2]`{.cpp} reward_count  `{0, 0}`{.cpp}  Globals to count number of continuous left and rights

Table: Misc

---------------------------------------------------------------------------------
type                 name          value                             description
----                 ----          -----                             -----------
`bool`{.cpp}         single_stim

`bool`{.cpp}         right_same

`int`{.cpp}          DUR_short     `100`{.cpp}

`int`{.cpp}          DUR_long      `500`{.cpp}

`int[2][2]`{.cpp}    diff_DUR      `{{DUR_short, DUR_long}, `{.cpp}
                                   `{  DUR_long, DUR_short}}`{.cpp}
                                   
`int[2][2]`{.cpp}    same_DUR      `{{ DUR_long, DUR_long},  `{.cpp}
                                   `  {DUR_short, DUR_short}}`{.cpp}

`bool`{.cpp}         right         `1`{.cpp}

`bool`{.cpp}         left          `0`{.cpp}

`int[2][2]`{.cpp}    right_DUR
                     
`int[2][2]`{.cpp}    left_DUR
--------------------------------------------------------------------------------------

Table: stimulus parameters


type                 name          value          description
----                 ----          -----          -----------
`bool`{.cpp}         auditory      `0`{.cpp}      Logical value. Runs in auditory mode when true
`int`{.cpp}          toneGoodLeft  `6000`{.cpp}   Hz
`int`{.cpp}          toneGoodRight `7000`{.cpp}   Hz
`int`{.cpp}          toneGood      `2000`{.cpp}   Hz
`int`{.cpp}          toneBad       `500`{.cpp}    Hz
`int`{.cpp}          toneDur       `100`{.cpp}    ms

Table: audio


type                 name                value                             description
----                 ----                -----                             -----------
`byte[2]`{.cpp}      count               `{0,0}`{.cpp}                     Global value to count the licks
`char`{.cpp}         waterVol            `10`{.cpp}                        uL per dispense
`int`{.cpp}          lickThres           `450`{.cpp}                                 
`bool[2]`{.cpp}      lickOn              `{false, false}`{.cpp}                      
`bool`{.cpp}         verbose             `true`{.cpp}                                 
`bool`{.cpp}         break_wrongChoice   `false`{.cpp}                     stop if the animal makes a mistake

Table: Reward




Start program
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
trials on the same side is used (Thanks to Conrad Lee from ANU). A counter
keeps track of the number of licks, and if the counter reaches 10
the associated port becomes inactive. Licking the other port subtracts
1 from the counter. In this way the animal must balance it's attention on
both ports.

Functions
---------
   
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
    
    ----------- -------------------------------------
    `'L'`{.cpp} correct hit on left port
    `'R'`{.cpp} correct hit on right port
    `'l'`{.cpp} incorrect lick on left port
    `'r'`{.cpp} incorrect lick on right port
    `0`{.cpp}   No lick detected during reward period
    ----------- -------------------------------------


Serial Input / Output
----------------------

*or Poor mans introspection*

```{.cpp}

lickThres = variable_value.toInt();

mode = variable_value[0];

rewardCond = variable_value[0];

break_wrongChoice = bool(variable_value.toInt());

minlickCount = variable_value.toInt();

t_noLickPer = variable_value.toInt();

right_same = bool(variable_value.toInt());

auditory = bool(variable_value.toInt());

single_stim = bool(variable_value.toInt());

timeout = variable_value.toInt();

t_stimDUR = variable_value.toInt();

t_stimONSET = variable_value.toInt();

t_rDELAY = variable_value.toInt();

t_rDUR = variable_value.toInt();

waterVol = variable_value.toInt();

DUR_short = variable_value.toInt();

DUR_long = variable_value.toInt();

OFF = variable_value.toInt();

```

plot_stats.py
==============

### Requires 

* [Bokeh](http://bokeh.pydata.org)
* [Pandas](http://pandas.pydata.org)
* [Numpy](http://www.numpy.org/)


References
==========