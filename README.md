#Libraries to install on raspi

sudo apt update

sudo apt install libhdf5-serial-dev
sudo apt install libatlas-base-dev
sudo apt install libjasper-dev
sudo apt install libqtgui4
sudo apt install libqt4-test
sudo apt install python3-opencv

sudo pip3 install netifaces psutil google-api-python-client 
                  wiringpi dronekit opencv-python

Create logs/ directory in the root app folder on Raspberry Pi (same place where app.py is located)

for the other project I had to install java jdk: https://adoptopenjdk.net/installation.html


droneapp.service is to make the app run as a service

Contact info: peter_black@angelic.com

FPS: 1  Quality: 60  Width 640 Height 480  Grayscale: False
360mb/h 5.5 - 7mb/m
336mb/h 56mb/10m
344mb/h 86mb/15m
340mb/h 170mb/30m

FPS: 1  Quality: 60  Width 640 Height 480  Grayscale: True
300mb/h 5mb/m
300mb/h 25mb/5m
336mb/h 56mb/10m
288mb/h 72mb/15m

720 & 1080 appear to have same FOV, 480 is reduced
13338 at Quality: 10  Width 640 Height 480  Grayscale: false
19590 at Quality: 60  Width 640 Height 480  Grayscale: True
21398 at Quality: 10  Width 1280 Height 720  Grayscale: True
34438 at Quality: 60  Width 640 Height 480  Grayscale: false
43826 at Quality: 10  Width 1920 Height 1080  Grayscale: True
48034 at Quality: 60  Width 1280 Height 720  Grayscale: True
50842 at Quality: 60  Width 1280 Height 720  Grayscale: True
92982 at Quality: 60  Width 1920 Height 1080  Grayscale: True
72394 at Quality: 90  Width 640 Height 480  Grayscale: false 640, and message is too long