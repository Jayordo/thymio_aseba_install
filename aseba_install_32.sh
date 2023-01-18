#Install instructions:

sudo apt install xrdp -y
sudo apt install flatpak -y
sudo apt install python3-opencv -y
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
sudo flatpak install org.mobsya.ThymioSuite -y
#requirements for opencv?
#sudo apt install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev libhdf5-serial-dev libhdf5-103 python3-pyqt5 python3-dev -y

sudo apt update --fix-missing -y && apt upgrade -y
#mb dont do this, it takes too long
#sudo apt full-upgrade

sudo pip3 install tdmclient

#TODO: test if above reqs make the -i command unnecessary
#the link extracts a pre-built wheel which improves install speed massively

#sudo pip3 install opencv-python

#After developing the robots, the UI-less version can be used because this one takes loooong
#sudo pip3 install opencv-python-headless

#optional lib for direct serial usb connection
#sudo pip3 install -y thymiodirect

#TODO: test if this is needed
#echo -e 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000a", MODE="0666"\nSUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000c", MODE="0666"' | sudo tee /etc/udev/rules.d/99-mobsya.rules
#sudo udevadm control --reload-rules

#Test if its working
#flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite
#python -m tdmclient list

#TODO: add autostart to TDM
