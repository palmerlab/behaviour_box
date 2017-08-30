################
Code Reference
################

============
Arduino Code
============



-----------
SerialComms
-----------

.. c:function::  getSerialInput()

      This function reads the data from the serial
      connection and returns it as a string.

      This is used later to update the values

.. c:function:: getSepIndex(String input, char separator)

      Returns the index of the separator character
      in a string.


.. c:function:: UpdateGlobals(String input)

    This is a big ugly function which compares the
    input string to the names of variables that I have
    stored in memory; This is very much not the `C`
    way to do things...

    I think this could be a hash table. I haven't
    learned enough about hash table implementation
    yet and I know this works, so for the moment:
    *If it ain't broke*...


-----------
sensors
-----------

.. c:function:: senseLick()

    1. check to see if the lick sensor has moved:
         if the sensor was in a low state, allow the calling of a rising edge.
    2. check if the sensor is above threshold
    3. report if the state of lickOn has change


----------------------
single_port_setup
----------------------

.. c:function:: runTrial()

    returns 0 if the stimulus was applied
    returns 1 if a timeout is required
    until next trial

    local variables and initialisation of the trial
    ``t_init`` is initialised such that ``t_since``
    returns 0 at the start of the trial, and
    increases from there.

    trial_phase0
    while the trial has not started
           1. update the time
           2. check for licks
           3. trigger the recording by putting ``recTrig = HIGH``



.. c:function:: Habituation()

    1. Determine the appropriate stimulus
    2. set active port
    3. counts number of sequential licks
        - Uses the C ternary operator, which has the form:
          ``A = boolean ? assignment if true : assignment if false;``
          the active port count gets incremented to a maximum of ten,
          while the non-active port count gets decremented to a minimum
          of zero. This is an important caveat as the counts are
          made with unsigned variables, meaning that one less than zero
          is actually 255!


-----------
States
-----------

.. c:function:: ActiveDelay(unsigned long wait, bool break_on_lick)

  needs to be documented

.. c:function:: deliver_reward(bool water)

  Open the water port on `port` for a
  duration defined by waterVol

.. c:function:: punish(int del)

  plays the punishment tone / buzzer

.. c:function:: Timeout(unsigned long wait, int depth)

  runs a time out

.. c:function:: preTrial()

  while the trial has not started
       1. update the time
       2. check for licks
       3. trigger the recording by putting recTrig -> HIGH


.. c:function:: TrialStimulus()

    runs the trial stimulus


.. c:function:: conditional_tone(int frequency, int duration)

    wrapper function so I don't need to put a billion if statements


-------------------------------------------------------------------------------


============
Python Code
============


.. function:: menu()

    Reads the characters in the buffer and modifies the program
    parameters accordingly

    see :ref:`interactivity`


-----------
Audio
-----------

.. function:: band_limited_noise(min_freq, max_freq, samples=1024, samplerate=1)


    Generates noise within a particular band of frequencies


.. function:: fftnoise(f)

    filter used in band_limited_noise

----------------------
config_loader
----------------------

.. function:: write_out_config(params, ID)


    writes a subset of parameters to an ini file which can then be
    used to recover variable values.


.. function:: ConfigSectionMap(section, Config)

    Helper function for reading configuration objects to a dictionary


.. function:: restore_old_config(ID)

    reads the old ini file.
    checks to see if the current ID is in the ini sections
    restores the varible values in the global namespace
    (Hacky solution)


----------------------
data_directories
----------------------

.. function:: timenow()

    provides the current time string in the form `HH:MM:SS`

    :return: the current time in the form `HH:MM:SS`
    :rtype: str

.. function:: today()

    provides today's date as a string in the form YYMMDD

    :return: the date as a string in the form YYMMDD
    :rtype: str

.. function:: create_datapath(DATADIR = "", date = today())

    make a path to save the data based on today's date



.. function:: create_logfile(DATADIR = "", date = today(), port = None, ID = None)

    make a logfile to save communications, based on today's date

----------------------
serial_wrapper
----------------------

.. function:: timenow()

    provides the current time string in the form `HH:MM:SS`

.. function:: init_serialport(port, logfile = None, ID = None)

    Open communications with the arduino;
    quits the program if no communications are
    found on port.

    If there are communications the script
    waits 500 ms then reads all incoming
    lines from the Serial port. These two
    lines include the arduino code version
    and a string that says the arduino is online


.. function:: Serial_monitor(ser, logfile, show = True, ID = None, verbose = None)

    Reads from the serial port one line at time.



.. function:: Continuous_monitor_arduino(ser, end_trial_msg = "- Status Ready", sep = ':', debug_flags = (("#", "\t#", "- ")), ID = None, verbose = None, logfile = None,)


        continously loops through messages from the serial monitor
        until the end_trial_msg is recieved.
        messages that are not preceded by debug_flags are stored in a
        dictionary which is returned by this function.



.. function:: update_bbox(ser, params, logfile, trial_df = {}, ID = None, verbose = None)

    Communicates the contents of the dict `params` through
    the serial communications port.

    data is sent in the form: `parmas[key] = value`  --> `key:value`

    trail_df dictionary is updated to include the parameters
    received from the arduino


-----------
numerical
-----------

Previously held functions to help with numerical
handling, these have mostly been replaced, now contains a
function for general conversion of strings to numbers

.. function:: num(s)

    First attempts to convert string s to an integer.
    If that gives a ValueError then it attempts to return s
    as a float. Finally if s cannot be converted to a float or
    an int, the string is returned unchanged.
