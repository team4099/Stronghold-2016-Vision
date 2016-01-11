# 4099: FIRST Stronghold Vision
Vision system for Team 4099's FIRST Stronghold robot

###Discussed:
* Distance to top of tower from Kinect is more than 4 meters
* To make it work:
* Physics processing on UDOO - how much to turn, what power to fire at, turn amount, etc
* Knowing distance from end of defense to castle wall and distance from castle wall to tower goal, we can get ground distance to tower goal (coming out of low bar)
* For teleop, some other method of getting distance to goal
* Keep shooter facing forwards unless going through portcullis (nothing else needs a ramp, and we don't have to spin around to get a shot off)
* If not that, at least start facing forward for the shooter in auto mode
