import logging
from urllib.parse import urlparse, parse_qs
import re
from langchain_community.document_loaders import YoutubeLoader
from youtube_transcript_api import YouTubeTranscriptApi

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_youtube_url(shared_url):
    # Parse the URL
    parsed_url = urlparse(shared_url)
    
    # Check if it's already a standard YouTube URL
    if parsed_url.netloc in ('www.youtube.com', 'youtube.com') and parsed_url.path == '/watch':
        return shared_url  # Return as is if it's already a standard URL
    
    # Extract video ID
    if parsed_url.netloc == 'youtu.be':
        video_id = parsed_url.path.lstrip('/')
    elif parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    else:
        raise ValueError("Invalid YouTube URL")
    
    if not video_id:
        raise ValueError("Could not extract video ID")
    
    # Construct the original URL
    original_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Extract timestamp if present
    timestamp_match = re.search(r't=(\d+)', shared_url)
    if timestamp_match:
        timestamp = timestamp_match.group(1)
        original_url += f"&t={timestamp}s"
    
    return original_url

def get_youtube_transcript_api(url, languages=['ko', 'en']):
    video_id = url.split("v=")[1]
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        logger.error(f"YouTubeTranscriptApi를 통한 자막 가져오기 실패: {str(e)}")
        return None
    
def get_youtube_transcript(url: str) -> str:
    url = convert_youtube_url(url)
    logger.info(f"변환된 URL: {url}")
    
    # Try to load the video content using the YoutubeLoader
    try:
        logger.info("YoutubeLoader를 사용하여 자막 가져오기 시도")
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True, languages=['ko', 'en'])
        content = loader.load()
        logger.info("YoutubeLoader를 통해 자막 가져오기 성공")
        return content
    except Exception as e:
        logger.error(f"YoutubeLoader를 통한 자막 가져오기 실패: {str(e)}")
    
    # If the loader fails, try to get the transcript using the API
    logger.info("YouTubeTranscriptApi를 사용하여 자막 가져오기 시도")
    transcript = get_youtube_transcript_api(url)
    if transcript:
        logger.info("YouTubeTranscriptApi를 통해 자막 가져오기 성공")
        return transcript
    else:
        logger.error("모든 방법으로 자막 가져오기 실패")
        return None

def main():
    # Example usage
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    transcript = get_youtube_transcript(url)
    if transcript:
        print(transcript)
    else:
        print("Failed to retrieve transcript")

if __name__ == "__main__":
    main()
