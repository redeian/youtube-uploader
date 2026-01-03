# Troubleshooting Guide

Common issues and solutions for the YouTube Video Uploader application.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Authentication Issues](#authentication-issues)
3. [Upload Issues](#upload-issues)
4. [File Issues](#file-issues)
5. [Network Issues](#network-issues)
6. [API Quota Issues](#api-quota-issues)
7. [Performance Issues](#performance-issues)
8. [Getting Help](#getting-help)

## Installation Issues

### "uv: command not found"

**Problem**: The `uv` package manager is not installed or not in your PATH.

**Solutions**:

1. **Install uv**:
   - **Windows (PowerShell)**:
     ```powershell
     powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - **macOS/Linux**:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```

2. **Add uv to PATH**:
   - **Windows**: Add `$HOME\.local\bin` to your PATH
   - **macOS/Linux**: Add `$HOME/.local/bin` to your PATH in `~/.bashrc` or `~/.zshrc`:
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     ```

3. **Restart your terminal** after adding to PATH.

### "Python version too old"

**Problem**: Python version is less than 3.10.

**Solutions**:

1. **Install Python 3.10+**:
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Verify installation**:
   ```bash
   python --version
   ```

3. **If multiple Python versions**:
   - Use `python3.10` or `python3.11` explicitly
   - Update the startup script to use the correct Python version

### "Failed to create virtual environment"

**Problem**: Virtual environment creation fails.

**Solutions**:

1. **Check Python installation**:
   ```bash
   python --version
   ```

2. **Try creating manually**:
   ```bash
   python -m venv .venv
   ```

3. **Check permissions**:
   - Ensure you have write permissions in the directory
   - Try running with administrator/sudo privileges

4. **On Windows**, ensure Windows Defender isn't blocking the operation.

### "Module not found" errors

**Problem**: Import errors when running the application.

**Solutions**:

1. **Ensure virtual environment is activated**:
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`

2. **Reinstall dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Check Python version**:
   ```bash
   python --version
   ```

4. **Clear pip cache and reinstall**:
   ```bash
   pip cache purge
   uv pip install -r requirements.txt --no-cache-dir
   ```

## Authentication Issues

### "Authentication failed"

**Problem**: OAuth authentication fails.

**Solutions**:

1. **Verify credentials**:
   - Check Client ID and Client Secret are correct
   - Ensure no extra spaces or characters
   - Regenerate credentials if needed

2. **Check redirect URI**:
   - Must be exactly `http://localhost:8501`
   - No trailing slashes
   - Match exactly in Google Cloud Console

3. **Verify API is enabled**:
   - Go to Google Cloud Console
   - Ensure YouTube Data API v3 is enabled

4. **Check OAuth consent screen**:
   - Ensure it's configured
   - For External apps, add your email as a test user

5. **Clear existing credentials**:
   - Delete `data/tokens/youtube_token.json`
   - Try authenticating again

### "Invalid Client ID"

**Problem**: Client ID is rejected.

**Solutions**:

1. **Verify Client ID format**:
   - Should look like: `123456789-abcde.apps.googleusercontent.com`
   - No extra characters or spaces

2. **Check project**:
   - Ensure you're using the correct Google Cloud project
   - Verify the OAuth client ID exists in Credentials

3. **Regenerate credentials**:
   - Go to Google Cloud Console → Credentials
   - Delete and recreate the OAuth client ID

### "Unauthorized Client"

**Problem**: Client is not authorized for the redirect URI.

**Solutions**:

1. **Verify redirect URI in Google Cloud Console**:
   - Go to Credentials → Edit OAuth client
   - Ensure `http://localhost:8501` is in authorized redirect URIs

2. **Check for typos**:
   - No trailing slashes
   - Exact match required

3. **Restart the application**:
   - Stop the application
   - Start it again
   - Try authenticating

### "Access Denied"

**Problem**: Access is denied during OAuth flow.

**Solutions**:

1. **For External apps**:
   - Ensure your email is listed as a test user
   - Go to OAuth consent screen → Test users
   - Add your email address

2. **Check app status**:
   - Ensure app is in "Testing" mode
   - For production, complete verification process

3. **Clear browser cookies**:
   - Sometimes cached OAuth data causes issues
   - Try in incognito/private mode

### Token expiration

**Problem**: Tokens expire and need refresh.

**Solutions**:

1. **Automatic refresh**:
   - The application should automatically refresh tokens
   - If it fails, clear credentials and re-authenticate

2. **Manually clear credentials**:
   - Delete `data/tokens/youtube_token.json`
   - Click "Logout" in the sidebar
   - Authenticate again

3. **Check token file permissions**:
   - Ensure the file is readable (600 permissions)
   - On Windows, check file permissions

## Upload Issues

### "Upload failed"

**Problem**: Video upload fails with generic error.

**Solutions**:

1. **Check file validity**:
   - Ensure file is not corrupted
   - Try opening the file in a video player
   - Test with a smaller video file

2. **Check internet connection**:
   - Ensure stable internet connection
   - Try uploading a smaller file first

3. **Check API quota**:
   - Go to Google Cloud Console → Quotas
   - Verify you haven't exceeded daily quota

4. **Check logs**:
   - Review `logs/youtube_uploader.log`
   - Look for specific error messages

5. **Try again**:
   - The application has retry logic
   - Wait a moment and try uploading again

### "Upload stuck at X%"

**Problem**: Upload progress stops and doesn't complete.

**Solutions**:

1. **Wait longer**:
   - Large files can take a long time
   - Check your internet upload speed

2. **Check network stability**:
   - Ensure stable connection
   - Try using a wired connection instead of Wi-Fi

3. **Reduce chunk size**:
   - Edit [`config.py`](../config.py:1)
   - Reduce `UPLOAD_CHUNK_SIZE` (e.g., from 5 MB to 1 MB)
   - Restart the application

4. **Check firewall/antivirus**:
   - Ensure they're not blocking the upload
   - Add exception for the application

5. **Restart the application**:
   - Stop and start again
   - Try uploading the file again

### "Upload progress not updating"

**Problem**: Progress bar doesn't update during upload.

**Solutions**:

1. **Wait a moment**:
   - Progress updates may be delayed
   - Large chunks take time to upload

2. **Check browser console**:
   - Open browser developer tools (F12)
   - Check for JavaScript errors

3. **Refresh the page**:
   - This may interrupt the upload
   - Only use as a last resort

4. **Check logs**:
   - Review `logs/youtube_uploader.log`
   - Look for progress updates

## File Issues

### "Invalid file format"

**Problem**: File format is not supported.

**Solutions**:

1. **Check supported formats**:
   - MP4, MOV, AVI, FLV, WMV, WebM, MKV, MPEG, MPG
   - Ensure your file extension matches

2. **Convert the file**:
   - Use a video converter to change format
   - Recommended: MP4 with H.264 codec

3. **Check file extension**:
   - Ensure the extension is lowercase (.mp4, not .MP4)
   - Rename the file if needed

### "File too large"

**Problem**: File exceeds YouTube's size limit.

**Solutions**:

1. **Check file size**:
   - YouTube limit: 256 GB
   - Your file must be smaller than this

2. **Compress the video**:
   - Use video compression software
   - Reduce resolution or bitrate
   - Recommended: 1080p or lower for most content

3. **Split the video**:
   - Use video editing software to split into parts
   - Upload each part separately

### "File not found"

**Problem**: Application can't find the uploaded file.

**Solutions**:

1. **Check temporary files**:
   - Look for `temp_*` files in the project directory
   - Ensure they exist and are readable

2. **Re-upload the file**:
   - Select the file again
   - Try uploading

3. **Check file permissions**:
   - Ensure the application has read permissions
   - On Windows, check file properties

4. **Clear temp files**:
   - Delete `temp_*` files
   - Re-upload the video

## Network Issues

### "Network error"

**Problem**: Upload fails due to network issues.

**Solutions**:

1. **Check internet connection**:
   - Ensure you have a stable connection
   - Try loading other websites

2. **Check firewall**:
   - Ensure firewall allows the application
   - Add exception for Streamlit

3. **Check proxy settings**:
   - If using a proxy, ensure it's configured correctly
   - Try without proxy if possible

4. **Retry the upload**:
   - The application has automatic retry logic
   - Wait a moment and try again

5. **Use a different network**:
   - Try a different Wi-Fi network
   - Try using mobile hotspot

### "Connection timeout"

**Problem**: Connection to YouTube API times out.

**Solutions**:

1. **Check internet speed**:
   - Test your upload speed
   - Slow connections may timeout

2. **Increase timeout**:
   - Edit [`config.py`](../config.py:1)
   - Increase `RETRY_MAX_DELAY`
   - Restart the application

3. **Reduce chunk size**:
   - Smaller chunks upload faster
   - Edit `UPLOAD_CHUNK_SIZE` in [`config.py`](../config.py:1)

4. **Try at a different time**:
   - Network congestion may cause timeouts
   - Try uploading during off-peak hours

## API Quota Issues

### "API quota exceeded"

**Problem**: Daily API quota has been exceeded.

**Solutions**:

1. **Check quota usage**:
   - Go to Google Cloud Console → Quotas
   - View your current usage

2. **Wait for quota reset**:
   - Quota resets every 24 hours
   - Check the reset time in Google Cloud Console

3. **Request quota increase**:
   - Go to Google Cloud Console → Quotas
   - Click "Request quota increase"
   - May require verification

4. **Optimize API usage**:
   - Avoid unnecessary API calls
   - Use caching where possible

5. **Use a different project**:
   - Create a new Google Cloud project
   - Get new credentials for the new project

### "Quota cost too high"

**Problem**: Upload uses too many quota units.

**Solutions**:

1. **Understand quota costs**:
   - Upload video: 1,600 units
   - Get video details: 1 unit
   - List videos: 1 unit

2. **Optimize uploads**:
   - Batch uploads when possible
   - Avoid repeated uploads of the same video

3. **Monitor usage**:
   - Check quota regularly
   - Plan uploads accordingly

## Performance Issues

### "Application is slow"

**Problem**: Application responds slowly.

**Solutions**:

1. **Check system resources**:
   - Close other applications
   - Ensure sufficient RAM available
   - Check CPU usage

2. **Clear browser cache**:
   - Clear browser cookies and cache
   - Try in incognito/private mode

3. **Reduce file size**:
   - Compress videos before uploading
   - Lower resolution if acceptable

4. **Check internet speed**:
   - Test your upload speed
   - Consider upgrading if slow

### "Memory usage high"

**Problem**: Application uses too much memory.

**Solutions**:

1. **Upload smaller files**:
   - Large files require more memory
   - Consider splitting large videos

2. **Close other applications**:
   - Free up system memory
   - Restart the application

3. **Reduce chunk size**:
   - Smaller chunks use less memory
   - Edit `UPLOAD_CHUNK_SIZE` in [`config.py`](../config.py:1)

4. **Restart the application**:
   - Clear any memory leaks
   - Start fresh

## Getting Help

### Before Asking for Help

1. **Check the logs**:
   - Review `logs/youtube_uploader.log`
   - Look for error messages and stack traces

2. **Try the solutions above**:
   - Go through relevant troubleshooting sections
   - Try multiple solutions if needed

3. **Gather information**:
   - Note the exact error message
   - Record what you were doing when it happened
   - Note your operating system and Python version

### Where to Get Help

1. **Documentation**:
   - [README](../README.md)
   - [Setup Instructions](SETUP.md)
   - [API Setup Guide](API_SETUP.md)

2. **Logs**:
   - Check `logs/youtube_uploader.log`
   - Look for detailed error information

3. **Issue Tracker**:
   - Open an issue on the project repository
   - Include:
     - Error message
     - Steps to reproduce
     - System information
     - Log file excerpt

4. **Community**:
   - Check if others have similar issues
   - Search existing issues

### Reporting Issues

When reporting an issue, include:

1. **Error message**: The exact error you're seeing
2. **Steps to reproduce**: What you did before the error
3. **System information**:
   - Operating system and version
   - Python version (`python --version`)
   - Streamlit version (`streamlit --version`)
4. **Log excerpt**: Relevant part of `logs/youtube_uploader.log`
5. **Screenshots**: If applicable, include screenshots

### Debug Mode

To enable detailed logging:

1. Edit [`config.py`](../config.py:1)
2. Change `LOG_LEVEL = "INFO"` to `LOG_LEVEL = "DEBUG"`
3. Restart the application
4. Check `logs/youtube_uploader.log` for detailed logs

### Resetting the Application

If all else fails, you can reset the application:

1. **Stop the application**
2. **Delete the virtual environment**:
   - Delete the `.venv` directory
3. **Delete data directories**:
   - Delete `data/tokens/` directory
   - Delete `logs/` directory
4. **Run the startup script again**:
   - This will recreate everything from scratch

**Warning**: This will clear all saved credentials and logs.

---

Still having issues? Check the [README](../README.md) or open an issue on the project repository.
