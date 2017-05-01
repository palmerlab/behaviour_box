Install
=======

Many of the steps described here require administrator privileges on the
PC that you are using.

Arduino
-------

To install the Arduino component you will need to have the Arduino IDE
which you can get from
`here <https://www.arduino.cc/en/Main/Software>`__. The instructions for
how to setup Arduino on Windows can be found
`here <https://www.arduino.cc/en/Guide/ArduinoUno>`__.

Once the Arduino IDE is installed open ``behaviourbox\behaviourbox.ino``
in the Arduino editor. With an Arduino plugged in to the USB port you
can now upload the code using the ``compile/run`` button in the editor.
Note the the port that the Arduino is connected to (It'll be labeled
``COMx`` where ``x`` is an integer).

Python
------

This system was written using python 2.7 on Windows 7. You can download
python from
`here <https://www.python.org/downloads/release/python-2713/>`__

Because this is a command line interface it helps to have python
available from the system path, in addition you should have the python
package manager (pip) for installing the dependencies. To do all that I
would recommend following this `setup
guide <https://www.howtogeek.com/197947/how-to-install-python-on-windows/>`__.

For those familiar with installing python dependencies on windows the
packages and versions used here can be found in ``requirements.txt``.

Go to Christop Gohlke's `Unofficial Windows Binaries for Python
Extension Packages <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`__ page
and make sure to follow the instructions there for installing
numpy\ `1 <#f1>`__\ .

-  Download additional packages from
   http://www.lfd.uci.edu/~gohlke/pythonlibs/

   -  `Pandas <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pandas>`__
   -  `sounddevice <http://www.lfd.uci.edu/~gohlke/pythonlibs/#sounddevice>`__
   -  **These smaller packages are also required and can be downloaded
      from the same site.** Use your browsers search to find them, they
      cannot be linked to

      -  Colorama
      -  Pyserial

In windows open an elevated command window. To do this find cmd.exe in
the start menu, right click and select run as administrator. Now cd to
the directory containing the ``.whl`` files that you just downloaded.
You should then be able to run ``pip install *.whl`` to get all the
packages.

Requirements
~~~~~~~~~~~~

-  `Windows
   7 <https://www.microsoft.com/en-au/software-download/windows7>`__
-  `Pandas (0.19.0) <http://pandas.pydata.org>`__
-  `Numpy (1.11.2+mkl) <http://www.numpy.org/>`__
-  `Pyserial (2.7) <https://github.com/pyserial/pyserial>`__
-  `Colorama (0.3.7) <https://pypi.python.org/pypi/colorama>`__
-  `sounddevice
   (0.3.5) <http://python-sounddevice.readthedocs.io/en/0.3.5/>`__
-  An Arduino running ``behaviourbox.ino`` connected to the same
   computer

--------------

1 Follow specific instructions for installing Numpy+mkl. Numpy is a
python package which is designed for dealing with numerical arrays
quickly. The mkl version is simply a version of the package that has
been compiled with the intel math kernel libraries. This makes it a lot
faster than the basic version. This system doesn't necessarily require
the speed of the mkl version, but it is a nice thing to have `↩ <#a1>`__
