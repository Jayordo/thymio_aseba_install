#new install (not working I guess)

# sudo apt full-upgrade
# sudo apt install xrdp -y
# sudo apt install flatpak -y
# sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
# sudo flatpack install org.mobsya.ThymioSuite -y

#creates file to grant permission for usb device I think?

# echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000a", MODE="0666"' | sudo tee -a /etc/udev/rules.d/99-mobsya.rules
# echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0617", ATTRS{idProduct}=="000c", MODE="0666"' | sudo tee -a /etc/udev/rules.d/99-mobsya.rules
# sudo udevadm control --reload-rules

#run from terminal or rdp
#flatpak run org.mobsya.ThymioSuite
#flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite #test this

# old install, for reference
# sudo apt-get update

sudo apt-get install -y \
    mesa-common-dev \
    libgl1-mesa-dev \
    clang clang-format \
    build-essential \
    gdb \
    git \
    cmake \
    ninja-build \
    libavahi-compat-libdnssd-dev \
    libudev-dev \
    libssl-dev \
    libfreetype6 \
    libfontconfig \
    libnss3 libasound2 libxtst6 libxrender1 libxi6 libxcursor1 libxcomposite1 \
    qttools5-dev-tools \
    qttools5-dev \
    qtbase5-dev \
    qt5-qmake \
    libqt5help5 \
    libqt5opengl5-dev \
    libqt5svg5-dev \
    libqt5x11extras5-dev \
    libqwt-qt5-dev \
    libqt5charts5-dev \
	qtdeclarative5-dev \
    g++-multilib
#libqt5webengine5 

cd ~/
git clone --recursive https://github.com/mobsya/aseba.git
cd aseba

# mkdir build && cd build
# cmake -DMOBSYA_WEBAPPS_ROOT_DIR=share/ -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF ..
# make
