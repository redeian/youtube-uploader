# YouTube API Setup Guide

Complete guide to obtaining YouTube Data API v3 credentials for the YouTube Video Uploader application.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Configuring OAuth Consent Screen](#configuring-oauth-consent-screen)
5. [Creating OAuth 2.0 Credentials](#creating-oauth-20-credentials)
6. [Enabling YouTube Data API v3](#enabling-youtube-data-api-v3)
7. [Testing Your Credentials](#testing-your-credentials)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

To use the YouTube Video Uploader application, you need to:

1. Create a Google Cloud project
2. Enable the YouTube Data API v3
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials (Client ID and Client Secret)
5. Configure redirect URI for the application

These credentials allow the application to upload videos to your YouTube channel on your behalf.

## Prerequisites

Before you begin, ensure you have:

- A Google account (Gmail or Google Workspace)
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- Basic understanding of OAuth 2.0 (helpful but not required)

## Step-by-Step Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project selector dropdown (top left)
4. Click "New Project"
5. Enter a project name (e.g., "YouTube Video Uploader")
6. Click "Create"
7. Wait for the project to be created (usually takes a few seconds)
8. Select your new project from the dropdown

### Step 2: Enable YouTube Data API v3

1. In the Google Cloud Console, navigate to:
   - **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click on "YouTube Data API v3" from the results
4. Click the "Enable" button
5. Wait for the API to be enabled

### Step 3: Configure OAuth Consent Screen

1. Navigate to **APIs & Services** → **OAuth consent screen**
2. Choose user type:
   - **External**: For public use (recommended for personal use)
   - **Internal**: For organization use only
3. Click "Create"
4. Fill in the required information:
   - **App name**: YouTube Video Uploader
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
5. Click "Save and Continue"
6. For "Scopes", click "Save and Continue" (no additional scopes needed)
7. For "Test users", add your email address if using External type
8. Click "Save and Continue"
9. Review and click "Back to Dashboard"

### Step 4: Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** → **Credentials**
2. Click "Create Credentials" → "OAuth client ID"
3. Select application type: **Web application**
4. Fill in the required information:
   - **Name**: YouTube Video Uploader
5. Add authorized redirect URIs:
   - Click "Add URI"
   - Enter: `http://localhost:8080`
   - Click "Add URI" again
6. Click "Create"
7. **IMPORTANT**: Copy the Client ID and Client Secret from the popup
   - Client ID: A long string like `123456789-abcde.apps.googleusercontent.com`
   - Client Secret: A shorter string like `GOCSPX-abc123xyz456`

### Step 5: Save Your Credentials

Save your credentials securely:

```text
Client ID:     123456789-abcde.apps.googleusercontent.com
Client Secret: GOCSPX-abc123xyz456
```

**Security Tips**:
- Never share these credentials
- Don't commit them to version control
- Store them in a secure location
- You can always regenerate them if needed

## Configuring OAuth Consent Screen (Detailed)

### For External Apps (Recommended)

1. **App Information**:
   - App name: YouTube Video Uploader
   - App logo: Optional (recommended for production)
   - User support email: Your email
   - Developer contact: Your email

2. **Scopes**:
   - No additional scopes needed for testing
   - The application will request necessary scopes during authentication

3. **Test Users**:
   - Add your email address as a test user
   - Only test users can use the app in testing mode
   - To publish to public, you need to complete verification

### For Internal Apps

If you're using a Google Workspace account:

1. Choose "Internal" as user type
2. Complete the consent screen setup
3. All users in your organization can use the app
4. No verification needed

## Creating OAuth 2.0 Credentials (Detailed)

### Web Application Configuration

When creating the credentials, ensure:

1. **Application Type**: Web application
2. **Name**: YouTube Video Uploader (or any descriptive name)
3. **Authorized JavaScript origins**: Leave empty (not needed)
4. **Authorized redirect URIs**: Must include:
   - `http://localhost:8080`

### Why localhost:8080?

The OAuth authentication uses a separate local server on port 8080 to avoid conflicts with Streamlit (which runs on port 8501). The OAuth flow redirects back to this URL after authentication.

### Testing the Redirect URI

To verify your redirect URI is correct:

1. Start the application
2. Open `http://localhost:8501` in your browser (Streamlit will be running here)
3. The OAuth callback will use port 8080 automatically

## Enabling YouTube Data API v3 (Detailed)

### API Quotas and Limits

YouTube Data API v3 has default quotas:

- **Daily quota**: 10,000 units
- **Upload cost**: 1,600 units per video
- **Other operations**: Varying costs

### Monitoring Your Quota

1. Go to **APIs & Services** → **Quotas**
2. Select "YouTube Data API v3"
3. View your current usage and limits
4. Request quota increase if needed (requires verification)

### Quota Cost Reference

Common operations:
- Upload video: 1,600 units
- Get video details: 1 unit
- List videos: 1 unit
- Search videos: 100 units

## Testing Your Credentials

### Using the Application

1. Start the YouTube Video Uploader application
2. Enter your Client ID and Client Secret in the sidebar
3. Click "Login with YouTube"
4. If successful, you'll see "✅ Authenticated"

### Manual Testing with OAuth Playground

1. Go to [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
2. Configure your client ID and secret
3. Select scopes:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`
4. Authorize and test the flow

### Verifying Token Storage

After successful authentication:

1. Check `data/tokens/youtube_token.json` exists
2. The file should contain encrypted token data
3. Token files have restricted permissions (600)

## Security Best Practices

### Protecting Your Credentials

1. **Never share** your Client ID and Client Secret
2. **Don't commit** credentials to version control
3. **Use environment variables** for production deployments
4. **Rotate credentials** if they're compromised

### Using Streamlit Secrets (Production)

For production deployment on Streamlit Cloud:

1. Go to your app settings
2. Add secrets in `.streamlit/secrets.toml`:
   ```toml
   [youtube]
   client_id = "your-client-id.apps.googleusercontent.com"
   client_secret = "your-client-secret"
   ```

3. Update [`app.py`](../app.py:1) to read from secrets:
   ```python
   import streamlit as st
   
   client_id = st.secrets["youtube"]["client_id"]
   client_secret = st.secrets["youtube"]["client_secret"]
   ```

### Token Security

The application implements several security measures:

- **Encryption**: Tokens are encrypted using Fernet encryption
- **File Permissions**: Token files have restricted permissions (600)
- **Automatic Refresh**: Tokens are refreshed when expired
- **Secure Storage**: Tokens are stored in `data/tokens/` directory

### Revoking Access

If you need to revoke the application's access:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Navigate to "Third-party apps & services"
3. Find "YouTube Video Uploader"
4. Click "Remove Access"

## Troubleshooting

### Common Issues

#### "Invalid Client ID"

**Solutions**:
- Verify you copied the Client ID correctly
- Ensure the OAuth consent screen is configured
- Check that YouTube Data API v3 is enabled

#### "Unauthorized Client"

**Solutions**:
- Verify the redirect URI is exactly `http://localhost:8501`
- Check the OAuth consent screen is configured
- Ensure you're using the correct project

#### "Access Denied"

**Solutions**:
- Check that you're listed as a test user (for External apps)
- Verify the scopes are correct
- Ensure the app is in "Testing" mode

#### "Redirect URI Mismatch"

**Solutions**:
- Ensure the redirect URI in Google Console matches exactly
- Check for trailing slashes or typos
- Verify the application is running on port 8501

#### "Quota Exceeded"

**Solutions**:
- Wait for quota to reset (usually 24 hours)
- Request quota increase in Google Cloud Console
- Optimize your API usage

### Debug Mode

To enable debug logging:

1. Edit [`config.py`](../config.py:1)
2. Change `LOG_LEVEL = "INFO"` to `LOG_LEVEL = "DEBUG"`
3. Restart the application
4. Check `logs/youtube_uploader.log` for detailed logs

### Regenerating Credentials

If you need new credentials:

1. Go to **APIs & Services** → **Credentials**
2. Find your OAuth client ID
3. Click the pencil icon to edit
4. Click "Reset secret" to generate a new Client Secret
5. Or click "Delete" to remove and recreate credentials

## Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Quotas](https://developers.google.com/youtube/v3/determine_quota_cost)

## Next Steps

Once you have your credentials:

1. Start the YouTube Video Uploader application
2. Enter your Client ID and Client Secret
3. Authenticate with YouTube
4. Upload your first video!

For more help, see:
- [Setup Instructions](SETUP.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [README](../README.md)

---

Happy uploading! 📹
