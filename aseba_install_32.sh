#Install instructions:

sudo apt-get update --fix-missing -y && sudo apt-get upgrade -y
sudo apt install xrdp -y
sudo apt install libatlas-base-dev -y
sudo apt install flatpak -y
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
sudo flatpak install org.mobsya.ThymioSuite -y

echo -e 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000a", MODE="0666"\nSUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000c", MODE="0666"' | sudo tee /etc/udev/rules.d/99-mobsya.rules
sudo udevadm control --reload-rules

#sets tdm to start on boot
echo -e 'flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite \nexit 0' | sudo tee /etc/rc.local

sudo pip3 install tdmclient
sudo pip3 install opencv-python==4.5.3.56
#sudo pip3 install opencv-python-headless #for post dev use
sudo pip3 install -U numpy
#some camera dependencies
#sudo pip3 install matplotlib
#add some thing to enable raspi-config hardware camera support
#sudo pip3 install climage


#optional lib for direct serial usb connection
#sudo pip3 install -y thymiodirect

#Test if its working
#flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite
#python -m tdmclient list

#TODO: add autostart to TDM
