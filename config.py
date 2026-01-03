"""
Application configuration for YouTube Video Uploader.
Centralized settings for API, upload parameters, and paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
TOKENS_DIR = DATA_DIR / "tokens"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
TOKENS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# YouTube API configuration
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"

# OAuth 2.0 configuration
OAUTH_SCOPES = [
    YOUTUBE_UPLOAD_SCOPE,
    YOUTUBE_READ_WRITE_SCOPE,
]
OAUTH_PORT = int(os.getenv('OAUTH_PORT', '8080'))  # Port for OAuth local server (can be overridden via .env)
OAUTH_REDIRECT_URI = f"http://localhost:{OAUTH_PORT}"  # OAuth callback URI
OAUTH_TOKEN_FILE = TOKENS_DIR / "youtube_token.json"
OAUTH_ENCRYPTION_KEY_FILE = TOKENS_DIR / ".encryption_key"

# YouTube API credentials (from environment variables)
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID', '')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET', '')

# Google Generative AI API key (from environment variables)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Upload configuration
UPLOAD_CHUNK_SIZE = 20 * 1024 * 1024  # 20 MB chunks (increased from 5MB for better performance)
MAX_FILE_SIZE = 256 * 1024 * 1024 * 1024  # 256 GB (YouTube limit)
SUPPORTED_VIDEO_FORMATS = [
    ".mp4", ".mov", ".avi", ".flv", ".wmv", ".webm", ".mkv", ".mpeg", ".mpg"
]

# Connection optimization
UPLOAD_CONNECTION_TIMEOUT = 30  # seconds
UPLOAD_READ_TIMEOUT = 60  # seconds
UPLOAD_MAX_RETRIES = 5  # Increased from 3 for better reliability
UPLOAD_RETRY_BACKOFF = 1.5  # Reduced from 2.0 for faster retries
UPLOAD_RESUMABLE_THRESHOLD = 10 * 1024 * 1024  # 10MB - files larger than this will use resumable uploads

# Bandwidth throttling (bytes per second)
# Set to 0 to disable throttling (maximum speed)
UPLOAD_BANDWIDTH_LIMIT = 0  # Default: no limit (0 = unlimited)
# Example limits:
# 1 Mbps: 1 * 1024 * 1024
# 5 Mbps: 5 * 1024 * 1024
# 10 Mbps: 10 * 1024 * 1024

# Retry configuration
MAX_RETRY_ATTEMPTS = 5  # Increased for better reliability
RETRY_INITIAL_DELAY = 1.0  # seconds
RETRY_MAX_DELAY = 60.0  # seconds
RETRY_BACKOFF_MULTIPLIER = 1.5  # Reduced for faster retries

# Progress reporting
PROGRESS_UPDATE_INTERVAL = 0.1  # seconds

# Logging configuration
LOG_FILE = LOGS_DIR / "youtube_uploader.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Streamlit configuration
STREAMLIT_TITLE = "AI YouTube Uploader by Mark Digital"
STREAMLIT_PAGE_ICON = "📹"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_LOGO = "assets/logo.png"

# UI Messages
MSG_AUTH_SUCCESS = "✅ Successfully authenticated with YouTube!"
MSG_AUTH_FAILED = "❌ Authentication failed. Please check your credentials."
MSG_UPLOAD_SUCCESS = "✅ Video uploaded successfully!"
MSG_UPLOAD_FAILED = "❌ Upload failed. Please try again."
MSG_FILE_INVALID = "❌ Invalid file format. Please upload a video file."
MSG_FILE_TOO_LARGE = f"❌ File size exceeds YouTube's limit of {MAX_FILE_SIZE / (1024**3):.0f} GB."
MSG_QUOTA_EXCEEDED = "⚠️ API quota exceeded. Please try again later."
MSG_NETWORK_ERROR = "⚠️ Network error. Retrying..."

# Video categories (YouTube API category IDs)
VIDEO_CATEGORIES = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
    "30": "Movies",
    "31": "Anime/Animation",
    "32": "Action/Adventure",
    "33": "Classics",
    "34": "Comedy",
    "35": "Documentary",
    "36": "Drama",
    "37": "Family",
    "38": "Foreign",
    "39": "Horror",
    "40": "Sci-Fi/Fantasy",
    "41": "Thriller",
    "42": "Shorts",
    "43": "Shows",
    "44": "Trailers",
}

# Privacy status options
PRIVACY_STATUS_OPTIONS = ["public", "unlisted", "private"]
