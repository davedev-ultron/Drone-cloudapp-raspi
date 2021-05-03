import time, logging, netifaces
from dronekit import connect, VehicleMode, Command
import ProtoData_pb2 as proto
from control_tab import ControlTab
import serial


class Drone:
    def __init__(self, configurations):
        drone_id      = configurations['drone']['id']
        arduino_controller  = configurations['drone']['arduino_controller']
        # in the constructor we extract configurations that we need
        # is connected to telemety port that is a serial port that is defined in config linux device
        self.vehicle = serial.Serial(arduino_controller, 9600)
        logging.info('Connected to Arduino Controller Hardware on:  %s Baud: 9600', arduino_controller)
            
        # create local variables    
        self.drone_id = drone_id
        self.state = "DISARMED"
        self.is_active =True
        self.control_tab = ControlTab(self) # will encapsulate all the logic (take-off, landing, etc), will know mav link commands (think of this as a control panel)
        logging.info("Drone connected")
        
    # will get latest data from vehicle
    def getDroneDataSerialized(self):
        drone_data = proto.DroneData()

        # there is many parameters that can be accessed in vehicle object
        # that are accessible via drone kit
        # want to familiarize myself with their website for more advanced use

        drone_data.state = self.state
        drone_data.drone_id = str(self.drone_id)

        # protobuf library to serialize to string so we can send to java app 
        return drone_data.SerializeToString() 
        
    def freeze(self):
        logging.info('Freezing in a spot')
        # control tab knows the algorythm what that actually means
        # drone doesnt know but control tab does
        self.control_tab.stopMovement()
    
    def toggleLed(self):
        # control tab know gpio outputs of raspi and set them to high or low
        self.control_tab.toggleLed()

    def close(self):
        # release the resources
        self.vehicle.close()

    # when we want to execute a command we receive the object from the protobuf
    # checks what code it is and will call control tab
    def executeCommand(self, command):
        if command.code == 1:
            self.control_tab.forward()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Forward')
            return
        if command.code == 2:
            self.control_tab.back()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Backward')
            return
        if command.code == 3:
            self.control_tab.left()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Left')
            return
        if command.code == 4:
            self.control_tab.right()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Right')
            return
        if command.code == 5:
            self.control_tab.stopMovement()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Stop')
            return
        if command.code == 10:
            self.control_tab.servoLeft()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Servo Left')
            return
        if command.code == 11:
            self.control_tab.servoMid()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Servo Mid')
            return
        if command.code == 12:
            self.control_tab.servoRight()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Servo Right')
            return
        if command.code == 13:
            self.toggleLed()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Toggle LED')
            return