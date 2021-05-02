import time, threading, logging
from dronekit import VehicleMode, Command
from pymavlink import mavutil
import serial

# separate thread
class Engine (threading.Thread):
   def __init__(self, drone, control_tab):
      threading.Thread.__init__(self)
      self.daemon = True
      self.drone = drone
      self.vehicle = drone.vehicle
      self.last_mission_cmnd_index = -1
      self.control_tab = control_tab
      ser = serial.Serial('/dev/ttyACM0', 9600)
      
      logging.info('Engine started')
       
   def executeChangesNow(self):
       # we are building message immediatly and flushing it
       msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
       0,       # time_boot_ms (not used)
       0, 0,    # target system, target component
       mavutil.mavlink.MAV_FRAME_BODY_NED, # frame
       0b0000111111000111, # type_mask (only positions enabled)
       0, 0, 0,
       self.control_tab.speed_x, self.control_tab.speed_y, self.control_tab.speed_z, # x, y, z velocity in m/s
       0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
       0, 0)
        
       self.vehicle.send_mavlink(msg)
       self.vehicle.flush()
      
   def killMotorsNow(self):
       # flight termination command mavlink, will instantly kill voltage of ESCs and motors
       msg = self.vehicle.message_factory.command_long_encode(
       1, 1,    # target system, target component
       mavutil.mavlink.MAV_CMD_DO_FLIGHTTERMINATION , #command
       1, #confirmation
       1,  # param 1, yaw in degrees
       1,          # param 2, yaw speed deg/s
       1,          # param 3, direction -1 ccw, 1 cw
       True, # param 4, 1 - relative to current position offset, 0 - absolute, angle 0 means North
       0, 0, 0)    # param 5 ~ 7 not used
       self.vehicle.send_mavlink(msg)
       self.vehicle.flush()
      
   def rotate(self, direction, rotation_angle):
       msg = self.vehicle.message_factory.command_long_encode(
       0, 0,    # target system, target component
       mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
       0, #confirmation
       rotation_angle,  # param 1, yaw in degrees
       1,          # param 2, yaw speed deg/s
       direction,          # param 3, direction -1 ccw, 1 cw
       True, # param 4, 1 - relative to current position offset, 0 - absolute, angle 0 means North
       0, 0, 0)    # param 5 ~ 7 not used
       self.vehicle.send_mavlink(msg)
       self.vehicle.flush()
   
   def run(self):
      while(True):
          try:
              if self.control_tab.speed_x != 0 or self.control_tab.speed_z != 0:
                  self.control_tab.speed_x, self.control_tab.speed_z, # x, z velocity in m/s
                  string = 'f'
                  ser.write(string.encode("UTF-8"))
                  self.vehicle.flush()
              time.sleep(1.5) # since there is delay of 1.5 s here, executeChangesNow() will execute immediatly
              
          except Exception as e:
              logging.error("Engine killed: "+str(e))