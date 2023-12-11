from googleapiclient.discovery import build
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import os
import tempfile

def generate_thumbnail(video_content, width=230, height=130):
    try:
        # Create a temporary file on disk to store the video content
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_file.write(video_content)
        temp_video_file.close()

        # Create the video clip
        video = VideoFileClip(temp_video_file.name)
        thumbnail = video.get_frame(0)  # Get the first frame as the thumbnail
        video.close()

        # Resize the thumbnail to the desired dimensions
        thumbnail_pil = Image.fromarray(thumbnail)
        thumbnail_pil = thumbnail_pil.resize((width, height), resample=Image.LANCZOS)

        # Convert the thumbnail image to BytesIO
        thumbnail_io = BytesIO()
        thumbnail_pil.save(thumbnail_io, format='JPEG')

        thumbnail_io.seek(0)

        # Clean up the temporary file
        os.unlink(temp_video_file.name)

        return thumbnail_io

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


# image = get_youtube_thumbnail("https://www.youtube.com/watch?v=dyu0rBMO0kg")

# print(image)