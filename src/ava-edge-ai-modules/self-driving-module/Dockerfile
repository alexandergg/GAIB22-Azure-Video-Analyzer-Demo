FROM python:3.8-slim-buster

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends syslog-ng

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff-tools \
    i2c-tools \
    libsm6 \
    libxext6 \
    libwebp-dev \
    libpng16-16 \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libqtgui4 \
    libqt4-test 

RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y wget runit nginx

RUN apt-get update -y && \
    apt-get install -y libnginx-mod-nchan

COPY conf/app.conf /etc/nginx/sites-available

RUN apt-get clean

COPY app /app/

EXPOSE 80

COPY conf/app.sh /app.sh
RUN chmod +x app.sh
RUN bash app.sh

CMD ["runsvdir","/var/runit"]

