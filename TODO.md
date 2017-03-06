
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


-------------------------------------------------------------------------------

### TODO:

Presently the new box compiles.

- [ ] Remove all deprecated features from this Read Me!
- [ ] Make the thresholds for each sensor independent, 
      and modifiable through python
- [ ] Make a nice way to switch between GnG and 2AFC
- [ ] Make a flag for the buzzer to turn on and off.
- [ ] Make sure all existing / relevant variables can be accessed through 
      python menu
- [ ] make the python menu accept a dict or something for general interfacing.
    - [ ] consider tab completion and raw_input to access all variables.
    - [ ] Have both a quick hotkey menu and tab completing complete interface.


- [ ] What I would like is to report a matrix of times of lick events back to the
     python program.

    Conceptually to do this I would replace the constant print outs
    with a single boiler plate variable which contains all the relevant values.
    the ultimate printout might be something like this:

    ```yaml
    - trial: 03d
        #These values all got printed in one hit before commencing a trial
        - parameters:
            - variable: value
            - variable: value
            - variable: value
            - variable: value
        
        #These get printed in a stream as the licksensor runs...
        - licks: [t, ..., t]
        
        #These values would all be printed at the end of the 
        - events:
            - event: [status, time]
            - event: [status, time]
            - event: [status, time]
            - event: [status, time]
    ```
--------------------------------------------------------------------------------
