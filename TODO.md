
SerialControl.py 

    `menu`
        TODO: On pause show current settings
        TODO: Allow an input mechanism to access all possible values
        TODO: make menu accept a dictionary or something and have it 
              return one as well!
                - Use the keys of the dictionary to allow tab 
                  completion and scrolling of the inputs as well
    
    TODO: Make operant a function like habituation
    TODO: Refactor to separate the reporting from running the trial
              
behaviourbox.ino

    [DONE]: include contingency to report on lick early without breaking?
            - ie monitor licks during the stimulus period and report this value
        TODO: Allow early licks to deliver a reward if correct.
            - Requires monitoring of first lick or some such thing
            
    TODO: make verbosity a scale instead of Boolean