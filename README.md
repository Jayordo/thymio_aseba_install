# How to

## On your desktop
1. Download raspberry pi imager from: https://www.raspberrypi.com/software/
2. Insert sd in PC and run Raspberry Pi Imager
3. Choose default Raspberry pi os (32-bit). In my current case it's Debian Bullseye with desktop from 2022-09-22.
4. Select storage, your sd card.
5. Go to settings and enable SSH with password authentication, setup a username and password. Press save.
6. Press write, wait for it to finish and stick it in the raspberry.
7. Find the Pi's ipadress, and ssh to it.

## On the Pi
1. Run the following lines:
```sh
cd ~/Documents
git clone https://github.com/Jayordo/thymio_aseba_install
cd thymio_aseba_install
. aseba_install_32.sh
```
2. Once it's done you can test if it's working by running:
```sh
flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite
python3 -m tdmclient list
```
You should see the info of your Thymio, you might need to reconnect the usb cable for it to work.
4. To test the main functions run the test_scripts, if blink.py doesn't work the Thymio might need a firmware update. 
Which can be done through the Thymio suite app(which possibly requires X, so you might need to rdp to it)
