"""BigQuery Agent using Google ADK with MCP integration."""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from .oauth_helper import get_bigquery_token

# Load environment variables from .env file
load_dotenv()

# Get Google Cloud project ID from environment
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "privacy-ml-lab2")

# Get OAuth token for BigQuery
access_token = get_bigquery_token()

# Configure BigQuery MCP server connection parameters
mcp_connection_params = StreamableHTTPConnectionParams(
    url="https://bigquery.googleapis.com/mcp",
    headers={
        "Authorization": f"Bearer {access_token}",
        "X-Goog-User-Project": GOOGLE_CLOUD_PROJECT
    }
)

# Create MCP toolset for BigQuery
bq_toolset = McpToolset(
    connection_params=mcp_connection_params,
    tool_name_prefix="bq"
)

# Define root agent with BigQuery tools
root_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="bigquery_assistant",
    description="A helpful assistant with access to BigQuery via MCP",
    instruction=f"""You are a helpful BigQuery assistant with access to BigQuery MCP tools.

You can help users:
- List datasets and tables in their BigQuery projects
- Get metadata about datasets and tables
- Execute SQL queries (SELECT statements only)
- Analyze data and provide insights

When executing queries, make sure to:
1. Use proper BigQuery SQL syntax
2. Always specify the project ID as {GOOGLE_CLOUD_PROJECT}
3. Format results in a clear, readable way

Be helpful and guide users through their BigQuery data exploration.""",
    tools=[bq_toolset]
)
