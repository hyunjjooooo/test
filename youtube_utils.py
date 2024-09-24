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

def get_youtube_transcript(url: str, languages=['ko', 'en']) -> str:
    try:
        url = convert_youtube_url(url)
        logger.info(f"Converted URL: {url}")
        video_id = url.split("v=")[1]
        
        # Try to load the video content using the YoutubeLoader
        try:
            logger.info("Attempting to get transcript using YoutubeLoader")
            loader = YoutubeLoader.from_youtube_url(url, add_video_info=True, languages=languages)
            content = loader.load()
            if content:
                logger.info("Successfully retrieved transcript using YoutubeLoader")
                return content[0].page_content
            else:
                logger.warning("YoutubeLoader returned empty content")
        except Exception as e:
            logger.error(f"Failed to get transcript using YoutubeLoader: {str(e)}")
        
        # If the loader fails, try to get the transcript using the YouTubeTranscriptApi
        logger.info("Attempting to get transcript using YouTubeTranscriptApi")
        try:
            # 사용 가능한 자막 목록 확인
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = [tr.language_code for tr in transcript_list]
            logger.info(f"Available transcripts: {available_languages}")
            
            # 요청한 언어의 자막 가져오기 시도
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    content = transcript.fetch()
                    logger.info(f"Successfully retrieved {lang} transcript for video ID: {video_id}")
                    return " ".join([entry['text'] for entry in content])
                except Exception as lang_e:
                    logger.warning(f"Failed to get {lang} transcript: {str(lang_e)}")
            
            # 요청한 언어로 실패한 경우, 자동 생성된 자막 시도
            try:
                transcript = transcript_list.find_generated_transcript(languages)
                content = transcript.fetch()
                logger.info(f"Retrieved auto-generated transcript for video ID: {video_id}")
                return " ".join([entry['text'] for entry in content])
            except Exception as gen_e:
                logger.warning(f"Failed to get auto-generated transcript: {str(gen_e)}")
            
            logger.error("No suitable transcript found")
        except Exception as e:
            logger.error(f"Failed to get transcript using YouTubeTranscriptApi: {str(e)}")
        
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_youtube_transcript: {str(e)}")
        return None

# 여기에 필요한 다른 함수들을 추가할 수 있습니다.
