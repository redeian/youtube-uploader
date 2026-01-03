# Setup Instructions

Complete guide to setting up and running the YouTube Video Uploader application.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Getting API Credentials](#getting-api-credentials)
4. [Running the Application](#running-the-application)
5. [First-Time Setup](#first-time-setup)
6. [Configuration](#configuration)

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.10 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Disk Space**: 500 MB for application + space for video files
- **Internet**: Stable internet connection for API calls and uploads

### Recommended Requirements

- **Python**: Version 3.11 or 3.12
- **RAM**: 8 GB or more
- **Disk Space**: 10 GB or more (for large video files)
- **Internet**: High-speed connection for faster uploads

## Installation

### Option 1: Using Startup Scripts (Recommended)

The easiest way to get started is to use the provided startup scripts.

#### Windows

1. Download or clone the repository
2. Navigate to the project directory
3. Double-click `start.bat`
4. The script will automatically:
   - Install `uv` package manager if not present
   - Create a virtual environment
   - Install all dependencies
   - Launch the application

#### macOS/Linux

1. Download or clone the repository
2. Navigate to the project directory
3. Make the script executable:
   ```bash
   chmod +x start.sh
   ```
4. Double-click `start.sh` or run:
   ```bash
   ./start.sh
   ```
5. The script will automatically:
   - Install `uv` package manager if not present
   - Create a virtual environment
   - Install all dependencies
   - Launch the application

### Option 2: Manual Installation

If you prefer to set up manually or encounter issues with the startup scripts:

#### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```bash
   python --version
   ```

#### Step 2: Install uv Package Manager

uv is a fast Python package installer.

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
```

#### Step 3: Create Virtual Environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
uv pip install -r requirements.txt
```

#### Step 5: Create Required Directories

```bash
# Create directories for tokens and logs
mkdir -p data/tokens logs
```

#### Step 6: Run the Application

```bash
streamlit run app.py
```

## Getting API Credentials

To use this application, you need to obtain OAuth 2.0 credentials from Google.

**Detailed instructions**: See [API Setup Guide](API_SETUP.md)

### Quick Summary

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Go to Credentials → Create Credentials → OAuth client ID
5. Select "Web application"
6. Add authorized redirect URI: `http://localhost:8501`
7. Copy Client ID and Client Secret

## Running the Application

### Using Startup Scripts

Simply double-click the appropriate startup script:
- Windows: `start.bat`
- macOS/Linux: `start.sh`

### Manual Execution

If you've set up manually:

```bash
# Activate virtual environment
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

# Run the application
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## First-Time Setup

### 1. Authenticate with YouTube

1. Open the application in your browser
2. In the sidebar, you'll see "API Credentials" section
3. Enter your YouTube API Client ID and Client Secret
4. Click "Login with YouTube"
5. A browser window will open asking for authorization
6. Review the permissions and click "Allow"
7. You'll be redirected back to the application
8. You should see "✅ Authenticated" in the sidebar

### 2. Test Your Connection

After authentication, the application will automatically:
- Test the connection to YouTube API
- Retrieve your channel information
- Display your channel name in the sidebar

### 3. Upload Your First Video

1. Click "Browse files" or drag and drop a video file
2. Enter a title for your video (required)
3. Optionally add description, tags, select category, and choose privacy status
4. Click "Upload Video"
5. Monitor the progress bar
6. Wait for upload to complete
7. You'll receive a confirmation with the video URL

## Configuration

### Default Settings

The application comes with sensible defaults:

- **Upload Chunk Size**: 5 MB
- **Retry Attempts**: 3
- **Max File Size**: 256 GB (YouTube limit)
- **Supported Formats**: MP4, MOV, AVI, FLV, WMV, WebM, MKV, MPEG, MPG

### Customizing Settings

Edit [`config.py`](../config.py:1) to customize:

```python
# Upload configuration
UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB chunks
MAX_FILE_SIZE = 256 * 1024 * 1024 * 1024  # 256 GB

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1.0  # seconds

# Logging configuration
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Streamlit Configuration

Edit [`.streamlit/config.toml`](../.streamlit/config.toml:1) to customize Streamlit settings:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"

[server]
port = 8501
headless = false
```

## Troubleshooting

### Common Issues

#### "uv: command not found"

**Solution**: Install uv using the commands in Step 2 above.

#### "Python version too old"

**Solution**: Install Python 3.10 or higher from [python.org](https://www.python.org/downloads/)

#### "Authentication failed"

**Solution**: 
- Verify your Client ID and Client Secret are correct
- Ensure the redirect URI is set to `http://localhost:8501`
- Check that YouTube Data API v3 is enabled in your Google Cloud Console

#### "Upload fails with quota error"

**Solution**: 
- You've exceeded your daily API quota
- Wait until the quota resets (usually 24 hours)
- Consider increasing your quota in Google Cloud Console

#### "File validation error"

**Solution**:
- Ensure the file is in a supported format
- Check that the file size is under 256 GB
- Verify the file is not corrupted

For more troubleshooting tips, see [Troubleshooting Guide](TROUBLESHOOTING.md).

## Next Steps

- Read the [API Setup Guide](API_SETUP.md) for detailed credential setup
- Check the [Troubleshooting Guide](TROUBLESHOOTING.md) if you encounter issues
- Review the [README.md](../README.md) for usage instructions
- Explore the [Implementation Plan](../plans/youtube-uploader-plan.md) for technical details

## Support

If you encounter any issues not covered in this guide:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review the application logs in `logs/youtube_uploader.log`
3. Open an issue on the project repository

## Security Notes

- Never share your Client ID and Client Secret
- Store credentials securely
- The application encrypts tokens before saving them
- Token files have restricted permissions (600)
- Clear credentials when done using the application

---

Happy uploading! 📹
