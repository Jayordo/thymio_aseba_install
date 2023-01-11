sudo apt-get update

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
# g++-multilib \

cd ~/
git clone --recursive https://github.com/mobsya/aseba.git
cd aseba

mkdir build && cd build
cmake  -DMOBSYA_WEBAPPS_ROOT_DIR=share/ -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF ..
make
