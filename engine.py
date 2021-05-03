import time, threading, logging

# separate thread
class Engine (threading.Thread):
   def __init__(self, drone, control_tab):
      threading.Thread.__init__(self)
      self.daemon = True
      self.drone = drone
      self.vehicle = drone.vehicle
      self.control_tab = control_tab      
      logging.info('Engine started')
       
   def executeChangesNow(self):       
       self.vehicle.write(string.encode("UTF-8"))
       self.vehicle.flush()
   
   def run(self):
      while(True):
          try:
            #   if xxxx
            #       string = 'f'
            #       self.vehicle.write(string.encode("UTF-8"))
            #       self.vehicle.flush()
              time.sleep(1.5) # since there is delay of 1.5 s here, executeChangesNow() will execute immediatly
              
          except Exception as e:
              logging.error("Engine killed: "+str(e))