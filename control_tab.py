import time, logging
from engine import Engine

class ControlTab:
    def __init__(self, drone):
        self.vehicle = drone.vehicle
        self.drone = drone
        # engine object maintains movements because we want continuous movement
        # that way when a command is received we update the speed then send it to the
        # engine thread and it will execute that in a loop
        self.engine = Engine(drone, self)
        self.engine.start()
    
    # speed is 3d vector    
    def stopMovement(self):
        string = 's'
        self.vehicle.write(string.encode("UTF-8"))
        # self.engine.executeChangesNow()
        
    def left(self):
        string = 'l'
        self.vehicle.write(string.encode("UTF-8"))
    
    def right(self):
        string = 'r'
        self.vehicle.write(string.encode("UTF-8"))
        
    def forward(self):
        string = 'f'
        self.vehicle.write(string.encode("UTF-8"))
        
    def back(self):
        string = 'b'
        self.vehicle.write(string.encode("UTF-8"))

    def toggleLed(self):        
        string = 'a'
        self.vehicle.write(string.encode("UTF-8"))

    def servoLeft(self):
        string = 'q'
        self.vehicle.write(string.encode("UTF-8"))

    def servoMid(self):
        string = 'w'
        self.vehicle.write(string.encode("UTF-8"))
        
    def servoRight(self):
        string = 'e'
        self.vehicle.write(string.encode("UTF-8"))