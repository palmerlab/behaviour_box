import argparse

p = argparse.ArgumentParser(description="This program controls the Arduino "
                                           "and reads from it too"
                                            )

kwargs = {
    ("-i", "--ID", ) : {
                    'default' : "",
                    'help' : "identifier for this animal/run",
                    },

    ('-repeats', ) : {
                    'default' : 5,
                    'type' : int,
                    'help' : "the number of times this block should repeat, "
                            "by default this is 1",
                    },

    ('-noise', ) : {
                    'action' : 'store_true',
                    'help' : 'plays a noise during trials'
                    },

    ('-ITI', ) : {
                    'nargs' : 2,
                    'default' : [2,5],
                    'type' : float,
                    'help' : "an interval for randomising between trials",
                    },

    ('-datapath', ) : {
                    'default' : "./data",
                    'help' : "path to save data to, "
                            "by default is "
                            "./data",
                    },

    ('-fname', ) : {
                    'default' : "",
                    'help' : "name of file "
                            "if left blank defaults to "
                            "ID + todays date as ID_YYMMDD"
                    },

    ("-port", ) : {
                    'default' : "COM7",
                    'help' : "port that the Arduino is connected to",
                    },

}

for k, v in kwargs.iteritems():
    p.add_argument(*k, **v)

args = p.parse_args()
