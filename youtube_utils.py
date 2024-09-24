import logging
from urllib.parse import urlparse, parse_qs
import re
from langchain_community.document_loaders import YoutubeLoader
from youtube_transcript_api import YouTubeTranscriptApi

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# convert_youtube_url 함수는 그대로 유지

def get_youtube_transcript_api(url, languages=['ko', 'en']):
    try:
        video_id = url.split("v=")[1]
        logger.debug(f"Attempting to get transcript for video ID: {video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        logger.info(f"Successfully retrieved transcript using YouTubeTranscriptApi for video ID: {video_id}")
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        logger.error(f"Failed to get transcript using YouTubeTranscriptApi: {str(e)}")
        return None
    
def get_youtube_transcript(url: str) -> str:
    try:
        url = convert_youtube_url(url)
        logger.info(f"Converted URL: {url}")
        
        # Try to load the video content using the YoutubeLoader
        try:
            logger.info("Attempting to get transcript using YoutubeLoader")
            loader = YoutubeLoader.from_youtube_url(url, add_video_info=True, languages=['ko', 'en'])
            content = loader.load()
            logger.info("Successfully retrieved transcript using YoutubeLoader")
            return content[0].page_content if content else None
        except Exception as e:
            logger.error(f"Failed to get transcript using YoutubeLoader: {str(e)}")
        
        # If the loader fails, try to get the transcript using the API
        logger.info("Attempting to get transcript using YouTubeTranscriptApi")
        transcript = get_youtube_transcript_api(url)
        if transcript:
            logger.info("Successfully retrieved transcript using YouTubeTranscriptApi")
            return transcript
        else:
            logger.error("Failed to retrieve transcript using all methods")
            return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return None

# main 함수는 그대로 유지
