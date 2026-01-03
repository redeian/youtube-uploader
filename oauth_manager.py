"""
OAuth 2.0 Authentication Manager for YouTube API.
Handles authentication flow, token persistence, and automatic token refresh.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

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


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class OAuthManager:
    """
    Manages OAuth 2.0 authentication for YouTube API.
    Handles token storage, encryption, and automatic refresh.
    """
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize OAuth Manager.
        
        Args:
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials: Optional[Credentials] = None
        self.fernet = self._get_encryption_key()
        
    def _get_encryption_key(self) -> Fernet:
        """
        Get or create encryption key for token storage.
        
        Returns:
            Fernet instance for encryption/decryption
        """
        key_file = config.OAUTH_ENCRYPTION_KEY_FILE
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set file permissions to read/write only by owner
            os.chmod(key_file, 0o600)
        
        return Fernet(key)
    
    def _encrypt_token(self, token_data: dict) -> bytes:
        """
        Encrypt token data.
        
        Args:
            token_data: Token dictionary to encrypt
            
        Returns:
            Encrypted bytes
        """
        token_json = json.dumps(token_data)
        return self.fernet.encrypt(token_json.encode())
    
    def _decrypt_token(self, encrypted_data: bytes) -> dict:
        """
        Decrypt token data.
        
        Args:
            encrypted_data: Encrypted token bytes
            
        Returns:
            Decrypted token dictionary
        """
        decrypted = self.fernet.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
    
    def _save_credentials(self, credentials: Credentials) -> None:
        """
        Save credentials to encrypted file.
        
        Args:
            credentials: Google OAuth credentials
        """
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        encrypted_data = self._encrypt_token(token_data)
        
        with open(config.OAUTH_TOKEN_FILE, 'wb') as f:
            f.write(encrypted_data)
        
        # Set file permissions to read/write only by owner
        os.chmod(config.OAUTH_TOKEN_FILE, 0o600)
        
        logger.info("Credentials saved successfully")
    
    def _load_credentials(self) -> Optional[Credentials]:
        """
        Load credentials from encrypted file.
        
        Returns:
            Credentials object or None if not found
        """
        if not config.OAUTH_TOKEN_FILE.exists():
            return None
        
        try:
            with open(config.OAUTH_TOKEN_FILE, 'rb') as f:
                encrypted_data = f.read()
            
            token_data = self._decrypt_token(encrypted_data)
            
            credentials = Credentials(
                token=token_data['token'],
                refresh_token=token_data['refresh_token'],
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )
            
            if token_data['expiry']:
                from datetime import datetime
                credentials.expiry = datetime.fromisoformat(token_data['expiry'])
            
            logger.info("Credentials loaded successfully")
            return credentials
            
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return None
    
    def _refresh_credentials(self, credentials: Credentials) -> Credentials:
        """
        Refresh expired credentials.
        
        Args:
            credentials: Expired credentials
            
        Returns:
            Refreshed credentials
        """
        try:
            credentials.refresh(Request())
            logger.info("Credentials refreshed successfully")
            return credentials
        except Exception as e:
            logger.error(f"Error refreshing credentials: {str(e)}")
            raise AuthenticationError(f"Failed to refresh credentials: {str(e)}")
    
    def authenticate(self) -> Credentials:
        """
        Authenticate with YouTube API using OAuth 2.0 flow.
        Loads existing credentials if available, otherwise initiates new flow.
        
        Returns:
            Authenticated Credentials object
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Try to load existing credentials
        credentials = self._load_credentials()
        
        if credentials and credentials.valid:
            logger.info("Using existing valid credentials")
            self.credentials = credentials
            return credentials
        
        if credentials and credentials.expired and credentials.refresh_token:
            logger.info("Refreshing expired credentials")
            credentials = self._refresh_credentials(credentials)
            self._save_credentials(credentials)
            self.credentials = credentials
            return credentials
        
        # Need to perform new OAuth flow
        logger.info("Initiating new OAuth flow")
        
        try:
            # Create OAuth flow configuration
            client_config = {
                'installed': {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'redirect_uris': [config.OAUTH_REDIRECT_URI]
                }
            }
            
            # Create flow
            flow = InstalledAppFlow.from_client_config(
                client_config,
                scopes=config.OAUTH_SCOPES
            )
            
            # Run local server for OAuth callback
            credentials = flow.run_local_server(
                port=config.OAUTH_PORT,
                prompt='consent',
                authorization_prompt_message='Please visit this URL to authorize the application: {url}'
            )
            
            # Save credentials
            self._save_credentials(credentials)
            self.credentials = credentials
            
            logger.info("Authentication successful")
            return credentials
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Get current credentials without triggering authentication.
        
        Returns:
            Credentials object or None if not authenticated
        """
        if self.credentials and self.credentials.valid:
            return self.credentials
        
        # Try to load from disk
        credentials = self._load_credentials()
        if credentials:
            if credentials.valid:
                self.credentials = credentials
                return credentials
            elif credentials.expired and credentials.refresh_token:
                try:
                    credentials = self._refresh_credentials(credentials)
                    self._save_credentials(credentials)
                    self.credentials = credentials
                    return credentials
                except Exception:
                    pass
        
        return None
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        credentials = self.get_credentials()
        return credentials is not None and credentials.valid
    
    def clear_credentials(self) -> None:
        """
        Clear stored credentials.
        """
        if config.OAUTH_TOKEN_FILE.exists():
            config.OAUTH_TOKEN_FILE.unlink()
            logger.info("Credentials cleared")
        
        self.credentials = None
    
    def get_auth_url(self) -> str:
        """
        Get authorization URL for manual OAuth flow.
        Useful for environments where local server won't work.
        
        Returns:
            Authorization URL
        """
        client_config = {
            'installed': {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': [config.OAUTH_REDIRECT_URI]
            }
        }
        
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=config.OAUTH_SCOPES
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
