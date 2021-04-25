import logging, threading

import ProtoData_pb2 as proto_library
from command_data_dto import CommandData
from utils import Utils

# extends thread
class DataReceiver (threading.Thread):
   def __init__(self, socket, drone):
      threading.Thread.__init__(self) # super constructor from object that we extend and provide self instance
      self.daemon = True # low priority can be exited by calling app
      self.socket = socket
      self.drone = drone
      self.isActive = True
      
   # run object that is called when starting thread
   # sidenote, here we are starting our own threads, unlike in java
   # starting own threads is not a good practice, anyway...
   def run(self):
      while(self.isActive):
          # try catch cause we dont want our thread to get destroyed
          try:
              # this will block until we receive something
              data = Utils.readNetworkMessage(self.socket)
              
              # using protobuf to deserialize
              # using command object cause thats what were receiving
              command = proto_library.Command()
              command.ParseFromString(data)
              
              commandData = CommandData()
              # extract code
              commandData.code = command.code
              
              # if its code 14 then we also have to deserialize payload with mission data
              if(command.code == 14):
                  missionData = proto_library.MissionData()
                  missionData.ParseFromString(command.payload)
                  
                  commandData.data = missionData
              
              self.drone.executeCommand(commandData)
              
          except Exception as e:
              logging.error('DataReceiver: '+str(e), exc_info=True)
   
   def stop(self):
       self.isActive = False