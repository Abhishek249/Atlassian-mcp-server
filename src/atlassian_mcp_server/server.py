"""Main server implementation."""

import logging
import sys
from typing import Any

from mcp.server import FastMCP

from .config import Settings
from .jira_client import JiraClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

# Create server instance
mcp = FastMCP("atlassian-mcp-server")
settings = Settings()
jira_client = JiraClient(settings)


@mcp.tool()
async def jira_create_issue(
    project_key: str,
    summary: str,
    issue_type: str,
    description: str = "",
    priority: str | None = None,
    assignee_email: str | None = None,
    labels: list[str] | None = None,
) -> str:
    """Create a new Jira issue with custom fields.
    
    Args:
        project_key: Project key (e.g., 'PH', 'CDP')
        summary: Issue title/summary
        issue_type: Issue type (Task, Bug, Story, Epic, etc.)
        description: Issue description (markdown supported)
        priority: Priority name (Highest, High, Medium, Low, Lowest)
        assignee_email: Assignee email address
        labels: Array of label strings
    
    Returns:
        Success message with issue key and URL
    """
    from .tools import jira_create_issue as _create
    return await _create(jira_client, {
        "project_key": project_key,
        "summary": summary,
        "issue_type": issue_type,
        "description": description,
        "priority": priority,
        "assignee_email": assignee_email,
        "labels": labels or [],
    })


@mcp.tool()
async def jira_update_issue(
    issue_key: str,
    summary: str | None = None,
    description: str | None = None,
    assignee_email: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
) -> str:
    """Update an existing Jira issue.
    
    Args:
        issue_key: Issue key (e.g., 'PH-2301')
        summary: New issue title
        description: New description
        assignee_email: New assignee email
        priority: New priority name
        labels: New labels array
    
    Returns:
        Success message
    """
    from .tools import jira_update_issue as _update
    return await _update(jira_client, {
        "issue_key": issue_key,
        "summary": summary,
        "description": description,
        "assignee_email": assignee_email,
        "priority": priority,
        "labels": labels,
    })


@mcp.tool()
async def jira_search_issues(jql: str, max_results: int = 50) -> str:
    """Search for Jira issues using JQL (Jira Query Language).
    
    Args:
        jql: Jira Query Language string
        max_results: Maximum number of results (default: 50)
    
    Returns:
        Formatted list of matching issues
    """
    from .tools import jira_search_issues as _search
    return await _search(jira_client, {"jql": jql, "max_results": max_results})


@mcp.tool()
async def jira_get_issue(issue_key: str, include_comments: bool = True) -> str:
    """Get detailed information about a Jira issue.
    
    Args:
        issue_key: Issue key (e.g., 'PH-2301')
        include_comments: Include comments (default: true)
    
    Returns:
        Detailed issue information
    """
    from .tools import jira_get_issue as _get
    return await _get(jira_client, {"issue_key": issue_key, "include_comments": include_comments})


@mcp.tool()
async def jira_add_comment(issue_key: str, comment: str) -> str:
    """Add a comment to a Jira issue.
    
    Args:
        issue_key: Issue key (e.g., 'PH-2301')
        comment: Comment text (markdown supported)
    
    Returns:
        Success message
    """
    from .tools import jira_add_comment as _comment
    return await _comment(jira_client, {"issue_key": issue_key, "comment": comment})


@mcp.tool()
async def jira_transition_issue(issue_key: str, transition_name: str) -> str:
    """Transition a Jira issue to a new status.
    
    Args:
        issue_key: Issue key (e.g., 'PH-2301')
        transition_name: Target status name (e.g., 'In Progress', 'Done')
    
    Returns:
        Success message
    """
    from .tools import jira_transition_issue as _transition
    return await _transition(jira_client, {"issue_key": issue_key, "transition_name": transition_name})


def main() -> None:
    """Main entry point."""
    try:
        logger.info("Starting Atlassian MCP Server...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
