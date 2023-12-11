from googleapiclient.discovery import build
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
from django.core.files.base import ContentFile

def generate_thumbnail(video_file):
    try:
        video = VideoFileClip(video_file.path)
        thumbnail_path = os.path.join(os.path.dirname(video_file.path), "thumbnail.jpg")
        thumbnail = video.get_frame(0)  # Get the first frame as the thumbnail
        thumbnail_content = ContentFile(thumbnail.tobytes())
        video.close()

        with open(thumbnail_path, "wb") as thumbnail_file:
            thumbnail_file.write(thumbnail_content.read())

        return thumbnail_path

    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None


def get_youtube_thumbnail(youtube_link):
    # Extract the video ID from the YouTube link
    video_id = youtube_link.split('?v=')[-1]
    
    # Initialize the YouTube Data API client
    youtube = build('youtube', 'v3', developerKey='AIzaSyD16IpqqSa99jDwvNmpP8CgmTrzbuqba78')
    
    # Retrieve video details
    video_details = youtube.videos().list(part='snippet', id=video_id).execute()

    # print(video_details)
    
    # Get the URL of the default video thumbnail
    if 'items' in video_details and len(video_details['items']) > 0:
        thumbnail_url = video_details['items'][0]['snippet']['thumbnails']['maxres']['url']
        return thumbnail_url
    return None


