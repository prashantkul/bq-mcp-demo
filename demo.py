#!/usr/bin/env python3
"""Demo script for BigQuery MCP OAuth flow."""

import asyncio
import os
import json
from oauth_handler import BigQueryOAuthHandler
from mcp_client import demo_query


def main():
    """Main demo function."""
    print("=" * 60)
    print("BigQuery MCP Server - OAuth Demo")
    print("=" * 60)

    # Configuration
    client_secret_file = "client_secret_174522850388-srg7egdrj6q3q2un44vr3npe7i79i4jk.apps.googleusercontent.com.json"
    project_id = "privacy-ml-lab2"
    table_id = "privacy-ml-lab2.travel_data.agent_interactions"

    if not os.path.exists(client_secret_file):
        print(f"❌ Error: Client secret file not found: {client_secret_file}")
        return

    # Initialize OAuth handler
    oauth = BigQueryOAuthHandler(client_secret_file)

    # Try to load existing credentials
    if not oauth.load_credentials():
        # Run OAuth flow if no valid credentials
        print("\n📋 No valid credentials found. Starting OAuth flow...\n")
        oauth.authenticate()
        oauth.save_credentials()

    # Get access token
    access_token = oauth.get_access_token()
    print(f"\n🎟️  Access Token: {access_token[:20]}...{access_token[-20:]}")

    # Query BigQuery table
    print("\n" + "=" * 60)
    print(f"Querying Table: {table_id}")
    print("=" * 60)

    asyncio.run(demo_query(access_token, project_id, table_id))

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
