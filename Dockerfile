# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim-buster

EXPOSE 6766

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
  && apt-get update -q \
  && apt-get install -qy swig ffmpeg libsphinxbase-dev gcc automake autoconf libasound2-dev python3-dev python3-pip build-essential swig git libpulse-dev libtool bison swig libavutil-dev libswscale-dev python3-dev libpulse-dev libpocketsphinx-dev libavformat-dev libswresample-dev libavdevice-dev libavfilter-dev python3-pocketsphinx \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install pocketsphinx

RUN git clone -b '0.16' https://github.com/sc0ty/subsync.git

WORKDIR /subsync

RUN cp subsync/config.py.template subsync/config.py
RUN sed -i '/wxPython==4.0.6/d' ./requirements.txt
RUN pip3 install -r requirements.txt

RUN python3 setup.py build
RUN python3 setup.py install

# Install pip requirements
WORKDIR /syncharr

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /syncharr
RUN mv /syncharr/syncharr.ini.docker /syncharr/syncharr.ini

CMD ["./run.sh"]
