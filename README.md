Behaviour Box
=======================

Usage
-----

1. Update the variables in `behaviourbox\USER_variables.h`

   1. Confirm that the pins are correct
   2. Decide on timing variables 

![](documentation\trial_diagram.svg)

2.  Set the trial parameters you want to randomise:

   1. For the opto you have 3:  `{stimulus}{light_stim}{light_resp}`
      Each of these is encoded in a binary variable, so can take the value 0 or 1.
      ​

   2. ​

      ​

   ​

####                                                                     TODO:                                                            ####


Making some major revisions to run the bbox without a digitizer. I'm going to change the way that the bbox outputs to be more inline with what is in the `TODO.md` file. 

It is going to take a single argument of the form:
`{stimulus}{light_stim}{light_resp}`
where each value is a boolean that is three bits, so it should be fast.

The bbox will then continuously output lick times as integers. Because we implement a forced delay between the rising and the falling of the lick time, we can insert the communication in this period. The thing is, I'm not sure I can guarantee transmission....

This will make the serial control much lighter, to the point that I won't need much of the existing overheads....