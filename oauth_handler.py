"""OAuth 2.0 handler for Google BigQuery MCP server."""

import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    def do_GET(self):
        """Handle GET request from OAuth callback."""
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body style="font-family: system-ui; padding: 40px; text-align: center;">
                    <h1>&#x2705; Authentication Successful!</h1>
                    <p>You can close this window and return to your terminal.</p>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>&#x274C; No authorization code received</h1>")

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class BigQueryOAuthHandler:
    """Handles OAuth 2.0 authentication for BigQuery."""

    SCOPES = [
        'https://www.googleapis.com/auth/bigquery',
        'https://www.googleapis.com/auth/bigquery.readonly',
        'https://www.googleapis.com/auth/cloud-platform'
    ]

    def __init__(self, client_secret_file):
        """Initialize OAuth handler.

        Args:
            client_secret_file: Path to OAuth client secret JSON file
        """
        self.client_secret_file = client_secret_file
        self.credentials = None

    def authenticate(self):
        """Run OAuth flow to get credentials.

        Returns:
            google.oauth2.credentials.Credentials: OAuth credentials
        """
        print("\n🔐 Starting BigQuery OAuth flow...\n")

        # Create flow from client secrets
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secret_file,
            scopes=self.SCOPES,
            redirect_uri='http://localhost:8080'
        )

        # Run local server for OAuth callback
        self.credentials = flow.run_local_server(
            port=8080,
            open_browser=True,
            success_message='Authentication successful! You can close this window.'
        )

        print("✅ Authentication successful!")
        return self.credentials

    def get_access_token(self):
        """Get current access token.

        Returns:
            str: Access token
        """
        if not self.credentials:
            raise ValueError("Not authenticated. Call authenticate() first.")

        # Refresh token if expired
        if self.credentials.expired and self.credentials.refresh_token:
            print("🔄 Refreshing access token...")
            self.credentials.refresh(Request())

        return self.credentials.token

    def save_credentials(self, filename='token.json'):
        """Save credentials to file.

        Args:
            filename: Path to save credentials
        """
        with open(filename, 'w') as f:
            f.write(self.credentials.to_json())
        print(f"💾 Credentials saved to {filename}")

    def load_credentials(self, filename='token.json'):
        """Load credentials from file.

        Args:
            filename: Path to credentials file

        Returns:
            bool: True if credentials loaded successfully
        """
        try:
            self.credentials = Credentials.from_authorized_user_file(
                filename,
                self.SCOPES
            )

            # Refresh if expired
            if self.credentials.expired and self.credentials.refresh_token:
                print("🔄 Refreshing access token...")
                self.credentials.refresh(Request())

            print(f"✅ Credentials loaded from {filename}")
            return True
        except Exception as e:
            print(f"⚠️  Could not load credentials: {e}")
            return False
