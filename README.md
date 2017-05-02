Behaviour Box
=============

This repository contains a set of files to implement a Go-No-Go
task using an Arduino and Python 2.7. By itself this collects some summary
information for a behavioural trial, but is not a stand alone implementation.
In addition to what is recorded here, I record the signal direct from the
lick sensor using  [Wavesurfer](https://github.com/JaneliaSciComp/Wavesurfer).

The two components to this implementation are the Arduino code, found in
`./behaviourbox/behaviourbox.ino` and a Python wrapper for communicating
with this code `./SerialControl.py`.

Note: *The python wrapper is not written in a cross platform way, it relies 
on specific bindings for windows keyboard events.*

[Documentation](https://palmerlab.github.io/index.html)
-------------------------------------------------------
