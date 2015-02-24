# LeapDryer

##### 4th Year MEng Engineering Project
##### School of Engineering, University of Warwick

Using a Leap Motion to control the airflow velocity of a hand dryer with RC servos.

Current hardware system involves an Arduino for servo control, and external laptop for Leap data processing. Methods for transmitting raw USB data are being researched so that the nearby-laptop dependence can be removed.

Files here include an HTML/Javascript visualiser for the Leap data, and a Python script for the embedded system and recording of test data.

An algorithm will be produced that correlates selected Leap variables (r,p,y,x,y,z,grip...) to sound level so that different hand positions can be acted upon to reduce noise.
