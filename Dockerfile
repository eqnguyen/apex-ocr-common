FROM nvidia/cuda:10.2-base-ubuntu18.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN apt-get update && apt-get install -y \
    python3-pip \
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
    libxext6

RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update
RUN apt-get update && apt-get install -y python3.10 python-setuptools python3.10-distutils
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install install paddlepaddle-gpu==2.4.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN python3 -m pip install --upgrade setuptools wheel

RUN python3 -m pip install opencv-python --verbose

RUN python3 -m pip install wheel \
    numpy \
    Pillow \
    pytesseract\
    regex \
    tqdm \
    click \
    protobuf \
    screeninfo

RUN python3 -m pip install pymupdf

RUN python3 -m pip install common dual tight data prox
RUN python3 -m pip install paddleocr

RUN useradd -ms /bin/bash apex
USER apex
WORKDIR /home/apex

COPY --chown=apex cache_paddle.py /home/apex/
RUN python3 /home/apex/cache_paddle.py

USER root
COPY --chown=apex requirements.txt .
RUN sed -i 's/\==.*//' requirements.txt
RUN pip3 install -r requirements.txt
USER apex

RUN mkdir data

COPY --chown=apex ./apex_ocr /home/apex/apex-ocr/apex_ocr
COPY --chown=apex setup.py /home/apex/apex-ocr
COPY --chown=apex README.md /home/apex/apex-ocr
COPY --chown=apex requirements.txt /home/apex/apex-ocr


USER root
RUN python3 -m pip install -e /home/apex/apex-ocr

USER apex


ENTRYPOINT [ "python3", "-m", "apex_ocr" ]