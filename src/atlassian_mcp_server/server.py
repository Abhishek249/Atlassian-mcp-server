"""Main server implementation."""

import asyncio
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import Settings
from .jira_client import JiraClient
from .tools import (
    jira_add_comment,
    jira_create_issue,
    jira_get_issue,
    jira_search_issues,
    jira_transition_issue,
    jira_update_issue,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("atlassian-mcp-server")
    settings = Settings()
    jira_client = JiraClient(settings)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            Tool(
                name="jira_create_issue",
                description="Create a new Jira issue with custom fields",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_key": {
                            "type": "string",
                            "description": "Project key (e.g., 'PH', 'CDP')",
                        },
                        "summary": {
                            "type": "string",
                            "description": "Issue title/summary",
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Issue type (Task, Bug, Story, Epic, etc.)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Issue description (markdown supported)",
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority name (Highest, High, Medium, Low, Lowest)",
                        },
                        "assignee_email": {
                            "type": "string",
                            "description": "Assignee email address",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of label strings",
                        },
                    },
                    "required": ["project_key", "summary", "issue_type"],
                },
            ),
            Tool(
                name="jira_update_issue",
                description="Update an existing Jira issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "Issue key (e.g., 'PH-2301')",
                        },
                        "summary": {"type": "string", "description": "New issue title"},
                        "description": {"type": "string", "description": "New description"},
                        "assignee_email": {"type": "string", "description": "New assignee email"},
                        "priority": {"type": "string", "description": "New priority name"},
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New labels array",
                        },
                    },
                    "required": ["issue_key"],
                },
            ),
            Tool(
                name="jira_search_issues",
                description="Search for Jira issues using JQL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "jql": {
                            "type": "string",
                            "description": "Jira Query Language string",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 50)",
                            "default": 50,
                        },
                    },
                    "required": ["jql"],
                },
            ),
            Tool(
                name="jira_get_issue",
                description="Get detailed information about a Jira issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "Issue key (e.g., 'PH-2301')",
                        },
                        "include_comments": {
                            "type": "boolean",
                            "description": "Include comments (default: true)",
                            "default": True,
                        },
                    },
                    "required": ["issue_key"],
                },
            ),
            Tool(
                name="jira_add_comment",
                description="Add a comment to a Jira issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "Issue key (e.g., 'PH-2301')",
                        },
                        "comment": {
                            "type": "string",
                            "description": "Comment text (markdown supported)",
                        },
                    },
                    "required": ["issue_key", "comment"],
                },
            ),
            Tool(
                name="jira_transition_issue",
                description="Transition a Jira issue to a new status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "Issue key (e.g., 'PH-2301')",
                        },
                        "transition_name": {
                            "type": "string",
                            "description": "Target status name (e.g., 'In Progress', 'Done')",
                        },
                    },
                    "required": ["issue_key", "transition_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        try:
            if name == "jira_create_issue":
                result = await jira_create_issue(jira_client, arguments)
            elif name == "jira_update_issue":
                result = await jira_update_issue(jira_client, arguments)
            elif name == "jira_search_issues":
                result = await jira_search_issues(jira_client, arguments)
            elif name == "jira_get_issue":
                result = await jira_get_issue(jira_client, arguments)
            elif name == "jira_add_comment":
                result = await jira_add_comment(jira_client, arguments)
            elif name == "jira_transition_issue":
                result = await jira_transition_issue(jira_client, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def run_server() -> None:
    """Run the MCP server."""
    logger.info("Starting Atlassian MCP Server...")
    server = create_server()

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio")
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
