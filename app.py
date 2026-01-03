"""
YouTube Video Uploader - Streamlit Application
A complete application for uploading videos to YouTube with OAuth 2.0 authentication.
"""

import logging
import time
from pathlib import Path
from typing import Optional

import streamlit as st
from google.oauth2.credentials import Credentials

import config
from oauth_manager import OAuthManager, AuthenticationError
from youtube_client import (
    YouTubeClient,
    FileValidationError,
    QuotaExceededError,
    NetworkError,
    UploadError
)
from ai_metadata_generator import AIMetadataGenerator

# Check if credentials are configured in environment
CREDENTIALS_CONFIGURED = bool(config.YOUTUBE_CLIENT_ID and config.YOUTUBE_CLIENT_SECRET)

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

# Page configuration
st.set_page_config(
    page_title=config.STREAMLIT_TITLE,
    page_icon=config.STREAMLIT_PAGE_ICON,
    layout=config.STREAMLIT_LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'oauth_manager' not in st.session_state:
        st.session_state.oauth_manager = None
    if 'youtube_client' not in st.session_state:
        st.session_state.youtube_client = None
    if 'channel_info' not in st.session_state:
        st.session_state.channel_info = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'upload_progress' not in st.session_state:
        st.session_state.upload_progress = 0
    if 'upload_complete' not in st.session_state:
        st.session_state.upload_complete = False
    if 'upload_result' not in st.session_state:
        st.session_state.upload_result = None
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None
    if 'success_message' not in st.session_state:
        st.session_state.success_message = None
    if 'upload_clicked' not in st.session_state:
        st.session_state.upload_clicked = False
    if 'thumbnail_file' not in st.session_state:
        st.session_state.thumbnail_file = None


def render_sidebar():
    """Render the sidebar with API credentials and authentication."""
    st.sidebar.title("⚙️ Settings")
    
    # API Credentials Section
    st.sidebar.header("🔑 API Credentials")
    
    # Use environment variables if available, otherwise allow manual input
    if CREDENTIALS_CONFIGURED:
        client_id = config.YOUTUBE_CLIENT_ID
        client_secret = config.YOUTUBE_CLIENT_SECRET
        st.sidebar.info("✅ Credentials loaded from .env file")
    else:
        client_id = st.sidebar.text_input(
            "Client ID",
            type="password",
            help="Enter your YouTube OAuth 2.0 Client ID",
            key="client_id"
        )
        
        client_secret = st.sidebar.text_input(
            "Client Secret",
            type="password",
            help="Enter your YouTube OAuth 2.0 Client Secret",
            key="client_secret"
        )
    
    st.sidebar.markdown("---")
    
    # Authentication Section
    st.sidebar.header("🔐 Authentication")
    
    # Check if credentials are provided
    if client_id and client_secret:
        # Initialize OAuth manager if not already done
        if st.session_state.oauth_manager is None:
            st.session_state.oauth_manager = OAuthManager(client_id, client_secret)
        
        # Check authentication status
        if st.session_state.oauth_manager.is_authenticated():
            st.session_state.authenticated = True
            st.sidebar.success("✅ Authenticated")
            
            # Reinitialize YouTube client if needed
            if st.session_state.youtube_client is None:
                credentials = st.session_state.oauth_manager.get_credentials()
                if credentials:
                    st.session_state.youtube_client = YouTubeClient(credentials)
                    # Get channel info if not available
                    if st.session_state.channel_info is None:
                        st.session_state.channel_info = st.session_state.youtube_client.get_channel_info()
            
            # Show channel info if available
            if st.session_state.channel_info:
                st.sidebar.info(f"Channel: {st.session_state.channel_info['title']}")
            
            # Logout button
            if st.sidebar.button("Logout", key="logout_btn"):
                st.session_state.oauth_manager.clear_credentials()
                st.session_state.authenticated = False
                st.session_state.youtube_client = None
                st.session_state.channel_info = None
                st.session_state.success_message = "Logged out successfully"
                st.rerun()
        else:
            st.session_state.authenticated = False
            st.sidebar.warning("⚠️ Not authenticated")
            
            # Login button
            if st.sidebar.button("Login with YouTube", key="login_btn"):
                try:
                    with st.spinner("Authenticating..."):
                        credentials = st.session_state.oauth_manager.authenticate()
                        st.session_state.authenticated = True
                        
                        # Initialize YouTube client
                        st.session_state.youtube_client = YouTubeClient(credentials)
                        
                        # Get channel info
                        st.session_state.channel_info = st.session_state.youtube_client.get_channel_info()
                        
                        st.session_state.success_message = config.MSG_AUTH_SUCCESS
                        st.rerun()
                
                except AuthenticationError as e:
                    st.session_state.error_message = f"{config.MSG_AUTH_FAILED}\n\n{str(e)}"
                    st.rerun()
                except Exception as e:
                    st.session_state.error_message = f"Authentication error: {str(e)}"
                    st.rerun()
    else:
        st.session_state.authenticated = False
        st.sidebar.info("Please enter your API credentials to continue")
    
    st.sidebar.markdown("---")
    
    # Help Section
    st.sidebar.header("❓ Help")
    if st.sidebar.button("How to get API credentials"):
        st.sidebar.markdown("""
        **To get YouTube API credentials:**
        
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select existing one
        3. Enable YouTube Data API v3
        4. Go to Credentials → Create Credentials → OAuth client ID
        5. Select "Web application"
        6. Add authorized redirect URI: `http://localhost:8080`
        7. Copy Client ID and Client Secret
        
        **Using .env file (Recommended):**
        
        1. Copy `.env.example` to `.env`
        2. Fill in your credentials in `.env`
        3. Restart the application
        
        For detailed instructions, see the documentation.
        """)


def render_main_interface():
    """Render the main interface for video upload."""
    st.markdown('<h1 class="main-header">📹 YouTube Video Uploader</h1>', unsafe_allow_html=True)
    
    # Show success/error messages
    if st.session_state.success_message:
        st.markdown(f'<div class="success-box">{st.session_state.success_message}</div>', unsafe_allow_html=True)
        st.session_state.success_message = None
    
    if st.session_state.error_message:
        st.markdown(f'<div class="error-box">{st.session_state.error_message}</div>', unsafe_allow_html=True)
        st.session_state.error_message = None
    
    # Check if authenticated
    if not st.session_state.authenticated:
        st.info("🔐 Please authenticate with YouTube in the sidebar to continue.")
        return
    
    # Show upload result if available
    if st.session_state.upload_complete and st.session_state.upload_result:
        render_upload_success()
        return
    
    # Video Upload Section
    st.header("📤 Upload Video")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Select a video file",
        type=[ext[1:] for ext in config.SUPPORTED_VIDEO_FORMATS],
        help=f"Supported formats: {', '.join(config.SUPPORTED_VIDEO_FORMATS)}",
        key="video_uploader"
    )
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_file_path = Path(f"temp_{uploaded_file.name}")
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.uploaded_file = str(temp_file_path)
        
        # Show file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{len(uploaded_file.getbuffer()) / (1024**2):.2f} MB")
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        st.markdown("---")
        
        # Thumbnail Upload Section
        st.header("🖼️ Thumbnail")
        
        thumbnail_file = st.file_uploader(
            "Upload Custom Thumbnail",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload a custom thumbnail for your video (JPG, PNG, or WEBP format)",
            key="thumbnail_uploader"
        )
        
        if thumbnail_file:
            # Save thumbnail temporarily
            temp_thumbnail_path = Path(f"temp_thumbnail_{thumbnail_file.name}")
            with open(temp_thumbnail_path, "wb") as f:
                f.write(thumbnail_file.getbuffer())
            
            st.session_state.thumbnail_file = str(temp_thumbnail_path)
            
            # Display thumbnail preview
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(temp_thumbnail_path, caption="Thumbnail Preview", width=200)
            with col2:
                st.metric("File Name", thumbnail_file.name)
                st.metric("File Size", f"{len(thumbnail_file.getbuffer()) / (1024**2):.2f} MB")
        
        st.markdown("---")
        
        # AI Metadata Generation Section
        st.header("🤖 AI-Powered Metadata Generation")
        
        # Video context for AI
        video_context = st.text_area(
            "Video Content Context",
            placeholder="Describe your video content, topic, or main points (e.g., 'A tutorial about Python programming for beginners covering variables, loops, and functions')",
            help="Provide a brief description of your video content to generate optimized title and description",
            key="video_context",
            height=100
        )
        
        # Generate AI Metadata button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 Tip: The more detailed your video context, the better the AI-generated metadata will be.")
        with col2:
            generate_ai_button = st.button(
                "✨ Generate with AI",
                type="primary",
                use_container_width=True,
                key="generate_ai_btn"
            )
        
        # Handle AI generation
        if generate_ai_button and video_context:
            if not config.GEMINI_API_KEY:
                st.error("❌ Google Generative AI API key not configured. Please add GEMINI_API_KEY to your .env file.")
            else:
                try:
                    with st.spinner("🤖 Generating optimized metadata with AI..."):
                        # Get current values
                        current_category = st.session_state.get('video_category', 'Education')
                        current_tags = st.session_state.get('video_tags', 'AI')
                        current_language = st.session_state.get('video_language', 'Thai')
                        
                        # Initialize AI generator
                        ai_generator = AIMetadataGenerator()
                        
                        # Generate metadata
                        ai_result = ai_generator.generate_metadata(
                            video_context=video_context,
                            video_language=current_language,
                            category=current_category,
                            tags=current_tags
                        )
                        
                        # Update session state with AI-generated values
                        st.session_state.video_title = ai_result['title']
                        st.session_state.video_description = ai_result['description']
                        
                        # Merge AI-generated tags with existing tags
                        if ai_result['tags']:
                            existing_tags = [tag.strip() for tag in current_tags.split(',') if tag.strip()]
                            ai_tags = [tag.strip() for tag in ai_result['tags'].split(',') if tag.strip()]
                            merged_tags = list(set(existing_tags + ai_tags))
                            st.session_state.video_tags = ', '.join(merged_tags)
                        
                        st.success("✅ AI-generated metadata applied successfully!")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Failed to generate AI metadata: {str(e)}")
                    logger.error(f"AI metadata generation error: {str(e)}", exc_info=True)
        
        st.markdown("---")
        
        # Metadata Section
        st.header("� Video Metadata")
        
        # Title
        title = st.text_input(
            "Title *",
            value=uploaded_file.name.rsplit('.', 1)[0],
            help="Enter a descriptive title for your video",
            key="video_title"
        )
        
        # Description
        description = st.text_area(
            "Description",
            placeholder="Enter a description for your video...",
            help="Provide details about your video content",
            key="video_description",
            height=150
        )
        
        # Tags
        tags_input = st.text_input(
            "Tags",
            value="AI",
            placeholder="Enter tags separated by commas (e.g., tutorial, python, programming)",
            help="Add relevant tags to help viewers find your video",
            key="video_tags"
        )
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
        
        # Category
        category = st.selectbox(
            "Category",
            options=list(config.VIDEO_CATEGORIES.values()),
            index=14,  # Default to "Education"
            help="Select the category that best describes your video",
            key="video_category"
        )
        category_id = next(
            (k for k, v in config.VIDEO_CATEGORIES.items() if v == category),
            "22"
        )
        
        # Privacy Status
        privacy_status = st.selectbox(
            "Privacy Status",
            options=config.PRIVACY_STATUS_OPTIONS,
            index=2,  # Default to "private"
            help="Choose who can view your video",
            key="privacy_status"
        )
        
        st.markdown("---")
        
        # Additional Settings
        st.header("⚙️ Additional Settings")
        
        # Recording Date
        from datetime import datetime
        recording_date = st.date_input(
            "Recording Date",
            value=datetime.now().date(),
            help="The date when the video was recorded",
            key="recording_date"
        )
        
        # Video Language
        video_language = st.selectbox(
            "Video Language",
            options=["English", "Thai", "Spanish", "French", "German", "Japanese", "Korean", "Chinese", "Other"],
            index=1,  # Default to "Thai"
            help="The primary language of the video",
            key="video_language"
        )
        
        # Altered Content
        altered_content = st.selectbox(
            "Altered Content - Do any of the following describe your content?",
            options=["No", "Yes - Contains altered content", "Yes - Contains synthetic content", "Yes - Contains generative AI content"],
            index=0,  # Default to "No"
            help="Select if your content contains altered, synthetic, or generative AI content",
            key="altered_content"
        )
        
        # Paid Promotion
        paid_promotion = st.checkbox(
            "Paid Promotion",
            value=False,
            help="Check if this video contains paid promotion or sponsored content",
            key="paid_promotion"
        )
        
        # Metadata summary
        with st.expander("📋 Metadata Summary"):
            summary_data = {
                "title": title,
                "description": description[:100] + "..." if len(description) > 100 else description,
                "tags": tags,
                "category": category,
                "category_id": category_id,
                "privacy_status": privacy_status,
                "recording_date": str(recording_date),
                "video_language": video_language,
                "altered_content": altered_content,
                "paid_promotion": paid_promotion
            }
            if st.session_state.thumbnail_file:
                summary_data["thumbnail"] = "Custom thumbnail uploaded"
            st.json(summary_data)
        
        st.markdown("---")
        
        # Upload Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            upload_button = st.button(
                "🚀 Upload Video",
                type="primary",
                use_container_width=True,
                disabled=not title,
                key="upload_btn"
            )
        
        if upload_button:
            if not title:
                st.error("Please enter a title for your video")
            else:
                # Start upload
                st.session_state.upload_complete = False
                st.session_state.upload_progress = 0
                st.session_state.upload_clicked = True
                st.rerun()
    else:
        st.info("📁 Please select a video file to upload")


