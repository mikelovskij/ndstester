# ndstester
* This is an attempt to build a very rough way to test the nds2 connection python bindings.
In order to use this tool, the nds2 python swig bindings are required, as well as the  gwpy, numpy, logging and collections modules.
The main class is located in the ndstoast.py file and it contains several method that are used to perform tests on the
 objects created by the nds2 python package.

* A comprehensive test can be performed performed launching the
 ```python tester(self, testchannels=[], servers=None, gpsb=None, gpse=None, stride=5, nrand=10, avail_check=True)```
method of the NdsTester class. A basic documentation on how to use this method is available in the code and can be accessed
from an interactive console after importing the ndstoast module and quering ndstoast.NdsTester.tester?

* A very simple example script that uses the 'tester' and 'resultlogger' methods to perform the tests and to log the
results in a human readable txt file is given in the 'testscript.py' file.
