import subprocess
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
import requests
import m3u8
import aioredis
import asyncio
import asyncio.subprocess
import yt_dlp
import ffmpeg 
import io
import httpx
import os
from io import BytesIO

REENCODE_STREAM = True

redis = None
app = FastAPI()

# Add an on_startup event to initialize Redis when the application starts
@app.on_event("startup")
async def startup():
    await init_redis()

# Initialize Redis connection
async def init_redis():
    global redis
    REDIS_HOST = 'redis'
    REDIS_PORT = 6379
    redis = await aioredis.create_redis_pool(f"redis://{REDIS_HOST}:{REDIS_PORT}")


@app.get("/")
def read_root():
    return {"status": "online"}

@app.head("/health")
def read_root():
    return {}

@app.get("/stream/{channel_name}")
async def stream_channel(channel_name: str):
    global REENCODE_STREAM
    stream_url = await get_stream_url(channel_name)
    if not stream_url:
        raise HTTPException(status_code=404, detail="Unable to fetch stream")

    # Use a Redis key based on the channel name for caching the modified playlist
    redis_key = f"twitch_proxy:playlist:{channel_name}"

    # Try to get the modified playlist from Redis
    modified_playlist = await redis.get(redis_key)

    # If the modified playlist is not in the cache, fetch it and store it in Redis
    if not modified_playlist:
        async with httpx.AsyncClient() as client:
            response = await client.get(stream_url)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Unable to fetch stream")

        playlist = m3u8.loads(response.content.decode("utf-8"))
        for segment in playlist.segments:
               segment.uri = f"/stream/{channel_name}/segments/{segment.uri.split('/')[-1]}"

        modified_playlist = playlist.dumps()

        # Store the modified playlist in Redis with an expiration time (e.g., 60 seconds)
        await redis.setex(redis_key, 10, modified_playlist)

    return Response(content=modified_playlist, media_type="application/x-mpegurl")



@app.get("/stream/{channel_name}/segments/{segment_name}")
async def stream_segment(channel_name: str, segment_name: str):
    global REENCODE_STREAM

    stream_url = await get_stream_url(channel_name)
    if not stream_url:
        raise HTTPException(status_code=404, detail="Unable to fetch stream")

    response = requests.get(stream_url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Unable to fetch stream")

    playlist = m3u8.loads(response.content.decode("utf-8"))

    # Find the base URL from the first segment's URI
    first_segment = playlist.segments[0]
    base_url = first_segment.uri.rsplit("/", 1)[0]

    segment_url = f"{base_url}/{segment_name}"

    # Use a Redis key based on the segment URL
    redis_key = f"twitch_proxy:{segment_url}"

    # Try to get the segment data from Redis
    segment_data = await redis.get(redis_key)

    # If the data is not in the cache, fetch it and store it in Redis
    if not segment_data:
        async with httpx.AsyncClient() as client:
            response = await client.get(segment_url)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Unable to fetch segment")

        segment_data = response.content

        # Reencode the segment data if True
        if REENCODE_STREAM:
            # Replace the temporary file creation with BytesIO buffers
            input_buffer = BytesIO(segment_data)
            output_buffer = BytesIO()

            # Modify the input and output file arguments in the ffmpeg command
            try:
                process = (
                    ffmpeg.input("pipe:0", format="mpegts")
                    .output(
                        "pipe:1",
                        format = "mpegts",
                        vcodec="libx264",
                        preset="ultrafast",
                        crf="51", # 51 is the worst quality, 0 is the best, 23-28 is the default for twitch
                        acodec="aac",
                        strict="experimental",
                    )
                    .global_args("-hide_banner", "-loglevel", "error")
                    .compile()
                )

                process = subprocess.Popen(process, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                output_buffer, _ = process.communicate(input=input_buffer.getvalue())
                process.wait()
            except Exception as e:
                print(f"Error reencoding stream: {e}")
                return None

            # Assign the output buffer's content to segment_data
            segment_data = output_buffer

    # Store the segment data in Redis with an expiration time (e.g., 60 seconds)
    await redis.setex(redis_key, 30, segment_data)
    print(len(segment_data))
    return Response(content=segment_data, media_type="video/MP2T")


async def get_stream_url(channel_name: str) -> str:
    # Use a Redis key based on the channel name for caching the stream URL
    redis_key = f"twitch_proxy:stream_url:{channel_name}"
    
    # Try to get the stream URL from Redis
    stream_url = await redis.get(redis_key)

    # If the stream URL is not in the cache, fetch it and store it in Redis
    if not stream_url:
        ydl_opts = {
            "format": "best[height<=360]",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(f"https://www.twitch.tv/{channel_name}", download=False)
                stream_url = info_dict.get("url", None)
                
                if stream_url:
                    # Store the stream URL in Redis with an expiration time (e.g., 60 seconds)
                    await redis.setex(redis_key, 20, stream_url.encode())

            except Exception as e:
                print(f"Error fetching stream: {e}")
                return None
    else:
        # Decode the stream URL from bytes to string
        stream_url = stream_url.decode()

    return stream_url
