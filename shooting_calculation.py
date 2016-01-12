#!/usr/bin/python
"""
    Calculates recommended firing acceleration and angles to land a shot

    Kent Ma
    FRC 4099
"""

class ShootingCalculation(object):
    def __init__(self, period):
        """ 
        
        :param:`period` - delay for distance sensor polling. May not be necessary
        """
     
        self.verticalAngle = None
        self.firingAcceleration = None
        self.lateralAngle = None
        self.acquired = False
        self.period = period

    def getAcquired(self):
        """ If the goal target was in sight AND a shot can make it in """
        return self.acquired

    def getVerticalAngle(self):
        """ Vertical angle to move the shooter """
        return self.verticalAngle

    def getFiringAcceleration(self):
        return self.firingAcceleration

    def getLateralAngle(self):
        """ Lateral angle to move the shooter """
        return self.lateralAngle

    def update(self):
        """ Performs calculations to find recommended firing angle, firing 
        acceleration, and rotation angle
        """
        #: TODO
        self.verticalAngle = 90
        self.firingAcceleration = 17
        self.lateralAngle = 45

    def pollKinect(self):
        #: TODO
        """ Polls internal kinect system for latest vision information """
        self.acquired = True
        pass
