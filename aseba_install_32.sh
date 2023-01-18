Install instructions:

sudo apt full-upgrade -y

sudo apt install xrdp -y
sudo apt install flatpak -y
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
sudo flatpak install org.mobsya.ThymioSuite -y

pip install --upgrade -y tdmclient
pip install -y opencv-python
#optional
#pip install -y thymiodirect

echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000a", MODE="0666"' | sudo tee -a /etc/udev/rules.d/99-mobsya.rules
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000c", MODE="0666"' | sudo tee -a /etc/udev/rules.d/99-mobsya.rules
sudo udevadm control --reload-rules

#Test if its working
#flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite
#python3 -m tdmclient list

#https://raspberrypi-guide.github.io/programming/install-opencv.html
#dunno how much of this is needed
#sudo apt-get install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev libhdf5-serial-dev libhdf5-103 python3-pyqt5 python3-dev -y
#pip install opencv-python

#TODO: add autostart to TDM