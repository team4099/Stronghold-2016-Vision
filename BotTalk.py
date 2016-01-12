#!/usr/bin/python
import socket
import sys
import struct
#import threading

from ShootingCalculation import ShootingCalculation

"""
    Handles communication between bot and this onboard processor

    Kent Ma
    FRC 4099
"""

def return_calculations(clientsocket, processor):

    """ Calls internal systems to calculate the firing angle and sends it to
    the given socket.

    Parameters:
        :param:`clientsocket` - Socket to send output to
        :param:`processor` - Processing system (ShootingCalculation obj) to call

    Output format:
        Sends a string with the following:

            <acquired>,<verticalAngle>,<firingAcceleration>,<lateralAngle>

        Acquired states:
        0 - No target acquired
        1 - Target was successfully acquired and can be fired upon
    """

    processor.pollKinect()

    if processor.getAcquired():
        processor.update()
        verticalAngle = processor.getVerticalAngle()
        firingAcceleration = processor.getFiringAcceleration()
        lateralAngle = processor.getLateralAngle()
        message = [1, verticalAngle, firingAcceleration, lateralAngle]
    else: 
        message = [0]

    clientsocket.send(",".join(str(i) for i in message).encode("utf-8"))
    clientsocket.close()


def main():
    processor = ShootingCalculation(.25)

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddr = ('0.0.0.0', 5802)
    serverSocket.bind(serverAddr)
    serverSocket.listen(5)

    #try:
    while True:
        (clientsocket, clientaddr) = serverSocket.accept()

        #: TODO: Threading? May not be necessary
        return_calculations(clientsocket, processor)

if __name__ == "__main__":
    main()
