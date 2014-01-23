TPySelector example
===================
Granted, this example does not make a lot of sense from a physical point of few but demonstrates how to run a local analysis written in python and using the TPySelector class.
Unfortunately, I cannot make the root files with the data available so on cannot run this but I hope that the code is clear enough to see what is going on and trust me, it works!
What this progam actuall does is:

1. Get options from the command line and put the files in a chain or fileset.
2. Process the files with Proof-lite. It is not really any analysis, just categorizing tracks into "associated" and "trigger" particles and filling it into a histogram.

It can be run (if one had the files ;)) with:


    $ python main.py --assoc 0.5 1 --triggers 1 

