sudo apt-get update --fix-missing -y && sudo apt-get upgrade -y
sudo apt install xrdp -y
sudo apt install libatlas-base-dev -y
sudo apt install flatpak -y
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
sudo flatpak install org.mobsya.ThymioSuite -y

#grants rights to usb ports
echo -e 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000a", MODE="0666"\nSUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000c", MODE="0666"' | sudo tee /etc/udev/rules.d/99-mobsya.rules
sudo udevadm control --reload-rules

#sets tdm to start on boot (this may not work nicely yet)
echo -e 'flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite \nexit 0' | sudo tee /etc/rc.local

sudo pip3 install tdmclient
sudo pip3 install opencv-python==4.5.3.56 #sudo pip3 install opencv-python-headless - for post dev use
sudo pip3 install -U numpy #installs older version of numpy

#tensoflow packages: https://www.tensorflow.org/lite/guide/python
#sudo pip3 install tflite-runtime

#pre-built object detection example: https://www.youtube.com/watch?v=mNjXEybFn98&list=PLQY2H8rRoyvz_anznBg6y3VhuSMcpN9oe
#sudo pip3 install tflite_support

#not fully tested yet(should do the same as following line):
sudo raspi-config nonint do_camera 0
#otherwise:
#replace camera_auto_detect=1 with start_x=1

#test camera:
#run test_camera.py
#if this doesnt work:
#libcamera-still -o /tmp/still-test.jpg (should not work due to legacy camera stack)
#to reduce pinkness for NoIR cameras
#awb_auto_is_greyworld=1

#test_camera.py dependency:
#sudo pip3 install climage

#optional lib for direct serial usb connection
#sudo pip3 install -y thymiodirect

#Test if tdm working
#flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite
#python -m tdmclient list

#TODO: add autostart to TDM
