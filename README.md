# Twitch Proxy Service
Proxy Service for Oculus Quest: re-encode Twitch content for compatibility with Oculus Quest devices

In this project, I aim to create a proxy service for Twitch.tv that enables watching Twitch streams on VRChat running on Oculus Quest.

## The problem
The Oculus Quest cannot play Twitch URLs directly nor process the M3U8 files used for streaming on Twitch.

## Proposed Solution
The proposed solution involves creating a proxy service that takes the M3U8 file and re-encodes it into a format compatible with the Oculus Quest.

## Current Progress
This project is a work in progress and has not yet reached full functionality. The current state of the project is as follows:
The re-encoded stream plays for a brief period (3-5 seconds) before stopping. The cause of this issue remains uncertain — it could be due to slow encoding or an issue with the re-encoded stream itself.
Note: I have temporarily paused development on this project due to other commitments and limited progress. However, anyone interested in continuing from where I left off is welcome to do so.

## Potential Dead End
It appears that the player does not connect to the segment URLs at all. Therefore, addressing the issue may require starting with the player itself and implementing an alternate mechanism in Udon to parse the file. However, it's worth noting that Udon does not currently support the creation of VRCUrls on the fly, which further complicates the development of a solution.


## How to run the service
```bash
docker build -t twitch_proxy_service .
docker run -p 80:80 twitch_proxy_service
```
Once the service is running, you can access the stream via the following URL:
```
http://localhost/stream/{channelname}
``` 


## Useful Commands for Development
```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
# or
venv\Scripts\activate     # For Windows

pip-compile requirements.in
pip install -r requirements.txt
```
