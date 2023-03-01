# syncharr

Syncharr is a tool distributed in a docker image that provides a HTTP Server to receive subtitles synchronization requests for a given video file.

The requests are dispatched in a "first come, first served basis" to an external subtitles synchronization tool. The result of each synchronization request can then be shared via a notification client.

Currently the following external synch tools are supported:
- [sc0ty/subsync](https://github.com/sc0ty/subsync)
- [smacke/ffsubsync](https://github.com/smacke/ffsubsync)

And for the delivery of notifications:
- [Telegram](https://telegram.org/)

## Goal

syncharr was implemented with the idea of being integrated and used together with [morpheus65535/bazarr](https://github.com/morpheus65535/bazarr). Bazarr already provides an embedded automatic synchronization tool but has some limitations. 

Some highlights of synchar:
- Being able to select which tool to be used or to have fallback synch tools when one of them fails;
- Send a notification with the synch result;
- Guarantee that each synch request is perfomed one at a time;
- Detailed logs.

Also, syncharr was implemented in a standalone docker image instead of bundling bazarr:
- to allow to receive bazarr container updates as soon as they are available;
- to easily integrate it in other environments/other tools;
- to be able to specify a docker cpu throttle just for syncharr container - as subtitle synchronization can be a heavy task at times.

**Notice**: syncharr is hosted by the Python WSGI HTTP Server: [Gunicorn](https://gunicorn.org/). It is not behind any HTTP proxy server, so its use outside of a local network of your trust is not advised.

## Synch Result Notification - Demo

### Telegram

<p float="left">
  <img width=310 src="https://i.imgur.com/nfKPPOU.png">
  <img width=310 src="https://i.imgur.com/OVN9D5w.png">
</p>

# Usage

Here are some example snippets to show how one can get started creating a container.

## Starting the container

### docker-compose

`docker-compose.yml`
```yaml
version: "2.4"

services:
  syncharr:
    container_name: syncharr
    image: rrvieir4/syncharr:latest
    restart: always
    networks:
      - servarr
    ports:
      - "6766:6766"
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Lisbon
      - SYNC_TOOLS=["sc0ty/subsync", "smacke/ffsubsync"]
      - SYNC_WINDOW_SIZE_SETTING=120
      - SYNC_VERBOSE_SETTING=2
      - TELEGRAM_USER_TOKEN=<your telegram user token>
      - TELEGRAM_CHAT_ID=<your telegram chat id>
    volumes:
      - /your/path/to/syncharr/data:/syncharr-data
      - /your/path/to/your/media:/media
```

Launch:
```console
docker-compose --file docker-compose.yml up -d --remove-orphans
```

### docker cli

```console
docker run -d \
  --name=syncharr \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Europe/Lisbon \
  -e SYNC_TOOLS='["sc0ty/subsync", "smacke/ffsubsync"]' \
  -e SYNC_WINDOW_SIZE_SETTING=120 \
  -e SYNC_VERBOSE_SETTING=2 \
  -e TELEGRAM_USER_TOKEN=<your telegram user token> \
  -e TELEGRAM_CHAT_ID=<your telegram chat id> \
  -p 6766:6766 \
  -v /your/path/to/syncharr/data:/syncharr-data \
  -v /your/path/to/your/media:/media \
  --restart unless-stopped \
  rrvieir4/syncharr:latest
```

### Parameters

| Name                     | Is Optional? | Default                                 | Description                                                                                                                                                                                                                                                                                        |
|--------------------------|--------------|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SYNC_TOOLS               | Yes          | `["sc0ty/subsync", "smacke/ffsubsync"]` | Ordered list with the IDs of the external tools that will be used to try to synchronize subtitles. Current supported tools -> name: [sc0ty/subsync](https://github.com/sc0ty/subsync), id: `sc0ty/subsync`; name: [smacke/ffsubsync](https://github.com/smacke/ffsubsync), id: `smacke/ffsubsync`. |
| SYNC_WINDOW_SIZE_SETTING | Yes          | `120`                                   | Max subtitle synch correction (in seconds)                                                                                                                                                                                                                                                         |
| SYNC_VERBOSE_SETTING     | Yes          | `2`                                     | Verbosity level (0 - 3), higher number means more data will be printed                                                                                                                                                                                                                             |
| TELEGRAM_USER_TOKEN      | Yes          |                                         | Your telegram user token. If none, no notification is sent                                                                                                                                                                                                                                         |
| TELEGRAM_CHAT_ID         | Yes          |                                         | Your telegram chat id. If none, no notification is sent                                                                                                                                                                                                                                            |

## REST API

#### Add a new sync request to the queue

- **GET** `/sync-request?sub=/path/sub.srt&media=/path/video.mkv&synchedSub=/path/sub-synched.srt`
  - `sub`: path to the subtitles that will be synchronized
  - `media`: path to the video file that will be used as reference to synchronize the subtitles
  - `synchedSub`: path to write the synchronized subtitles file.. if has the same path as the `sub`, the latter file is overriden.
  
#### See the log file

- **GET** `/sync-request/log`

## Bazarr integration

In Bazarr, go to the menu:

Settings > Subtitles

and make sure that the 'Custom Post-Processing' option is checked. 

Then add as 'command':
```console
curl -G -v "http://<your syncharr address>:6766/sync-request" --data-urlencode sub={{subtitles}} --data-urlencode media={{episode}} --data-urlencode synchedSub={{subtitles}}
```

Make sure to replace `<your syncharr address>` by the actual syncharr address.
