Usage
=====

A set of trials are run through the ``SerialController.py`` script. At
the windows command prompt cd to the root directory of the
behaviour\_box repository.

When the program runs the first thing it does is make a new folder to
save the logs in. The base of the new directory can be specified by
``--datapath`` and the new folder is always the current date is in the
format YYMMDD.

In addition it also creates two files, a raw log file which stores all
time stamped communications sent and received by the program, and a csv
file which contains the same data in tabulated form. The name pattern
for the csv is ``{ID}_{date}_000.csv`` where ID is given with the
``-ID`` argument and date is in the format YYMMDD.

.. note::
    It is important to note that the data files will be appended to each
    time the program is run over the course of the day, unless a new ID is
    specified.

Next the program checks the serial port specified by the ``--port``
argument. By default, if no port is specified the program will search
the available ports for any Arduino that is plugged in. If more than
one Arduino is available it will print a warning, followed by a list 
of Arduino ports. It will then select the first arduino.
On Windows the serial ports are specified by ``COMx`` where
``x`` is some integer. If no communications are found the program 
will exit. 

.. note ::
    If you always have the Arduino detected on the same port
    you can adjust the default value of the ``port`` variable to avoid setting
    this flag each run, see :ref:`adjust-defaults`. This strategy applies to
    all the variables that might remain invariant between sessions.


When the connection has been established the program first transmits a
number of configuration variables to the arduino, such as the lick
threshold, and timing information. These can be updated online later,
but it saves time to avoid sending them on each trial if they are
unchanged.

The program then begins to loop through the ``trials`` variable, which
is an iterable list of the stimulus durations. On each loop the program
tells the Arduino what duration to play, and whether or not to reward a
lick.

At this point the program sends the ``START`` message to the Arduino and
the trial begins. As the trial runs the program monitors the Arduino
status messages as they come in.

At the end of the trial the program collects all the status messages and
formats them into a Pandas DataFrame, which is then saved into
``{ID}_{date}_000.csv``


Interactive Options
-------------------

The Python wrapper was written to allow for limited interaction with the 
Arduino while a trial was being run without the need to touch the source code 
and recompile. With animal experimentation in mind it was decided that it 
would be best to avoid editing the control code during a run. The Arduino
exposes a number of relevant variables to the Serial Communications port,
which the Python wrapper reads and writes to.
 
The interactive options currently provided allow the following variables to be 
altered online:

* lick threshold
* show threshold
* lick count
* show lick count
* toggle mode
* adjust no lick Period
* show no Lick Period
* adjust trial duration
* toggle time out

.. _adjust-defaults:

Adjusting Default Arguments
---------------------------

The default parameters to the Python Script are all set in the file
``utilities\args.py``. The file looks something like this::

    import argparse
    
    # create the argument parsing object
    p = argparse.ArgumentParser(description="This program"
                                            "controls the Arduino" 
                                            "and reads from it too"
                                            )
                                            
    # construct a dictionary of program parameters
    kwargs = {
        ("-i", "--ID", ) : {
                        'default' : "_", 
                        'help' : "identifier for this animal/run",
                        },

                .
                .
                .
                        
        ("--port", ) : {
                        'default' : None,
                        'type' : str,
                        'help' : "port that the Arduino is connected to",
                        },
    }

    # load the argument parser with the parameters specified
    for k, v in kwargs.iteritems():
        p.add_argument(*k, **v)

    # read the command line arguments
    args = p.parse_args()

    
Each of the parameters that can be supplied as arguments to the Python Script
are defined in the ``kwargs`` dictionary in this file. Supplying a new value to
the ``'default'`` key of any of these parameters will set the value that the
program loads with if no value for that parameter has been supplied at the
command line.

For instance, on my system, my Arduino is always located on the port ``"COM5"``,
therefore my file looks something like this::

    import argparse
    
    # create the argument parsing object
    p = argparse.ArgumentParser(description="This program"
                                            "controls the Arduino" 
                                            "and reads from it too"
                                            )
                                            
    # construct a dictionary of program parameters
    kwargs = {
        ("-i", "--ID", ) : {
                        'default' : "_", 
                        'help' : "identifier for this animal/run",
                        },

                .
                .
                .
                        
        ("--port", ) : {
                        'default' : "COM5",
                        'type' : str,
                        'help' : "port that the Arduino is connected to",
                        },
    }

    # load the argument parser with the parameters specified
    for k, v in kwargs.iteritems():
        p.add_argument(*k, **v)

    # read the command line arguments
    args = p.parse_args()
