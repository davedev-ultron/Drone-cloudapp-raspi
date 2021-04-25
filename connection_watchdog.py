import logging, time, threading
from urllib.request import urlopen

# we are running on a separate thread
# tha paranthesis mean its extending the class
# we must also have the run method
# when we call start() it will start executing the run since it extends thread
class ConnectionWatchdog (threading.Thread):

    def __init__(self, drone, host_ip, max_reconnection_attempts):
        threading.Thread.__init__(self)
        # the thread that will be executing this thread
        # daemon means it can be exited wile it is running if the calling app wants to
        # if its not daemon then the app will wait
        self.daemon = True
        # we create a variable, in python if you want to have local object variable you define it in the constructor
        self.drone = drone
        self.host_ip = host_ip
        self.max_reconnection_attempts = max_reconnection_attempts
        self.connection_attempts = 0
        self.net_status = False

    # run method will be executed automatically by thread
    # independently from code being executed elsewhere so it can run in parallel
    def run(self):
        # just to make sure that resources have been release if were restarting
        time.sleep(5)
      
        # will run endlessly, try catch so that this thread does not break down
        while(True):
            try:
                # every second were checking if internet is on
                if self.is_internet_on():
                    self.connection_attempts = 0
                    time.sleep(1)
                else:
                    # if the connection is lost we freeze the drone
                    self.drone.freeze()
                    self.connection_attempts = self.connection_attempts + 1
                    logging.info("Connection attempt %s, max_reconnection_attempts %s", str(self.connection_attempts), str(self.max_reconnection_attempts))
                    time.sleep(1)
                    if self.connection_attempts == self.max_reconnection_attempts:
                        # if we exceed reeconnect attempts we commence procedure
                        # if we had different procuderes we could pass them in through constructor
                        self.drone.return_to_launch()
                        break
                    
            except Exception as e:
                logging.error(str(e), exc_info=True)
                time.sleep(2)
   

    def is_internet_on(self):
        try:
            # urlopen is python library, we will open url provided here
            # if we have internel and were able to open it then there will be no exception
            # otherwise exception will be threown and well set netstatus to false
            urlopen(str('http://' + self.host_ip), timeout=5)
            self.net_status = True # this variable is checked by the app
            return True
        except: 
            logging.error('ConnectionWatchdog - Network is unreachable: ', exc_info=True)
            self.net_status = False
            return False