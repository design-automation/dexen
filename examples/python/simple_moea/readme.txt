Overview
========

This is a trivial example of an moea. It generates boxes with different sizes, and tries to find
the box with maximum volume and minimum area. Thus, you should end up with a bunch of cubes on the 
pareto front.

All the tasks are in the tasks.py file. The settings.py file contains some constants. 

Running in the WEB UI
=====================
To run this example in the Web UI, you need to do the following.

Upload two files
- tasks.py
- settings.py

Register one event task:
- python tasks.py initialize

Register four dataflow tasks, as follows:

- python tasks.py develop
- {"genotype":{"$exists":true}, "phenotype":{"$exists":false}}

- python tasks.py evaluate_area
- {"phenotype":{"$exists":true}, "score_area":{"$exists":false}}

- python tasks.py evaluate_volume
- {"phenotype":{"$exists":true}, "score_volume":{"$exists":false}}

- python tasks.py feedback
- {"score_area":{"$exists":true}, "score_volume":{"$exists":true}, "alive":{"$equals":true}}

Then run the job.

Running from command line
=========================
To run this job from the command line, edit the username and password in the file main.py. 
Then you need to run this file, i.e.: python main.py

Log files
=========
Log files will be saved to the dexen/scripts folder. 