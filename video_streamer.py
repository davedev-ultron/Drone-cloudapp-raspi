# this file is to read frames from camera and send to cloudapp
# making video into its own file here for resiliency
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import time, socket, logging, configparser, argparse, sys
import utils from Utils

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
        logging.FileHandler(APP_DIR + 'logs/video-streamer | ' + str(time.asctime()) + '.log'),
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
VIDEO_PORT = int( config['cloud-app']['video-port'])

GRAYSCALE = config['video']['grayscale'].lower() == 'true'
FRAMES_PER_SECOND = int( config['video']['fps'])
JPEG_QUALITY = int( config['video']['quality'])
WIDTH = int( config['video']['width'])
HEIGHT = int( config['video']['height'])

# logging config values
logging.info('FPS: %s  Quality: %s  Width %s Height %s  Grayscale: %s', 
             str(FRAMES_PER_SECOND), str(JPEG_QUALITY), str(WIDTH), str(HEIGHT), GRAYSCALE)
logging.info('Drone ID: %s  Video Recipient: %s:%s', str(DRONE_ID), str(HOST_IP), str(VIDEO_PORT))

camera = None
# while loop will make sure our app continues to run
while(True):
    try:
        # setting up camera
        camera = PiCamera()
        camera.resolution = (WIDTH, HEIGHT)
        camera.framerate = FRAMES_PER_SECOND
        
        # array to capture data
        rawCapture = PiRGBArray(camera, size=(WIDTH, HEIGHT))
        
        # allowing time for next loop to connect and initialize
        time.sleep(0.1)
        
        logging.info("Camera module initiated")
        
        # create sockets
        # SOCK_DGRAM we create datagram which is UDP
        # we do not want TCP/IP protocol for this
        # if frame is lost thats fine
        # TCP will introduce additional latency because it guarantees every byte will be sent
        # FOR CONTROLS it is important but not here
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((HOST_IP, VIDEO_PORT))
        
        logging.info("Socket Opened, Video Streaming is started")
        
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            image_data = frame.array
            
            # rotate image because cam is mounded upside down
            image_data = cv2.rotate(image_data, cv2.ROTATE_180)
            
            # if network is slow grayscale will speed up
            if GRAYSCALE:
                image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
            
            # encoding into jpeg
            code, jpg_buffer = cv2.imencode(".jpg", image_data, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])

            # will combine drone id and frame into 1 message 
            # and now it can be sent over network as udp message
            datagramMsgBytes = Utils.create_datagram_message(DRONE_ID, jpg_buffer)

            #sending data
            video_socket.sendall(datagramMsgBytes)
            
            #clearing data for next iteration
            rawCapture.truncate(0)
        
    except Exception as e:
        logging.error("Video Stream Ended: " + str(e))
        
        # release the resource
        if camera != None:
            camera.close()