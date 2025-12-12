"""MCP client for BigQuery with OAuth authentication."""

import asyncio
import json
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.session import ClientSession as MCPClientSession
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
        print(f"\nConnecting to BigQuery MCP server at {server_url}...")

        # Create HTTP client with OAuth token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        self.http_client = httpx.AsyncClient(headers=headers, timeout=30.0)

        try:
            # Create custom HTTP-based transport for MCP
            from mcp.client.session import ClientSession as MCPSession
            from mcp.shared.message import JSONRPCMessage

            # Use HTTP transport for MCP communication
            class HTTPTransport:
                def __init__(self, client, url):
                    self.client = client
                    self.url = url

                async def send(self, message):
                    response = await self.client.post(self.url, json=message)
                    response.raise_for_status()
                    return response.json()

                async def receive(self):
                    # For HTTP, we don't have a persistent receive channel
                    pass

            transport = HTTPTransport(self.http_client, server_url)

            # Create MCP session with HTTP transport
            self.session = ClientSession(
                read_stream=None,
                write_stream=None
            )

            # Initialize the session with HTTP POST
            init_response = await self.http_client.post(
                server_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "bigquery-mcp-client",
                            "version": "1.0.0"
                        }
                    }
                }
            )
            init_response.raise_for_status()

            print(f"Connected to BigQuery MCP server")
            print(f"Response: {init_response.json()}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    async def list_tools(self):
        """List available tools from the MCP server."""
        if not self.http_client:
            raise ValueError("Not connected. Call connect() first.")

        try:
            response = await self.http_client.post(
                "https://bigquery.googleapis.com/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
            )
            response.raise_for_status()
            result = response.json()

            print(f"\nAvailable tools:")
            if "result" in result and "tools" in result["result"]:
                for tool in result["result"]["tools"]:
                    print(f"  - {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
            return result
        except Exception as e:
            print(f"Failed to list tools: {e}")
            raise

    async def query_table(self, table_id, limit=10):
        """Query a BigQuery table using MCP.

        Args:
            table_id: Full table ID (project.dataset.table)
            limit: Maximum number of rows to return

        Returns:
            Query results
        """
        print(f"\nQuerying table: {table_id}")

        query = f"SELECT * FROM `{table_id}` LIMIT {limit}"

        # Use MCP HTTP transport with execute_sql tool
        response = await self.http_client.post(
            "https://bigquery.googleapis.com/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "execute_sql",
                    "arguments": {
                        "query": query,
                        "projectId": self.project_id
                    }
                }
            }
        )
        response.raise_for_status()
        result = response.json()

        print(f"MCP query completed")
        return result

    async def close(self):
        """Close the MCP connection."""
        if self.http_client:
            await self.http_client.aclose()
        await self.exit_stack.aclose()
        print("Disconnected from MCP server")


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
        await client.list_tools()

        # Query the table
        result = await client.query_table(table_id)

        print("\n" + "=" * 60)
        print("Query Results")
        print("=" * 60)
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()
