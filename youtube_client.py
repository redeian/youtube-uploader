"""
YouTube API Client Wrapper.
Handles video uploads, metadata management, and progress tracking.
"""

import logging
import os
import time
from pathlib import Path
from typing import Callable, Dict, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

import config

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YouTubeClientError(Exception):
    """Base exception for YouTube client errors."""
    pass


class FileValidationError(YouTubeClientError):
    """Exception for file validation errors."""
    pass


class QuotaExceededError(YouTubeClientError):
    """Exception for API quota exceeded errors."""
    pass


class NetworkError(YouTubeClientError):
    """Exception for network-related errors."""
    pass


class UploadError(YouTubeClientError):
    """Exception for upload errors."""
    pass


class YouTubeClient:
    """
    Client for interacting with YouTube Data API v3.
    Handles video uploads with progress tracking and error handling.
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize YouTube client.
        
        Args:
            credentials: Authenticated OAuth credentials
        """
        self.credentials = credentials
        self.youtube = None
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize YouTube API service."""
        try:
            self.youtube = build(
                config.YOUTUBE_API_SERVICE_NAME,
                config.YOUTUBE_API_VERSION,
                credentials=self.credentials
            )
            logger.info("YouTube API service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube service: {str(e)}")
            raise YouTubeClientError(f"Failed to initialize YouTube service: {str(e)}")
    
    def validate_video_file(self, file_path: str) -> Dict[str, any]:
        """
        Validate video file before upload.
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dictionary with validation results
            
        Raises:
            FileValidationError: If file is invalid
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise FileValidationError(f"File not found: {file_path}")
        
        # Check if it's a file (not directory)
        if not path.is_file():
            raise FileValidationError(f"Path is not a file: {file_path}")
        
        # Check file extension
        if path.suffix.lower() not in config.SUPPORTED_VIDEO_FORMATS:
            raise FileValidationError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(config.SUPPORTED_VIDEO_FORMATS)}"
            )
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > config.MAX_FILE_SIZE:
            raise FileValidationError(
                f"File size ({file_size / (1024**3):.2f} GB) exceeds "
                f"YouTube's limit of {config.MAX_FILE_SIZE / (1024**3):.0f} GB"
            )
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            raise FileValidationError(f"File is not readable: {file_path}")
        
        logger.info(f"File validated successfully: {file_path}")
        
        return {
            'valid': True,
            'file_path': str(path.absolute()),
            'file_name': path.name,
            'file_size': file_size,
            'file_extension': path.suffix.lower()
        }
    
    def upload_video(
        self,
        file_path: str,
        metadata: Dict[str, any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, any]:
        """
        Upload video to YouTube with progress tracking.
        
        Args:
            file_path: Path to video file
            metadata: Video metadata (title, description, tags, category, privacy_status, thumbnail)
            progress_callback: Optional callback function for progress updates
                              Callback receives (bytes_uploaded, total_bytes)
        
        Returns:
            Dictionary with upload results including video ID
            
        Raises:
            FileValidationError: If file validation fails
            QuotaExceededError: If API quota is exceeded
            NetworkError: If network error occurs
            UploadError: If upload fails
        """
        # Validate file
        file_info = self.validate_video_file(file_path)
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': metadata.get('title', 'Untitled'),
                'description': metadata.get('description', ''),
                'tags': metadata.get('tags', []),
                'categoryId': metadata.get('category', '22'),  # Default: People & Blogs
                'defaultAudioLanguage': self._get_language_code(metadata.get('video_language', 'English'))
            },
            'status': {
                'privacyStatus': metadata.get('privacy_status', 'private'),
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Add recording details if recording date is provided
        if metadata.get('recording_date'):
            from datetime import datetime
            recording_date = metadata['recording_date']
            if isinstance(recording_date, str):
                recording_date = datetime.fromisoformat(recording_date)
            body['recordingDetails'] = {
                'recordingDate': recording_date.isoformat()
            }
        
        # Log altered content and paid promotion info (these cannot be set via API during upload)
        altered_content = metadata.get('altered_content', 'No')
        paid_promotion = metadata.get('paid_promotion', False)
        if altered_content != 'No' or paid_promotion:
            logger.info(f"Additional metadata - Altered Content: {altered_content}, Paid Promotion: {paid_promotion}")
            logger.info("Note: These fields need to be set manually in YouTube Studio after upload")
        
        logger.info(f"Starting upload: {file_info['file_name']}")
        
        # Handle thumbnail upload
        thumbnail_path = metadata.get('thumbnail')
        if thumbnail_path:
            logger.info(f"Thumbnail provided: {thumbnail_path}")
        
        try:
            # Create media upload object
            media = MediaFileUpload(
                file_path,
                chunksize=config.UPLOAD_CHUNK_SIZE,
                resumable=True
            )
            
            # Initialize upload request
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload with retry logic
            response = self._execute_upload_with_retry(
                request,
                media,
                progress_callback,
                file_info['file_size']
            )
            
            video_id = response.get('id', '')
            
            logger.info(f"Upload successful: Video ID = {video_id}")
            
            # Upload thumbnail if provided
            thumbnail_path = metadata.get('thumbnail')
            if thumbnail_path:
                try:
                    self._upload_thumbnail(video_id, thumbnail_path)
                    logger.info(f"Thumbnail uploaded successfully for video {video_id}")
                except Exception as e:
                    logger.warning(f"Failed to upload thumbnail: {str(e)}. Video uploaded without thumbnail.")
            
            return {
                'success': True,
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'title': metadata.get('title', 'Untitled'),
                'file_size': file_info['file_size']
            }
            
        except HttpError as e:
            error_details = self._parse_http_error(e)
            logger.error(f"HTTP error during upload: {error_details}")
            
            if error_details['error_type'] == 'quota_exceeded':
                raise QuotaExceededError(
                    f"API quota exceeded: {error_details['message']}"
                )
            else:
                raise UploadError(
                    f"Upload failed: {error_details['message']}"
                )
        
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            raise UploadError(f"Upload failed: {str(e)}")
    
    def _execute_upload_with_retry(
        self,
        request,
        media,
        progress_callback: Optional[Callable[[int, int], None]],
        total_bytes: int
    ) -> Dict[str, any]:
        """
        Execute upload with retry logic and progress tracking.
        
        Args:
            request: YouTube API upload request
            media: MediaFileUpload object
            progress_callback: Optional progress callback
            total_bytes: Total file size in bytes
            
        Returns:
            Upload response
            
        Raises:
            NetworkError: If network error occurs after retries
            UploadError: If upload fails
        """
        retry_count = 0
        last_exception = None
        
        while retry_count < config.MAX_RETRY_ATTEMPTS:
            try:
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    
                    if status:
                        # Update progress
                        bytes_uploaded = status.resumable_progress
                        if progress_callback:
                            progress_callback(bytes_uploaded, total_bytes)
                        
                        logger.debug(
                            f"Upload progress: {bytes_uploaded / total_bytes * 100:.1f}%"
                        )
                
                return response
            
            except Exception as e:
                last_exception = e
                retry_count += 1
                
                if retry_count >= config.MAX_RETRY_ATTEMPTS:
                    logger.error(f"Upload failed after {retry_count} attempts")
                    raise NetworkError(f"Upload failed after {retry_count} attempts: {str(e)}")
                
                # Calculate delay with exponential backoff
                delay = min(
                    config.RETRY_INITIAL_DELAY * (config.RETRY_BACKOFF_MULTIPLIER ** (retry_count - 1)),
                    config.RETRY_MAX_DELAY
                )
                
                logger.warning(
                    f"Upload attempt {retry_count} failed. Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
        
        raise NetworkError(f"Upload failed: {str(last_exception)}")
    
    def _get_language_code(self, language_name: str) -> str:
        """
        Convert language name to ISO 639-1 code.
        
        Args:
            language_name: Language name (e.g., "English", "Thai")
            
        Returns:
            ISO 639-1 language code (e.g., "en", "th")
        """
        language_map = {
            'English': 'en',
            'Thai': 'th',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Japanese': 'ja',
            'Korean': 'ko',
            'Chinese': 'zh',
            'Other': 'en'
        }
        return language_map.get(language_name, 'en')
    
    def _parse_http_error(self, error: HttpError) -> Dict[str, str]:
        """
        Parse HTTP error to determine error type and message.
        
        Args:
            error: HttpError from Google API
            
        Returns:
            Dictionary with error details
        """
        error_details = {
            'error_type': 'unknown',
            'message': str(error)
        }
        
        try:
            error_content = error.error_details[0] if error.error_details else {}
            error_reason = error_content.get('reason', '')
            
            if error_reason == 'quotaExceeded':
                error_details['error_type'] = 'quota_exceeded'
            elif error_reason == 'forbidden':
                error_details['error_type'] = 'forbidden'
            elif error_reason == 'invalidCredentials':
                error_details['error_type'] = 'authentication'
            
            error_details['message'] = error_content.get('message', str(error))
            
        except Exception:
            pass
        
        return error_details
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> None:
        """
        Upload a custom thumbnail for a video.
        
        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image file
            
        Raises:
            UploadError: If thumbnail upload fails
        """
        try:
            # Validate thumbnail file
            path = Path(thumbnail_path)
            if not path.exists():
                raise UploadError(f"Thumbnail file not found: {thumbnail_path}")
            
            # Check file extension
            if path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise UploadError(
                    f"Unsupported thumbnail format: {path.suffix}. "
                    f"Supported formats: JPG, JPEG, PNG, WEBP"
                )
            
            # Check file size (YouTube limit: 2MB)
            file_size = path.stat().st_size
            if file_size > 2 * 1024 * 1024:  # 2MB
                raise UploadError(
                    f"Thumbnail size ({file_size / (1024**2):.2f} MB) exceeds "
                    f"YouTube's limit of 2 MB"
                )
            
            # Create media upload object for thumbnail
            media = MediaFileUpload(
                thumbnail_path,
                mimetype='image/jpeg',  # YouTube accepts JPEG format
                resumable=False
            )
            
            # Set thumbnail
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            
            logger.info(f"Thumbnail uploaded successfully for video {video_id}")
        
        except HttpError as e:
            logger.error(f"HTTP error uploading thumbnail: {str(e)}")
            raise UploadError(f"Failed to upload thumbnail: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error uploading thumbnail: {str(e)}")
            raise UploadError(f"Failed to upload thumbnail: {str(e)}")
    
    def get_video_categories(self) -> Dict[str, str]:
        """
        Get available video categories from YouTube.
        
        Returns:
            Dictionary mapping category IDs to names
        """
        try:
            response = self.youtube.videoCategories().list(
                part='snippet',
                regionCode='US'
            ).execute()
            
            categories = {}
            for item in response.get('items', []):
                category_id = item['id']
                category_name = item['snippet']['title']
                categories[category_id] = category_name
            
            logger.info(f"Retrieved {len(categories)} video categories")
            return categories
            
        except HttpError as e:
            logger.error(f"Failed to get video categories: {str(e)}")
            # Return default categories if API call fails
            return config.VIDEO_CATEGORIES
    
    def get_upload_status(self, upload_url: str) -> Dict[str, any]:
        """
        Check status of an in-progress upload.
        
        Args:
            upload_url: Upload URL from resumable upload session
            
        Returns:
            Dictionary with upload status
        """
        # This would require tracking upload sessions separately
        # For now, return a placeholder
        return {
            'status': 'unknown',
            'bytes_uploaded': 0,
            'total_bytes': 0
        }
    
    def test_connection(self) -> bool:
        """
        Test connection to YouTube API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to fetch channel info to test connection
            response = self.youtube.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            channel_title = response['items'][0]['snippet']['title']
            logger.info(f"Connection test successful. Channel: {channel_title}")
            return True
            
        except HttpError as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_channel_info(self) -> Dict[str, any]:
        """
        Get information about the authenticated user's channel.
        
        Returns:
            Dictionary with channel information
        """
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if not response.get('items'):
                return {}
            
            channel = response['items'][0]
            
            return {
                'channel_id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet'].get('description', ''),
                'thumbnail': channel['snippet']['thumbnails']['default']['url'],
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'view_count': int(channel['statistics'].get('viewCount', 0))
            }
            
        except HttpError as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            return {}
