# YouTube Video Uploader 📹

A complete, production-ready Streamlit application for uploading local video files to YouTube using the YouTube Data API v3. Features OAuth 2.0 authentication with token persistence, real-time progress tracking, and comprehensive error handling.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- 🔐 **Secure OAuth 2.0 Authentication** - Authenticate with YouTube using OAuth 2.0 flow with encrypted token persistence
- 📤 **Easy Video Upload** - Upload videos to YouTube with a simple, intuitive interface
- 📊 **Real-time Progress Tracking** - Visual progress bar showing upload status
- 📝 **Complete Metadata Support** - Title, description, tags, category, and privacy status
- 🔄 **Automatic Token Refresh** - No need to re-authenticate every session
- ⚠️ **Comprehensive Error Handling** - Clear error messages for API quotas, invalid files, and network issues
- 🎨 **Polished UI** - Clean, modern interface with sidebar configuration
- 🚀 **One-Click Startup** - Double-click startup scripts for Windows and Unix/macOS
- 📦 **uv Package Manager** - Fast dependency management with uv
- 🔐 **Environment Configuration** - Secure credential management via `.env` file

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Internet connection
- YouTube API credentials (see [API Setup Guide](docs/API_SETUP.md))

### Installation

1. **Clone or download this repository**

2. **Run the startup script**

   - **Windows**: Double-click `start.bat`
   - **macOS/Linux**: Double-click `start.sh` or run `chmod +x start.sh && ./start.sh`

   The startup script will automatically:
   - Install `uv` package manager if not present
   - Create a virtual environment
   - Install all dependencies
   - Launch the application

3. **Authenticate with YouTube**

   - Enter your YouTube API Client ID and Client Secret in the sidebar
   - Click "Login with YouTube"
   - Authorize the application in your browser
   - Your credentials will be saved securely for future sessions

4. **Upload your video**

   - Select a video file from your computer
   - Enter video metadata (title, description, tags, category, privacy status)
   - Click "Upload Video"
   - Monitor the progress bar
   - Receive confirmation with video URL when complete

## 📁 Project Structure

```
youtube-helper/
├── app.py                          # Main Streamlit application
├── config.py                       # Application configuration
├── oauth_manager.py                # OAuth 2.0 authentication manager
├── youtube_client.py               # YouTube API client wrapper
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # uv project configuration
├── start.sh                        # Unix/macOS startup script
├── start.bat                       # Windows startup script
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── data/
│   └── tokens/                    # OAuth token storage (encrypted)
├── logs/
│   └── youtube_uploader.log      # Application logs
├── docs/
│   ├── SETUP.md                   # Setup instructions
│   ├── API_SETUP.md               # YouTube API setup guide
│   └── TROUBLESHOOTING.md         # Troubleshooting guide
├── plans/
│   └── youtube-uploader-plan.md   # Implementation plan
└── README.md                      # This file
```

## 🔑 Getting YouTube API Credentials

To use this application, you need to create a project in the Google Cloud Console and obtain OAuth 2.0 credentials.

**Detailed instructions**: See [API Setup Guide](docs/API_SETUP.md)

### Quick Overview

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Go to Credentials → Create Credentials → OAuth client ID
5. Select "Web application"
6. Add authorized redirect URI: `http://localhost:8501`
7. Copy Client ID and Client Secret

## 📖 Usage Guide

### Authentication

1. Open the application
2. Enter your Client ID and Client Secret in the sidebar
3. Click "Login with YouTube"
4. A browser window will open for authorization
5. Grant permissions to the application
6. You're now authenticated! Your credentials are saved securely

### Uploading a Video

1. Click "Browse files" or drag and drop a video file
2. Supported formats: MP4, MOV, AVI, FLV, WMV, WebM, MKV, MPEG, MPG
3. Maximum file size: 256 GB (YouTube limit)

### Video Metadata

- **Title** (required): A descriptive title for your video
- **Description** (optional): Detailed description of your content
- **Tags** (optional): Comma-separated keywords to help viewers find your video
- **Category** (optional): Select the category that best describes your video
- **Privacy Status**: Choose who can view your video
  - `public`: Anyone can find and view
  - `unlisted`: Anyone with the link can view
  - `private`: Only you can view

### Upload Process

1. Fill in the required metadata (at minimum: title)
2. Click "Upload Video"
3. Monitor the progress bar showing upload percentage
4. Wait for upload to complete
5. Receive confirmation with video URL

## 🔒 Security

- **Encrypted Token Storage**: OAuth tokens are encrypted using Fernet encryption
- **No Hardcoded Credentials**: Never store credentials in code
- **Secure File Permissions**: Token files have restricted permissions (600)
- **Session Management**: Clear credentials on logout
- **Input Validation**: All user inputs are validated and sanitized

## ⚙️ Configuration

Edit [`config.py`](config.py:1) to customize:

- Upload chunk size
- Retry attempts and delays
- File size limits
- Supported video formats
- Logging configuration
- UI messages

## 🐛 Troubleshooting

Having issues? Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for solutions to common problems.

Common issues:
- Authentication fails
- Upload gets stuck
- File validation errors
- API quota exceeded
- Network errors

## 📝 Development

### Setting Up Development Environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Install development dependencies (optional)
uv pip install pytest black flake8 mypy
```

### Running the Application

```bash
streamlit run app.py
```

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black .

# Lint code
flake8 .

# Type check
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues, questions, or suggestions, please open an issue on the project repository.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Web application framework
- [Google APIs](https://developers.google.com/youtube/v3) - YouTube Data API
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

## 📚 Documentation

- [Setup Instructions](docs/SETUP.md) - Detailed setup guide
- [API Setup Guide](docs/API_SETUP.md) - YouTube API credentials setup
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Implementation Plan](plans/youtube-uploader-plan.md) - Technical architecture and design

## 🎯 Roadmap

Future enhancements:
- [ ] Batch upload multiple videos
- [ ] Video thumbnail upload
- [ ] Upload scheduling
- [ ] Video management (edit, delete)
- [ ] Analytics dashboard
- [ ] Support for live streaming
- [ ] Custom thumbnails
- [ ] Video chapters
- [ ] Subtitle/caption upload

---

Made with ❤️ using Streamlit and Python
