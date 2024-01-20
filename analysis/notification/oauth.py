
from pydantic import BaseModel, Field
from typing import Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from typing import Any
from os import path, mkdir
from json import dump, load
from .models import Scopes
from .config import Config


class OAuth(BaseModel):
    secrets_file: str
    scopes: list[str] = [
        Scopes.drafts.value, Scopes.labels.value
    ]
    config: Config = Config()
    
    def credentials_to_dict(self, credentials: Credentials) -> dict:
        """Convert credentials to a dict."""
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }
        
    def create_default_credentials_path(self) -> str:
        """Create the default credentials directory."""
        current_user_home_dir = path.expanduser('~')
        if not path.exists(path.join(current_user_home_dir, self.config.credentials_dir)):
            mkdir(path.join(current_user_home_dir, self.config.credentials_dir))
        return path.join(current_user_home_dir, self.config.credentials_dir)
        
    def get_default_credentials_path(self) -> str:
        """Generate the default api token file location."""
        credentials_dir: str = self.create_default_credentials_path()
        credentials_file_path = path.join(credentials_dir, self.config.credentials_file_name)
        return credentials_file_path

    def get_credentials(self) -> Credentials:
        """Get the credentials."""
        credentials: Credentials = None
        credentials_path: str = self.get_default_credentials_path()
        try:
            with open(credentials_path, 'r', encoding='utf-8') as creds:
                credentials = Credentials(**load(creds))
        except FileNotFoundError:
            pass
        return credentials
    
    def generate_credentials(self) -> Credentials:
        flow = InstalledAppFlow.from_client_secrets_file(self.secrets_file, self.scopes)
        credentials = flow.run_local_server(port=0)
        return credentials
    
    def save_credentials(self, credentials: Credentials) -> None:
        credentials_dict = self.credentials_to_dict(credentials)
        credentials_path: str = self.get_default_credentials_path()
        with open(credentials_path, 'w', encoding='utf-8') as f:
            dump(credentials_dict, f)
            
    def credentials_expired(self, credentials: Credentials) -> bool:
        # youtube_client = self.get_youtube_client(credentials=credentials)
        # youtube_find_request = youtube_client.search().list(q='', part='id')
        # try:
        #     youtube_find_request.execute()
        # except RefreshError:
        #     return True
        # return False
        return False
            
    def get_gmail_client(self, credentials: Credentials) -> Any:
        gmail_client = build(self.config.api_service_name, 
                             self.config.api_version,
                             credentials=credentials)
        return gmail_client
    
    def authenticate(self) -> Any:
        credentials: Credentials = self.get_credentials()
        if not credentials or self.credentials_expired(credentials=credentials):
            credentials = self.generate_credentials()
            self.save_credentials(credentials=credentials)
        gmail_client = self.get_gmail_client(credentials=credentials)
        return gmail_client
    
def get_gmail_client(secrets_file: str):
    oauth: OAuth = OAuth(secrets_file=secrets_file)
    gmail_client = oauth.authenticate()
    return gmail_client