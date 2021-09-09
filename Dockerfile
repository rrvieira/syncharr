# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim-buster

EXPOSE 6766

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
  && apt-get update -q \
  && apt-get install -qy swig ffmpeg libsphinxbase-dev gcc automake autoconf libasound2-dev python3-dev python3-pip build-essential swig git libpulse-dev libtool bison swig libavutil-dev libswscale-dev python3-dev libpulse-dev libpocketsphinx-dev libavformat-dev libswresample-dev libavdevice-dev libavfilter-dev python3-pocketsphinx \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install pocketsphinx ffsubsync==0.4.16
RUN git clone -b '0.16' https://github.com/sc0ty/subsync.git

WORKDIR /subsync
RUN cp subsync/config.py.template subsync/config.py
RUN mkdir -p /root/.config/subsync/
RUN pip3 install .

COPY . /syncharr
WORKDIR /syncharr
RUN pip3 install -r requirements.txt
RUN mv syncharr.ini.docker syncharr.ini

ENV COLUMNS='640'

CMD ["gunicorn", "--bind", "0.0.0.0:6766", "webapp.webapp:app", "--timeout 90"]
