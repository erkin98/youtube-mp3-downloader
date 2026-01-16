import os
from pathlib import Path
from pytube import YouTube, Search
from pytube.exceptions import RegexMatchError, VideoUnavailable
import logging

logger = logging.getLogger(__name__)

class YouTubeService:
    @staticmethod
    def download_audio(url_str: str, output_path: Path | str | None = None) -> str:
        """
        Downloads audio from a YouTube URL.
        
        Args:
            url_str: The YouTube video URL.
            output_path: Directory to save the file.
            
        Returns:
            The path to the downloaded file.
            
        Raises:
            ValueError: If the URL is invalid.
            Exception: For other errors.
        """
        try:
            yt = YouTube(url_str)
            audio = yt.streams.filter(
                mime_type="audio/mp4", abr="48kbps", only_audio=True
            ).first()
            
            if not audio:
                # Fallback to any audio stream if specific one not found
                audio = yt.streams.filter(only_audio=True).first()
                if not audio:
                    raise ValueError("No audio stream found")

            # Clean filename to avoid filesystem issues
            # Remove characters that might be problematic in filenames
            safe_title = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
            filename = f"{safe_title}.mp3"
            
            file_path = audio.download(output_path=str(output_path) if output_path else None, filename=filename)
            return file_path
            
        except RegexMatchError:
            logger.error(f"Invalid YouTube URL: {url_str}")
            raise ValueError("Invalid YouTube URL")
        except VideoUnavailable:
            logger.error(f"Video unavailable: {url_str}")
            raise ValueError("Video is unavailable")
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise e

    @staticmethod
    def search_and_download_audio(query: str, output_path: Path | str | None = None) -> str:
        """
        Searches for a video and downloads the audio of the first result.
        """
        s = Search(query)
        if not s.results:
            raise ValueError("No results found")
        
        yt = s.results[0]
        return YouTubeService.download_audio(yt.watch_url, output_path)
