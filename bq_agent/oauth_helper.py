"""OAuth helper for BigQuery authentication."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oauth_handler import BigQueryOAuthHandler


def get_bigquery_token():
    """Get OAuth token for BigQuery access.

    Returns:
        str: OAuth access token
    """
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    client_secret_file = os.path.join(
        parent_dir,
        "client_secret_174522850388-srg7egdrj6q3q2un44vr3npe7i79i4jk.apps.googleusercontent.com.json"
    )
    token_file = os.path.join(parent_dir, "token.json")

    oauth = BigQueryOAuthHandler(client_secret_file)

    # Try to load existing credentials
    if not oauth.load_credentials(token_file):
        print("No valid credentials found. Starting OAuth flow...")
        oauth.authenticate()
        oauth.save_credentials(token_file)

    return oauth.get_access_token()
