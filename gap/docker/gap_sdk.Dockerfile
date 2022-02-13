FROM ubuntu:20.04
#FROM gap:base
SHELL ["/bin/bash", "-c"] MAINTAINER csamplawski@cs.umass.edu

RUN apt-get update 

RUN DEBIAN_FRONTEND=noninteractive TZ="America/New_York" apt-get -y install tzdata

#from gap_sdk repo
RUN apt-get install -y \
    autoconf \
    automake \
    bison \
    build-essential \
    cmake \
    curl \
    doxygen \
    flex \
    git \
    graphicsmagick-libmagick-dev-compat \
    gtkwave \
    libftdi-dev \
    libftdi1 \
    libjpeg-dev \
    libsdl2-dev \
    libsdl2-ttf-dev \
    libsndfile1-dev \
    libtool \
    libusb-1.0-0-dev \
    pkg-config \
    python3-pip \
    rsync \
    scons \
    texinfo \
    tmux \
    udev \
    vim \
    wget

#python -> python3
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

#versions from nntool requirements.txt
#needed for future pip install to work
RUN pip install numpy==1.19.5 cython==0.29.21 

WORKDIR "/root/"
RUN git clone https://github.com/GreenWaves-Technologies/gap8_openocd.git
WORKDIR "/root/gap8_openocd"
RUN ./bootstrap
RUN ./configure --program-prefix=gap8- --prefix=/usr --datarootdir=/usr/share/gap8-openocd
RUN make -j 4
RUN make -j 4 install
RUN cp /usr/share/gap8-openocd/openocd/contrib/60-openocd.rules /etc/udev/rules.d
#RUN udevadm control --reload-rules && udevadm trigger
RUN usermod -a -G dialout root
WORKDIR "/root/"

RUN git clone https://github.com/GreenWaves-Technologies/gap_riscv_toolchain_ubuntu_18.git
WORKDIR "/root/gap_riscv_toolchain_ubuntu_18"
RUN ./install.sh /usr/lib/gap_riscv_toolchain 
WORKDIR "/root/"

RUN git clone https://github.com/GreenWaves-Technologies/gap_sdk.git
WORKDIR "/root/gap_sdk"
RUN touch .tiler_url
RUN echo "https://greenwaves-technologies.com/autotiler/" >> .tiler_url
#RUN apt-get -y install libblas3 liblapack3 liblapack-dev libblas-dev
#RUN apt-get -y install gfortran 
#RUN pip install -r tools/nntool/requirements.txt
RUN pip install -r requirements.txt
ENV TILER_LICENSE_AGREED="TILER_LICENSE_AGREED"
RUN source configs/gapuino_v2.sh && make -j 4 all
WORKDIR "/root/"
RUN echo "source /root/gap_sdk/configs/gapuino_v2.sh" >> /root/.bashrc

RUN git clone https://github.com/GreenWaves-Technologies/image_classification_networks.git
WORKDIR "/root/image_classification_networks/"
RUN ./models/download_models.sh
WORKDIR "/root/"

RUN pip install pyserial
#RUN . gap_sdk/configs/gapuino_v2.sh

#SHELL ["/bin/bash", "-c", "source /gap_sdk/configs/gapuino_v2.sh"]
#RUN pip install numpy --upgrade

#RUN touch 90-ftdi_gapuino.rules
#RUN echo 'ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", MODE="0666", GROUP="dialout"'> 90-ftdi_gapuino.rules
#RUN echo 'ATTRS{idVendor}=="15ba", ATTRS{idProduct}=="002b", MODE="0666", GROUP="dialout"'>> 90-ftdi_gapuino.rules
#RUN mv 90-ftdi_gapuino.rules /etc/udev/rules.d/

