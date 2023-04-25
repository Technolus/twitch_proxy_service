# Twitch Proxy Service
Proxy Service for Oculus Quest: re-encode Twitch content for compatibility with Oculus Quest devices

In this project, I am trying to create a proxy service for Twitch.tv.
The goal is to be able to watch Twitch.tv streams on VRChat running on Oculus Quest.

## The problem
The quest is not able to play twitch URLs directly.
It also is not able to process the M3U8 files that are used to stream twitch.

## Potential solution
The solution is to create a proxy service that will take the m3u8 file and re-encode it to a format that the quest can play.

## Work in progress
This project is still in development and is not yet functional.
This is the current state of the project:
The re-encoded stream plays for a few seconds (3-5) and then stops.
I am not sure why this is happening. Might be that the encoding is far too slow or that there is a problem with the re-encoded stream.

## How to run the service
```bash
docker build -t twitch_proxy_service .
docker run -p 80:80 twitch_proxy_service
```

## Some usefull commands for development
```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
# or
venv\Scripts\activate     # For Windows

pip-compile requirements.in
pip install -r requirements.txt
```
