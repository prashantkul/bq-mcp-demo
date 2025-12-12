"""MCP client for BigQuery with OAuth authentication."""

import asyncio
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
import httpx


class BigQueryMCPClient:
    """MCP client for connecting to BigQuery remote MCP server."""

    def __init__(self, access_token, project_id):
        """Initialize MCP client.

        Args:
            access_token: OAuth access token for authentication
            project_id: GCP project ID
        """
        self.access_token = access_token
        self.project_id = project_id
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.http_client = None

    async def connect(self, server_url="https://bigquery.googleapis.com/mcp"):
        """Connect to BigQuery MCP server.

        Args:
            server_url: URL of the BigQuery MCP server
        """
        print(f"\n🔗 Connecting to BigQuery MCP server at {server_url}...")

        # Create HTTP client with OAuth token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        self.http_client = httpx.AsyncClient(headers=headers, timeout=30.0)

        try:
            # Initialize MCP session with SSE transport for remote server
            transport = await self.exit_stack.enter_async_context(
                sse_client(server_url)
            )

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(transport[0], transport[1])
            )

            # Initialize the session
            await self.session.initialize()

            print(f"✅ Connected to BigQuery MCP server!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"📋 Attempting direct HTTP connection as fallback...")
            # Keep http_client for direct API calls
            return False

    async def list_tools(self):
        """List available tools from the MCP server."""
        if not self.session:
            raise ValueError("Not connected. Call connect() first.")

        result = await self.session.list_tools()
        print(f"\n🔧 Available tools:")
        for tool in result.tools:
            print(f"  - {tool.name}: {tool.description}")
        return result.tools

    async def query_table(self, table_id, limit=10):
        """Query a BigQuery table.

        Args:
            table_id: Full table ID (project.dataset.table)
            limit: Maximum number of rows to return

        Returns:
            Query results
        """
        print(f"\n📊 Querying table: {table_id}")

        query = f"SELECT * FROM `{table_id}` LIMIT {limit}"

        if self.session:
            # Try using MCP session if connected
            try:
                result = await self.session.call_tool("query", {
                    "query": query,
                    "project_id": self.project_id
                })
                return result
            except Exception as e:
                print(f"⚠️  MCP query failed: {e}")
                print(f"📋 Falling back to direct BigQuery API...")

        # Fallback to direct BigQuery API
        return await self._query_direct(query)

    async def _query_direct(self, query):
        """Query BigQuery directly using REST API.

        Args:
            query: SQL query string

        Returns:
            Query results
        """
        url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.project_id}/queries"

        payload = {
            "query": query,
            "useLegacySql": False
        }

        try:
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            print(f"✅ Query completed!")
            return result
        except Exception as e:
            print(f"❌ Query failed: {e}")
            raise

    async def close(self):
        """Close the MCP connection."""
        if self.http_client:
            await self.http_client.aclose()
        await self.exit_stack.aclose()
        print("🔌 Disconnected from MCP server")


async def demo_query(access_token, project_id, table_id):
    """Demo function to query BigQuery table with OAuth.

    Args:
        access_token: OAuth access token
        project_id: GCP project ID
        table_id: Full table ID (project.dataset.table)
    """
    client = BigQueryMCPClient(access_token, project_id)

    try:
        await client.connect()

        # Try to list tools if connected via MCP
        try:
            await client.list_tools()
        except:
            print("ℹ️  MCP tools not available, using direct API")

        # Query the table
        result = await client.query_table(table_id)

        print("\n" + "=" * 60)
        print("Query Results")
        print("=" * 60)
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()
