# BigQuery MCP OAuth Demo

Python client demonstrating OAuth 2.0 authentication flow for Google's BigQuery MCP server.

## Overview

This demo implements a Model Context Protocol (MCP) client that authenticates with Google BigQuery using OAuth 2.0. The client attempts to connect to BigQuery's MCP server and falls back to direct REST API calls when necessary.

## Prerequisites

- Python 3.11+
- Conda (recommended)
- Google Cloud OAuth credentials (client_secret JSON file)
- Access to a BigQuery project

## Setup

1. Create and activate conda environment:
```bash
conda env create -f environment.yml
conda activate bigquery-mcp-oauth
```

2. Install MCP SDK:
```bash
pip install mcp --index-url https://pypi.org/simple
```

3. Place your OAuth client secret file in the project directory

## Usage

Run the demo:
```bash
python demo.py
```

The script will:
1. Check for cached OAuth credentials in `token.json`
2. Launch browser for authentication if needed
3. Request necessary BigQuery scopes:
   - `https://www.googleapis.com/auth/bigquery`
   - `https://www.googleapis.com/auth/bigquery.readonly`
   - `https://www.googleapis.com/auth/cloud-platform`
4. Attempt MCP server connection
5. Query the specified BigQuery table
6. Display results

## Configuration

Edit `demo.py` to modify:
- `project_id`: Your GCP project ID
- `table_id`: BigQuery table to query (format: `project.dataset.table`)

## Architecture

### Components

**oauth_handler.py**
- Manages OAuth 2.0 flow using `google-auth-oauthlib`
- Handles token refresh and persistence
- Implements local callback server for authorization code

**mcp_client.py**
- BigQuery MCP client implementation
- Attempts SSE transport connection to MCP server
- Falls back to direct BigQuery REST API on connection failure
- Provides query interface with automatic authentication

**demo.py**
- Main entry point
- Orchestrates OAuth flow and BigQuery queries
- Configured for `privacy-ml-lab2.travel_data.agent_interactions` table

## Example Output

```
============================================================
BigQuery MCP Server - OAuth Demo
============================================================

Access Token: ya29.a0Aa7pCA-fHosNK...0PhWhNsJ7no3DeQw0206

============================================================
Querying Table: privacy-ml-lab2.travel_data.agent_interactions
============================================================

Connecting to BigQuery MCP server at https://bigquery.googleapis.com/mcp...
Connection failed: unhandled errors in a TaskGroup (1 sub-exception)
Attempting direct HTTP connection as fallback...
MCP tools not available, using direct API

Querying table: privacy-ml-lab2.travel_data.agent_interactions
Query completed!

============================================================
Query Results
============================================================
{
  "kind": "bigquery#queryResponse",
  "schema": {
    "fields": [
      {
        "name": "interaction_id",
        "type": "STRING"
      },
      {
        "name": "user_id",
        "type": "STRING"
      },
      {
        "name": "session_id",
        "type": "STRING"
      },
      {
        "name": "agent_name",
        "type": "STRING"
      },
      {
        "name": "query_type",
        "type": "STRING"
      },
      {
        "name": "user_query",
        "type": "STRING"
      },
      {
        "name": "agent_response",
        "type": "STRING"
      },
      {
        "name": "tools_used",
        "type": "JSON"
      },
      {
        "name": "created_at",
        "type": "TIMESTAMP"
      }
    ]
  },
  "totalRows": "7",
  "rows": [
    {
      "f": [
        {"v": null},
        {"v": null},
        {"v": null},
        {"v": "travel_advisor_agent"},
        {"v": null},
        {"v": "Hello"},
        {"v": "Hello! I am your personal travel advisor..."},
        {"v": null},
        {"v": "1.758051366853934E9"}
      ]
    },
    ...
  ],
  "totalBytesProcessed": "1534",
  "jobComplete": true,
  "totalSlotMs": "117"
}
```

## Query Results Summary

Successfully queried `agent_interactions` table containing 7 records:

| Field | Type | Description |
|-------|------|-------------|
| interaction_id | STRING | Unique interaction identifier |
| user_id | STRING | User identifier |
| session_id | STRING | Session identifier |
| agent_name | STRING | Agent name (travel_advisor_agent) |
| query_type | STRING | Type of query |
| user_query | STRING | User's input query |
| agent_response | STRING | Agent's response |
| tools_used | JSON | Tools utilized by agent |
| created_at | TIMESTAMP | Interaction timestamp |

Sample interactions include:
- Greetings: "Hello", "Hey"
- Questions: "What destinations do you have?"
- Agent responses providing travel recommendations for destinations like Bali, Maldives, Paris, Tokyo, etc.

## Notes

- OAuth tokens are cached in `token.json` for reuse
- Token refresh happens automatically when expired
- MCP server connection currently fails (endpoint may not be publicly available)
- Fallback to BigQuery REST API works reliably
- Processed 1534 bytes, billed 10MB (minimum billing applies)

## Dependencies

See `requirements.txt` and `environment.yml` for complete list:
- google-auth-oauthlib
- google-auth
- mcp
- httpx

## License

MIT