def render_upload_success():
    """Render the upload success screen."""
    result = st.session_state.upload_result
    
    st.header("✅ Upload Successful!")
    
    # Success message
    st.markdown(f'<div class="success-box">{config.MSG_UPLOAD_SUCCESS}</div>', unsafe_allow_html=True)
    
    # Video details
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Video Information")
        st.write(f"**Title:** {result['title']}")
        st.write(f"**Video ID:** {result['video_id']}")
        st.write(f"**File Size:** {result['file_size'] / (1024**2):.2f} MB")
    
    with col2:
        st.subheader("Links")
        st.markdown(f"""
        - **Watch on YouTube:** [{result['video_url']}]({result['video_url']})
        - **Video ID:** `{result['video_id']}`
        """)
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Upload Another Video", key="upload_another_btn"):
        st.session_state.upload_complete = False
        st.session_state.upload_result = None
        st.session_state.uploaded_file = None
        st.session_state.upload_progress = 0
        
        # Clean up temp files
        if st.session_state.uploaded_file:
            temp_file = Path(st.session_state.uploaded_file)
            if temp_file.exists():
                temp_file.unlink()
        
        # Clean up thumbnail file
        if st.session_state.thumbnail_file:
            temp_thumbnail = Path(st.session_state.thumbnail_file)
            if temp_thumbnail.exists():
                temp_thumbnail.unlink()
            st.session_state.thumbnail_file = None
        
        st.rerun()


