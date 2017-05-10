.. behaviour_box documentation master file, created by
   sphinx-quickstart on Mon May  1 12:23:15 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for palmerlab\\behaviour_box
==========================================

``Version 3.0.20170201.8``

This documentation describes the code found in the following
source repository: `<https://github.com/palmerlab/behaviour_box>`_.


The repository contains a set of files to implement a Go -- No-Go task
using an Arduino and Python 2.7. 

This software is made up of two complementary components. 

The two components to this implementation are the Arduino code, found in
``./behaviourbox/behaviourbox.ino`` and a Python wrapper for
communicating with this code ``./SerialControl.py``.
The Arduino code is a simple module that implements a single Go -- No-Go
trial at a time. The Python wrapper is used for running a series of trials,
it automates the selection of trial variables and reads the Arduino messages,
logging the results of each trial and saves these in a ``.csv`` file.

.. note:: 
    The Python script was written on Windows and implements some basic
    interaction through Windows specific key bindings.
    In addition, the Python script was written using Python 2.7 and 
    relies heavily on this version's language (ie how byte strings are handled).

The behaviour box program is split into a handful of modules. Each
module mostly holds utility functions for the box as a whole. The file
``behaviourbox.ino`` itself only contains ``setup`` and ``loop``
functions, which call the other components as necessary.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Installation
   hardware
   Usage
   Output
   details
   code
   


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


