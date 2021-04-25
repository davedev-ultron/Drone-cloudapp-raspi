import time, threading, logging
from dronekit import VehicleMode, Command
from pymavlink import mavutil

# separate thread
class Engine (threading.Thread):
   def __init__(self, drone, control_tab):
      threading.Thread.__init__(self)
      self.daemon = True
      self.drone = drone
      self.vehicle = drone.vehicle
      self.last_mission_cmnd_index = -1
      self.control_tab = control_tab
      
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
              # checking to see if weve executed the last command
              if self.vehicle.commands.next == self.last_mission_cmnd_index:
                  self.drone.state = 'MISSION OVER'
                  # then we reset commands
                  self.vehicle.commands.next = 0
                  self.last_mission_cmnd_index = -1
                  self.vehicle.mode = VehicleMode("GUIDED")
                  #self.control_tab.togleLights()
              
              # if were not on a mission
              # we want to maintain some speed
              # rotation is not maintained only speed
              if self.control_tab.speed_x != 0 or self.control_tab.speed_y != 0 or self.control_tab.speed_z != 0:
                  # we construct a message of type my frame body net
                  msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
                  0,       # time_boot_ms (not used)
                  0, 0,    # target system, target component
                  mavutil.mavlink.MAV_FRAME_BODY_NED, # frame
                  0b0000111111000111, # type_mask (only positions enabled)
                  0, 0, 0,
                  self.control_tab.speed_x, self.control_tab.speed_y, self.control_tab.speed_z, # x, y, z velocity in m/s
                  # here you could set acceleration but currently not impleemnted in current version of pixahawk
                  0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
                  0, 0)
        
                  self.vehicle.send_mavlink(msg)
                  # flush - whatever is in buffer will be sent to pixahawk
                  self.vehicle.flush()
              time.sleep(1.5) # since there is delay of 1.5 s here, executeChangesNow() will execute immediatly
              
          except Exception as e:
              logging.error("Engine killed: "+str(e))