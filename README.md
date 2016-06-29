---
link-citations: true
---

Andrew's Behaviour Box
=======================

Version 3.0: Capacitive sensors
-------------------------------

`BB_V3.0.20160629`

This is the collection of files I use to run my behavioural experiments.

This branch record the state of the first fairly stable version.
It implements a frequency discrimination task, described by the 
following diagram.

Operant Mode
------------

![Flow of the behavioural paradigm](.\Flow_diagram.svg)


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
usage: SerialControl.py [-h] [-i ID] [-w WEIGHT] [-m MODE] [--repeats REPEATS]
                        [-p] [--verbose] [-a] [-bc] [-b] [-rs] [-s]
                        [-lt LICKTHRES] [-lc LCOUNT] [-nlp NOLICK]
                        [-td TRIALDUR] [-rd T_REWARDSTART] [-rend T_REWARDEND]
                        [-to TIMEOUT] [--freq FREQ FREQ] [--ITI ITI ITI]
                        [-L | -R] [-N TRIAL_NUM] [--datapath DATAPATH]
                        [--port PORT]
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
  -h, --help            show this help message and exit
  -i ID, --ID ID        identifier for this animal/run
  -w WEIGHT, --weight WEIGHT
                        weight of the animal in grams
  -m MODE, --mode MODE  the mode `h`abituaton or `o`perant, by default will
                        look in the config table
  --repeats REPEATS     the number of times this block should repeat, by
                        default this is 1
  -p, --punish          sets `break_wrongChoice` to True, incorrect licks will
                        end an operant trial early
  --verbose             for debug this will print everything if enabled
  -a, --auditory        switch to auditory stimulus instead of somatosensory
  -bc, --bias_correct   turn on the bias correction for the random number
                        generator
  -b, --blanks          include no stim trials
  -rs, --right_same     define the right port as correct for same stimulus
  -s, --single          use this flag for a single stimulus only
  -lt LICKTHRES, --lickThres LICKTHRES
                        set `lickThres` in arduino
  -lc LCOUNT, --lcount LCOUNT
                        set `minlickCount` in arduino
  -nlp NOLICK, --noLick NOLICK
                        set `t_noLickPer` in arduino
  -td TRIALDUR, --trialDur TRIALDUR
                        set minimum trial duration
  -rd T_REWARDSTART, --t_rewardSTART T_REWARDSTART
                        set start time of reward epoch
  -rend T_REWARDEND, --t_rewardEND T_REWARDEND
                        set end time of reward epoch
  -to TIMEOUT, --timeout TIMEOUT
                        set the timeout duration for incorrect licks
  --freq FREQ FREQ      Frequencies or OFF time values to be passed to arduino
                        as off_short and off_long
  --ITI ITI ITI         an interval for randomising between trials
  -L, --left
  -R, --right
  -N TRIAL_NUM, --trial_num TRIAL_NUM
                        trial number to start at
  --datapath DATAPATH   path to save data to, by default is
                        'C:/DATA/Andrew/wavesurfer/%YY%MM%DD'
  --port PORT           port that the Arduino is connected to

