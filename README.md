# Drone - Drone software
This repo contains the software that runs on the rasberry pi that controls the drone. It communicates over the internet with the java UI.

## Libraries to install on raspi

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
