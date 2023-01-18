## How to:

#On your desktop
1. Download raspberry pi imager from: https://www.raspberrypi.com/software/
2. Insert sd in PC and run Raspberry Pi Imager
3. Choose default Raspberry pi os (32-bit). In my current case it's Debian Bullseye with desktop from 2022-09-22.
4. Select storage, your sd card.
5. Go to settings and enable SSH with password authentication, setup a username and password. Press save.
6. Press write, wait for it to finish and stick it in the raspberry.
7. Find the Pi's ipadress, and ssh to it.

#On the pi
Run the following lines:
cd ~/Documents
git clone https://github.com/Jayordo/thymio_aseba_install
cd thymio_aseba_install
