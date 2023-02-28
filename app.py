#Inport all the libraries needed
import cv2
import numpy as np
import urllib
from PIL import Image
from io import BytesIO
from gtts import gTTS
from moviepy.editor import *
import os
import random
import praw
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

#This function use reddit API to get the meme's information
def get_data():
    reddit = praw.Reddit(
        client_id='R-oUGTprEw0vapxKVnxrSw',
        client_secret='If0E9QLZ40s3u5VIk9cGrGOWeDRP5g',
        user_agent='GAMemes',
    ) 
    subreddit = reddit.subreddit('memes')
    top_post = random.choice(list(subreddit.top('day', limit=50)))
    title = top_post.title
    image_url = top_post.url
    return title, image_url
title, image_url = get_data()

#This function creates the actual Video
def create_video(title, image_url):
    # Load image from URL and resize it to 1080x1920
    with urllib.request.urlopen(image_url) as url:
        image_data = url.read()
    image = Image.open(BytesIO(image_data))
    image = image.resize((1080, 1920))
    # Convert PIL image to OpenCV image
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # Create black background with 9:16 aspect ratio
    width = 1080
    height = 1920
    background = np.zeros((height, width, 3), dtype=np.uint8)
    # Add image to the background
    x_offset = int((width - image.shape[1]) / 2)
    y_offset = int((height - image.shape[0]) / 2)
    background[y_offset:y_offset+image.shape[0], x_offset:x_offset+image.shape[1]] = image
    # Add text to the background
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = title
    font_scale = 3.0 # increase font size to 2.0
    thickness = 10 # increase thickness to 3
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = int((width - text_size[0]) / 2)
    y = int(100)
    max_width = 200
    cv2.putText(background, text, (x, y), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA, max_width)
    # Create video writer with H.264 codec and 30 FPS
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    fps = 1
    video_writer = cv2.VideoWriter('video.mp4', fourcc, fps, (width, height))
    # Write each frame to the video writer
    for i in range(5):
        video_writer.write(background)
    # Release video writer and close OpenCV windows
    video_writer.release()
    cv2.destroyAllWindows()

#This function creates the voice over audio
def create_audio():
    tts = gTTS(title)
    tts.save('audio.mp3')

#this function combines both the video and audio
def combine(audio_path, video_path, output_path):
    vc = VideoFileClip("video.mp4")
    ac = AudioFileClip("audio.mp3")
    op = vc.set_audio(ac)
    op.write_videofile("output.mp4")

# Define the scopes needed for the YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# This function to publish the video to YouTube
def upload(video_path, title, description):
    # Authenticate the user and get the credentials
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    credentials = flow.run_local_server(port=0)
    # Create a YouTube service object
    youtube = build("youtube", "v3", credentials=credentials)
    # Upload the video to YouTube
    request_body = {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": "public"},
    }
    response = (
        youtube.videos()
        .insert(part="snippet,status", body=request_body, media_body=video_path)
        .execute()
    )
    # Return the video ID
    return response["id"]

#This code block executes the functions one by one
get_data()
create_video(title, image_url)
create_audio()
combine("audio.mp3", "video.mp4", "output.mp4")
upload("output.mp4", title+" #shorts #funny #memes", "#shorts #funny #memes #humor #comedy #entertainment #viral #popular #hilarious #jokes #laughs #amusing #satire #parody #irony Sub to the channel to get daily juicy memes")