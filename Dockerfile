FROM nvidia/cuda:10.2-base-ubuntu18.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

#  CUDA Libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-cudart-11-8 \
    cuda-cudart-dev-11-8 \
    libcublas-12-1 \
    libcublas-dev-12-1 \
    libcudnn8 \
    libcudnn8-dev

RUN apt-get update && apt-get install -y \
    libleptonica-dev \
    tesseract-ocr \
    libtesseract-dev \
    python3-pil \
    tesseract-ocr-eng \
    tesseract-ocr-script-latn \
    software-properties-common \
    git \
    curl \
    x11-xserver-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    sox

# Upgrade to Python 3.10
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update
RUN apt-get update && apt-get install -y python3.10 python-setuptools python3.10-distutils
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

RUN python3 -m pip install --upgrade pip setuptools wheel

# OpenCV takes a looong time to install, verbose so you can see progress
RUN python3 -m pip install opencv-python --verbose

# Install requirements here so code changes dont require reinstall
COPY --chown=apex requirements.txt .
RUN pip3 install -r requirements.txt

RUN python3 -m pip install paddlepaddle-gpu==2.5.0rc0

# Create non root user
RUN useradd -ms /bin/bash apex
USER apex
WORKDIR /home/apex

# Prefetch paddleOCR downloads
COPY --chown=apex cache_paddle.py /home/apex/
RUN python3 /home/apex/cache_paddle.py

# Copy program files
COPY --chown=apex ./apex_ocr /home/apex/apex-ocr/apex_ocr
ENV PYTHONPATH=/home/apex/apex-ocr:$PYTHONPATH

ENTRYPOINT [ "python3", "apex-ocr/apex_ocr/__main__.py" ]