def handle_upload():
    """Handle the video upload process with progress tracking."""
    if not st.session_state.uploaded_file:
        return
    
    # Check if YouTube client is initialized
    if not st.session_state.youtube_client:
        st.session_state.error_message = "YouTube client not initialized. Please authenticate again."
        st.session_state.upload_clicked = False
        st.rerun()
        return
    
    # Get metadata from session state
    metadata = {
        'title': st.session_state.get('video_title', 'Untitled'),
        'description': st.session_state.get('video_description', ''),
        'tags': [tag.strip() for tag in st.session_state.get('video_tags', '').split(',') if tag.strip()],
        'category': st.session_state.get('video_category_id', '22'),
        'privacy_status': st.session_state.get('privacy_status', 'private'),
        'recording_date': st.session_state.get('recording_date'),
        'video_language': st.session_state.get('video_language'),
        'altered_content': st.session_state.get('altered_content'),
        'paid_promotion': st.session_state.get('paid_promotion', False),
        'thumbnail': st.session_state.get('thumbnail_file')
    }
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Progress callback
    def progress_callback(bytes_uploaded: int, total_bytes: int):
        progress = bytes_uploaded / total_bytes
        st.session_state.upload_progress = progress
        progress_bar.progress(progress)
        status_text.text(f"Uploading... {progress * 100:.1f}% ({bytes_uploaded / (1024**2):.1f} MB / {total_bytes / (1024**2):.1f} MB)")
    
    try:
        # Perform upload
        result = st.session_state.youtube_client.upload_video(
            st.session_state.uploaded_file,
            metadata,
            progress_callback
        )
        
        # Update progress to 100%
        progress_bar.progress(1.0)
        status_text.text("Upload complete!")
        
        # Store result
        st.session_state.upload_result = result
        st.session_state.upload_complete = True
        st.session_state.success_message = config.MSG_UPLOAD_SUCCESS
        st.session_state.upload_clicked = False  # Reset the flag
        
        # Clean up temp files
        temp_file = Path(st.session_state.uploaded_file)
        if temp_file.exists():
            temp_file.unlink()
        
        # Clean up thumbnail file
        if st.session_state.thumbnail_file:
            temp_thumbnail = Path(st.session_state.thumbnail_file)
            if temp_thumbnail.exists():
                temp_thumbnail.unlink()
            st.session_state.thumbnail_file = None
        
        st.rerun()
    
    except FileValidationError as e:
        st.session_state.error_message = f"{config.MSG_FILE_INVALID}\n\n{str(e)}"
        st.session_state.upload_clicked = False  # Reset the flag
        st.rerun()
    
    except QuotaExceededError as e:
        st.session_state.error_message = f"{config.MSG_QUOTA_EXCEEDED}\n\n{str(e)}"
        st.session_state.upload_clicked = False  # Reset the flag
        st.rerun()
    
    except NetworkError as e:
        st.session_state.error_message = f"{config.MSG_NETWORK_ERROR}\n\n{str(e)}"
        st.session_state.upload_clicked = False  # Reset the flag
        st.rerun()
    
    except UploadError as e:
        st.session_state.error_message = f"{config.MSG_UPLOAD_FAILED}\n\n{str(e)}"
        st.session_state.upload_clicked = False  # Reset the flag
        st.rerun()
    
    except Exception as e:
        st.session_state.error_message = f"Unexpected error: {str(e)}"
        st.session_state.upload_clicked = False  # Reset the flag
        logger.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
        st.rerun()


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main interface
    render_main_interface()
    
    # Handle upload if triggered
    if st.session_state.uploaded_file and not st.session_state.upload_complete:
        if st.session_state.upload_clicked:
            st.session_state.upload_clicked = False  # Reset the flag
            handle_upload()


if __name__ == "__main__":
    main()
