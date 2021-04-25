import logging, time, argparse, configparser, sys
import socket, os, signal, psutil

from subprocess import Popen
from drone import Drone
from connection_watchdog import ConnectionWatchdog
from data_receiver import DataReceiver
from utils import Utils

# Part-06 Python - How to Run it as a Linux Service
# the above video shows that the .service file has to be moved in the raspi
parser = argparse.ArgumentParser()
# if no --d parameter is passed in, the it was started from console, if it is then started as a service
parser.add_argument('--d', nargs=1, default=None)
args = parser.parse_args()

APP_DIR = args.d[0] if args.d != None else "./"
CONFIGURATIONS = APP_DIR + 'configuration.ini'

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    # the str() below makes it create a new log file on every start
    handlers=[
        logging.FileHandler(APP_DIR + 'logs/main app | ' + str(time.asctime()) + '.log'),
        logging.StreamHandler()
        ]
    # 2 handlers to log to both console and file
)
 
# Reading config file
config = configparser.ConfigParser()
 
if len(config.read(CONFIGURATIONS)) == 0:
    logging.error("Could Not Read Configuration File: " + CONFIGURATIONS)
    sys.exit()
     
DRONE_ID = config['drone']['id']
HOST_IP = config['cloud-app']['ip']
DRONE_CLOUD_SERVER_PORT   = int( config['cloud-app']['control-port'])
MAX_RECONNECTION_ATTEMPTS = int( config['cloud-app']['max-reconnection-attempts'])

if __name__ == '__main__':
    logging.debug('DroneApp has started! Directory %s', APP_DIR)
    
    # endless loop trying to create drone object, could be simulator or pixahawk
    while(True):
        try:
            # if successful then we break cycle
            drone = Drone(config)
            break
        except Exception as e:
            logging.error(str(e), exc_info=True)
            time.sleep(2)
            
    
    # separate thread that will monitor if we are connected
    # if not then its going to freeze the done and attmpt to reconnect
    # does around 1 attempt per second so 180 attempts is about 3 minutes     
    # if it still cant connect then will start emergency procedure
    # is host ip accessible
    
    # IDEALLY WE WOULD START IN A SEPARATE PROCESS AND USE RABBITMQ OR SOCKET TO OBTAIN INFO OR DAT DATABASE
    # COULD ALSO MAKE WATCHDOG BE MAIN APPLICATION AND START VIDEO STRAM AND CONTROL PROCESS
    watchdog = ConnectionWatchdog(drone, HOST_IP, MAX_RECONNECTION_ATTEMPTS)
    watchdog.start()
    
    # holds process and can monitor if process exists
    # and if we need to kill or stop then this variable will be it
    video_streamer_proc = None
    control_server_socket = None
    server_message_receiver = None
    
    # main thread will wait here until watchdog says were connected
    # once we get to this line we assume there is connection to internet and drone
    while drone.is_active: # this is related to the kill motors button on the UI
        # we need try catch because we should not kill this thread
        try:
            # this variable shows wether drone is connected to internet or not
            # once connected to internet this will break and move on
            # we are blocking until the above thread connects ConnectionWatchdog()
            while not watchdog.net_status:
                time.sleep(1)
                
            # once connection is made 
            # we wait 3 seconds because resources may not be release immidiatly
            # such as raspi camera which could be an issue when reconnecting after a disconnect   
            time.sleep(3)
            
            #socket connection with backend
            control_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            control_server_socket.connect((HOST_IP, DRONE_CLOUD_SERVER_PORT))
            logging.info('Socket Connection Opened')

            # first thing to do after connect is to send drone id
            # java app will connect drone handler with id
            droneIdBytes = Utils.createNetworkMessage(str.encode(DRONE_ID))
            control_server_socket.send(droneIdBytes)
            logging.info('Drone ID: %s Connected To Control Server Endpoint: %s:%s', str(DRONE_ID), HOST_IP, str(DRONE_CLOUD_SERVER_PORT))
            
            # now we start video sending Popen - python process open command
            # will run from superuser
            # separate process so that we are always sending video no matter what
            
            # VIDEO WE CAN RUN FROM ANOTHER PROCESS CAUSE WE DONT COMMUNICATE WITH IT FROM HERE
            video_streamer_proc = Popen('/usr/bin/python3 ' + APP_DIR + 'video_streamer.py', shell=True)
            
            # activate receiver thread
            server_message_receiver = DataReceiver(control_server_socket, drone)
            server_message_receiver.start()
            
            # until we are connected to the internet and drone is active
            # from the drone we receive telemetry data
            while watchdog.net_status and drone.is_active:
                # we create network message and send it and continuously repeat
                # this is blocking but the receiver thread above will be running concurrently
                msg = Utils.createNetworkMessage(drone.getDroneDataSerialized())
                control_server_socket.send(msg)
                time.sleep(1)
            
        # we can have many exceptions here so we will catch it and freeze the drone (stop at the point where it is and wait 
        # until were connected to internet)    
        except Exception as e:
            logging.error(str(e), exc_info=True)
            drone.freeze()

        # to release resources
        # finally clause will always execute    
        finally:
            if video_streamer_proc != None:
                # psutil library will find process id and also its children and kill them
                current_process = psutil.Process(video_streamer_proc.pid)
                children = current_process.children(recursive=True)
                
                # children are killed
                for child in children:
                    if child.pid != os.getpid():
                        os.kill(child.pid, signal.SIGKILL)

                # parent is killed
                os.kill(video_streamer_proc.pid, signal.SIGKILL)
            
            if control_server_socket != None:
                control_server_socket.close()
            if server_message_receiver != None:
                server_message_receiver.stop()
            
    # close the drone itself
    drone.close()
    
    logging.info('Drone Offline')