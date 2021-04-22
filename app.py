import logging, time, argparse, configparser

# Part-06 Python - How to Run it as a Linux Service
# the above video shows that the .service file has to be moved in the raspi
parser = argparse.ArgumentParser()
# if no --d parameter is passed in, the it was started from console, if it is then started as a service
parser.add_argument('--d', nargs=1, default=None)
args = parser.parse_args()

APP_DIR = args.d[0] if args.d != None else "./"

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
VIDEO_PORT = int( config['cloud-app']['video-port'])

GRAYSCALE = config['video']['grayscale'].lower() == 'true'
FRAMES_PER_SECOND = int( config['video']['fps'])
JPEG_QUALITY = int( config['video']['quality'])
WIDTH = int( config['video']['width'])
HEIGHT = int( config['video']['height'])
 
if __name__ == '__main__':
    logging.debug('DroneApp has started! Directory %s', APP_DIR)
    
    # logging config values
    logging.info('FPS: %s  Quality: %s  Width %s Height %s  Grayscale: %s', 
                  str(FRAMES_PER_SECOND), str(JPEG_QUALITY), str(WIDTH), str(HEIGHT), GRAYSCALE)
     logging.info('Drone ID: %s  Video Recipient: %s:%s', str(DRONE_ID), str(HOST_IP), str(VIDEO_PORT))