```

See Also [list of rejected arguments](http://xkcd.com/1692/)



Interactive Options
-------------------


key         option     
----------- -----------------
     H      This menu
     P      Punish
     S      toggle single stimulus
     < >    lick threshold 
     ?      show threshold 
     [ ]    lickcount
     \\     show lickcount 
     tab    toggle mode
     : \"    adjust noLick period
     L      show noLick period
     ( )    adjust trial duration
     T      show trial duration period
     Y      toggle timeout (requires punish to take effect)
     B      toggle bias correction
----------- -----------------




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

|  DIGITAL  | output             | variable        |
| --------- | ------------------ | --------------- |                               
| pin 2     | IRQ comm interrupt | `irqpin`        |
| pin 3     | recording trigger  | `recTrig`       |
| pin 4     | bulb style trigger | `bulbTrig`      |
| pin 5     | stimulus           | `stimulusPin`   |
| pin 6     | Punishment Buzzer  | `buzzerPin`     |
| pin 7     | speaker            | `speakerPin`    |
| pin 10    | left water valve   | `waterValve[0]` |
| pin 11    | right water valve  | `waterValve[1]` |

Table: Digital connections to lick controller

| ANALOG    | input             |                 |
| --------- | ----------------- | --------------- |
| A0        | left  lick sensor | `lickSens[0]`   |
| A1        | right lick sensor | `lickSens[1]`   |
| A4        | MPR121 SCL        | `Wire`          |
| A5        | MPR121 SDA        | `Wire`          |

Table: Analog connections to lick controller
  
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

adjustable parameters
:    + `lickThres`
    + `mode`
    + `trialType`
    + `break_wrongChoice`
    + `minlickCount`
    + `t_noLickPer`
    + `OFF`
    + `ON`
    + `auditory`
    + `timeout`
    + `t_stimONSET`
    + `t_stimDUR`
    + `t_rewardDEL`
    + `t_rewardDUR`
    + `waterVol`

```{.cpp}
int UpdateGlobals(String input) {
    /*
    This is a big ugly function which compares the
    input string to the names of variables that I have
    stored in memory; This is very much not the `C` 
    way to do things...
    
    I think this could be a hash table. I haven't
    learned enough about hash table implementation
    yet and I know this works, so for the moment:
    *If it ain't broke*...
    */

    // sep is the index of the ':' character
    int sep = getSepIndex(input, ':');

    if (sep) {
        
        String variable_name = input.substring(0,sep);
        String variable_value = input.substring(sep+1);
        
        Serial.print("#");
        Serial.print(variable_name);
        Serial.print("\t");
        Serial.println(variable_value);
        
        // input before seperator?
        
        if (variable_name == "lickThres") {
                lickThres = variable_value.toInt();
                Serial.print("lickThres:\t");
                Serial.println(lickThres);
                return 1;
        }
            
        else if (variable_name == "mode") {
                mode = variable_value[0];
                Serial.print("mode:\t");
                Serial.println(mode);
                return 1;
        }
            
        else if (variable_name == "rewardCond") {
                rewardCond = variable_value[0];
                Serial.print("rewardCond:\t");
                Serial.println(rewardCond);
                return 1;
        }
          
        else if (variable_name == "break_wrongChoice") {
                break_wrongChoice = bool(variable_value.toInt());
                Serial.print("break_wrongChoice:\t");
                Serial.println(break_wrongChoice);
                return 1;
        }
            
        else if (variable_name == "minlickCount") {
                minlickCount = variable_value.toInt();
                Serial.print("minlickCount:\t");
                Serial.println(minlickCount);
                return 1;
        }
        else if (variable_name == "t_noLickPer") {
                t_noLickPer = variable_value.toInt();
                Serial.print("t_noLickPer:\t");
                Serial.println(t_noLickPer);
                return 1;
        }
        else if (variable_name == "right_same") {
                right_same = bool(variable_value.toInt());
                Serial.print("right_same:\t");
                Serial.println(right_same);
                return 1;
        }
        else if (variable_name == "off_short") {
                off_short = variable_value.toInt();
                Serial.print("off_short:\t");
                Serial.println(off_short);
                return 1;
        }
        else if (variable_name == "off_long") {
                off_long = variable_value.toInt();
                Serial.print("off_long:\t");
                Serial.println(off_long);
                return 1;
        }
        else if (variable_name == "auditory") {
                auditory = bool(variable_value.toInt());
                Serial.print("auditory:\t");
                Serial.println(auditory);
                return 1;
        }
        else if (variable_name == "single_stim") {
                single_stim = bool(variable_value.toInt());
                Serial.print("single_stim:\t");
                Serial.println(single_stim);
                return 1;
        }
        else if (variable_name == "timeout") {
                timeout = variable_value.toInt();
                Serial.print("timeout:\t");
                Serial.println(timeout);
                return 1;
        }
        else if (variable_name == "t_rewardSTART") {
                t_rewardSTART = variable_value.toInt();
                Serial.print("t_rewardSTART:\t");
                Serial.println(t_rewardSTART);
                return 1;
        }
        else if (variable_name == "t_rewardEND") {
                t_rewardEND = variable_value.toInt();
                Serial.print("t_rewardEND:\t");
                Serial.println(t_rewardEND);
                return 1;
        }
        else if (variable_name == "waterVol") {
                waterVol = variable_value.toInt();
                Serial.print("waterVol:\t");
                Serial.println(waterVol);
                return 1;
        }        
   }
   return 0;
}
```

plot_stats.py
==============

### Requires 

* [Bokeh](http://bokeh.pydata.org)
* [Pandas](http://pandas.pydata.org)
* [Numpy](http://www.numpy.org/)


References
==========