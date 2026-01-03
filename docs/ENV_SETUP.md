# Environment Configuration Guide

This guide explains how to configure the YouTube Video Uploader application using a `.env` file.

## Overview

The application supports two methods for configuring YouTube API credentials:

1. **.env file (Recommended)**: Secure, persistent configuration
2. **Manual input**: Enter credentials in the sidebar each session

Using a `.env` file is recommended because:
- Credentials are stored securely on your local machine
- No need to re-enter credentials each session
- Easy to manage and update
- More secure than hardcoding in source files

## Quick Setup

### Step 1: Create .env File

Copy the example file:

```bash
# On Unix/macOS
cp .env.example .env

# On Windows
copy .env.example .env
```

### Step 2: Get Your Credentials

Follow the [API Setup Guide](API_SETUP.md) to obtain your YouTube OAuth credentials.

### Step 3: Edit .env File

Open the `.env` file in a text editor and fill in your credentials:

```bash
# YouTube OAuth 2.0 Client ID
YOUTUBE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com

# YouTube OAuth 2.0 Client Secret
YOUTUBE_CLIENT_SECRET=your_client_secret_here

# OAuth Port (default: 8080)
# Change this if port 8080 is already in use
OAUTH_PORT=8080
```

### Step 4: Save and Restart

Save the `.env` file and restart the application. The credentials will be automatically loaded.

## Configuration Options

### YOUTUBE_CLIENT_ID (Required)

Your YouTube OAuth 2.0 Client ID.

**How to get it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services → Credentials
3. Click on your OAuth client ID
4. Copy the Client ID

**Format:** `123456789-abcde.apps.googleusercontent.com`

### YOUTUBE_CLIENT_SECRET (Required)

Your YouTube OAuth 2.0 Client Secret.

**How to get it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services → Credentials
3. Click on your OAuth client ID
4. Copy the Client Secret

**Format:** `GOCSPX-abc123xyz456`

### OAUTH_PORT (Optional)

Port for OAuth authentication server.

**Default:** `8080`

**Why separate from Streamlit?**
- Streamlit runs on port 8501
- OAuth uses port 8080 to avoid conflicts
- Both ports can run simultaneously

**When to change:**
- If port 8080 is already in use
- If you want to use a different port

**Example:**
```bash
OAUTH_PORT=9090
```

**Important:** If you change this port, you must also update the redirect URI in Google Cloud Console.

## Security Best Practices

### 1. Never Commit .env to Version Control

The `.env` file is already included in `.gitignore` to prevent accidental commits.

**Check .gitignore:**
```gitignore
# Environment Variables
.env
.env.local
```

### 2. Use Strong Secrets

- Keep your Client Secret private
- Never share it publicly
- Rotate it if compromised

### 3. File Permissions

Set appropriate file permissions:

```bash
# On Unix/macOS
chmod 600 .env

# This makes it readable only by you
```

### 4. Secure Storage

- Store `.env` in your project directory
- Don't upload it to cloud storage
- Back it up securely if needed

## Troubleshooting

### Credentials Not Loading

**Problem:** Application asks for credentials despite having a `.env` file.

**Solutions:**

1. **Check file name:**
   - Must be exactly `.env` (not `.env.txt` or similar)
   - On Windows, ensure file extensions are visible

2. **Check file location:**
   - Must be in the project root directory
   - Same directory as `app.py`

3. **Check file format:**
   - No spaces around `=` signs
   - No quotes around values
   - No trailing spaces

4. **Restart application:**
   - `.env` is loaded on application start
   - Restart after making changes

### Port Already in Use

**Problem:** Error "Address already in use" when authenticating.

**Solutions:**

1. **Change OAUTH_PORT in .env:**
   ```bash
   OAUTH_PORT=9090
   ```

2. **Update redirect URI in Google Cloud Console:**
   - Go to APIs & Services → Credentials
   - Edit your OAuth client ID
   - Add new redirect URI: `http://localhost:9090`

3. **Restart the application**

### Invalid Credentials

**Problem:** Authentication fails with "Invalid credentials" error.

**Solutions:**

1. **Verify credentials:**
   - Check Client ID and Secret are correct
   - No extra spaces or characters

2. **Check redirect URI:**
   - Must match `http://localhost:{OAUTH_PORT}`
   - No trailing slashes

3. **Regenerate credentials:**
   - Go to Google Cloud Console
   - Reset Client Secret
   - Update `.env` file

## Example .env File

```bash
# YouTube API Credentials
# DO NOT commit this file to version control!

# YouTube OAuth 2.0 Client ID
YOUTUBE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com

# YouTube OAuth 2.0 Client Secret
YOUTUBE_CLIENT_SECRET=GOCSPX-abc123xyz456def789

# OAuth Port (default: 8080)
OAUTH_PORT=8080
```

## Advanced Configuration

### Multiple Environments

You can use different `.env` files for different environments:

```bash
# Development
.env.development

# Production
.env.production

# Testing
.env.testing
```

To use a specific environment:

```bash
# Unix/macOS
export ENV=development

# Windows
set ENV=development
```

Then update [`config.py`](../config.py:1) to load the appropriate file.

### Environment-Specific Ports

Use different ports for different environments:

```bash
# Development
OAUTH_PORT=8080

# Production
OAUTH_PORT=8081

# Testing
OAUTH_PORT=8082
```

## Validation

After setting up your `.env` file, verify it's working:

1. **Start the application**
2. **Check the sidebar**
   - Should show "✅ Credentials loaded from .env file"
   - Should not show input fields for Client ID and Secret
3. **Click "Login with YouTube"**
4. **Authentication should work**

## Next Steps

Once your `.env` file is configured:

1. Start the application
2. Authenticate with YouTube
3. Upload your first video!

For more information:
- [API Setup Guide](API_SETUP.md)
- [Setup Instructions](SETUP.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [README](../README.md)

---

Happy uploading! 📹
