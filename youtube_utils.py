from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.document_loaders import YoutubeLoader
import logging

logger = logging.getLogger(__name__)

def convert_youtube_url(url):
    parsed_url = urlparse(url)
    
    if parsed_url.netloc in ('youtu.be', 'www.youtu.be'):
        video_id = parsed_url.path.lstrip('/')
    elif 'youtube.com' in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get('v', [None])[0]
    else:
        raise ValueError("Invalid YouTube URL")
    
    if not video_id:
        raise ValueError("Could not extract video ID")
    
    return f"https://www.youtube.com/watch?v={video_id}"

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import logging

logger = logging.getLogger(__name__)

def get_youtube_transcript(url: str, languages=['ko', 'en']) -> str:
    try:
        url = convert_youtube_url(url)
        logger.info(f"Converted URL: {url}")
        video_id = url.split("v=")[1]
        logger.info(f"Extracted video ID: {video_id}")
        
        # Try to load the video content using the YoutubeLoader
        try:
            logger.info("Attempting to get transcript using YoutubeLoader")
            loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
            content = loader.load()
            if content:
                logger.info("Successfully retrieved transcript using YoutubeLoader")
                return content[0].page_content
            else:
                logger.warning("YoutubeLoader returned empty content")
        except Exception as e:
            logger.error(f"Failed to get transcript using YoutubeLoader: {str(e)}", exc_info=True)
        
        # If the loader fails, try to get the transcript using the YouTubeTranscriptApi
        logger.info("Attempting to get transcript using YouTubeTranscriptApi")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            if transcript:
                logger.info(f"Successfully retrieved transcript for video ID: {video_id}")
                return " ".join([entry['text'] for entry in transcript])
            else:
                logger.warning("YouTubeTranscriptApi returned empty transcript")
        except TranscriptsDisabled:
            logger.error("Transcripts are disabled for this video")
        except NoTranscriptFound:
            logger.error("No transcript found for the specified languages")
        except Exception as e:
            logger.error(f"Failed to get transcript using YouTubeTranscriptApi: {str(e)}", exc_info=True)
        
        # If all methods fail, try to list available transcripts
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = [tr.language_code for tr in transcript_list]
            logger.info(f"Available transcripts: {available_languages}")
        except Exception as e:
            logger.error(f"Failed to list available transcripts: {str(e)}", exc_info=True)
        
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_youtube_transcript: {str(e)}", exc_info=True)
        return None
