#!/usr/bin/env python3
"""Test script for BigQuery Agent."""

from bq_agent.agent import root_agent


def main():
    """Test the BigQuery agent."""
    print("=" * 60)
    print("BigQuery Agent (Google ADK + MCP)")
    print("=" * 60)

    # Test query
    query = "List all datasets in the privacy-ml-lab2 project"
    print(f"\nQuery: {query}\n")

    # Send query to agent
    response = root_agent.send_message(query)

    print(f"Response:\n{response.text}\n")


if __name__ == "__main__":
    main()
