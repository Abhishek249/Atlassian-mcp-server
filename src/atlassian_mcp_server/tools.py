"""Tool implementations for Jira operations."""

import json
import logging
from typing import Any

from .jira_client import JiraClient

logger = logging.getLogger(__name__)


def markdown_to_adf(markdown: str) -> dict[str, Any]:
    """
    Convert markdown to Atlassian Document Format (ADF).
    
    Simple conversion for common markdown elements.
    For production, consider using a proper markdown->ADF library.
    """
    # Split into paragraphs
    paragraphs = [p.strip() for p in markdown.split("\n\n") if p.strip()]
    
    content: list[dict[str, Any]] = []
    
    for para in paragraphs:
        if para.startswith("# "):
            # Heading 1
            content.append({
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": para[2:]}]
            })
        elif para.startswith("## "):
            # Heading 2
            content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": para[3:]}]
            })
        elif para.startswith("### "):
            # Heading 3
            content.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": para[4:]}]
            })
        elif para.startswith("```"):
            # Code block
            lines = para.split("\n")
            language = lines[0][3:].strip() if len(lines[0]) > 3 else ""
            code_text = "\n".join(lines[1:-1]) if para.endswith("```") else "\n".join(lines[1:])
            content.append({
                "type": "codeBlock",
                "attrs": {"language": language or "text"},
                "content": [{"type": "text", "text": code_text}]
            })
        elif para.startswith("- ") or para.startswith("* "):
            # Bullet list
            items = [line[2:] for line in para.split("\n") if line.startswith(("- ", "* "))]
            content.append({
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": item}]}]
                    }
                    for item in items
                ]
            })
        else:
            # Regular paragraph
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": para}]
            })
    
    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


async def jira_create_issue(client: JiraClient, args: dict[str, Any]) -> str:
    """Create a new Jira issue."""
    project_key = args["project_key"]
    summary = args["summary"]
    issue_type = args["issue_type"]
    
    # Build fields
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }
    
    # Add description if provided
    if "description" in args:
        fields["description"] = markdown_to_adf(args["description"])
    
    # Add priority if provided
    if "priority" in args:
        fields["priority"] = {"name": args["priority"]}
    
    # Add assignee if provided
    if "assignee_email" in args:
        fields["assignee"] = {"emailAddress": args["assignee_email"]}
    
    # Add labels if provided
    if "labels" in args:
        fields["labels"] = args["labels"]
    
    payload = {"fields": fields}
    
    try:
        result = await client.post("/issue", json=payload)
        issue_key = result.get("key", "")
        issue_id = result.get("id", "")
        url = f"https://{client.settings.atlassian_cloud_id}/browse/{issue_key}"
        
        return json.dumps({
            "success": True,
            "issue_key": issue_key,
            "issue_id": issue_id,
            "url": url,
            "message": f"Created issue {issue_key}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to create issue: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def jira_update_issue(client: JiraClient, args: dict[str, Any]) -> str:
    """Update an existing Jira issue."""
    issue_key = args["issue_key"]
    
    fields: dict[str, Any] = {}
    
    if "summary" in args:
        fields["summary"] = args["summary"]
    
    if "description" in args:
        fields["description"] = markdown_to_adf(args["description"])
    
    if "priority" in args:
        fields["priority"] = {"name": args["priority"]}
    
    if "assignee_email" in args:
        fields["assignee"] = {"emailAddress": args["assignee_email"]}
    
    if "labels" in args:
        fields["labels"] = args["labels"]
    
    if not fields:
        return json.dumps({
            "success": False,
            "error": "No fields to update"
        }, indent=2)
    
    try:
        await client.put(f"/issue/{issue_key}", json={"fields": fields})
        url = f"https://{client.settings.atlassian_cloud_id}/browse/{issue_key}"
        
        return json.dumps({
            "success": True,
            "issue_key": issue_key,
            "url": url,
            "message": f"Updated issue {issue_key}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to update issue: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def jira_search_issues(client: JiraClient, args: dict[str, Any]) -> str:
    """Search for Jira issues using JQL."""
    jql = args["jql"]
    max_results = args.get("max_results", 50)
    
    try:
        result = await client.get(
            "/search",
            params={
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,assignee,priority,created,updated",
            }
        )
        
        issues = result.get("issues", [])
        total = result.get("total", 0)
        
        formatted_issues = []
        for issue in issues:
            fields = issue.get("fields", {})
            formatted_issues.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name"),
                "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                "created": fields.get("created"),
                "updated": fields.get("updated"),
                "url": f"https://{client.settings.atlassian_cloud_id}/browse/{issue.get('key')}"
            })
        
        return json.dumps({
            "success": True,
            "total": total,
            "returned": len(issues),
            "issues": formatted_issues
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to search issues: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def jira_get_issue(client: JiraClient, args: dict[str, Any]) -> str:
    """Get detailed information about a Jira issue."""
    issue_key = args["issue_key"]
    include_comments = args.get("include_comments", True)
    
    expand = "changelog" if include_comments else ""
    
    try:
        result = await client.get(
            f"/issue/{issue_key}",
            params={"expand": expand} if expand else {}
        )
        
        fields = result.get("fields", {})
        
        issue_data = {
            "key": result.get("key"),
            "summary": fields.get("summary"),
            "description": fields.get("description"),
            "status": fields.get("status", {}).get("name"),
            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
            "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
            "labels": fields.get("labels", []),
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "url": f"https://{client.settings.atlassian_cloud_id}/browse/{issue_key}"
        }
        
        # Add comments if requested
        if include_comments:
            comments_result = await client.get(f"/issue/{issue_key}/comment")
            comments = comments_result.get("comments", [])
            issue_data["comments"] = [
                {
                    "author": c.get("author", {}).get("displayName"),
                    "body": c.get("body"),
                    "created": c.get("created")
                }
                for c in comments
            ]
        
        return json.dumps({
            "success": True,
            "issue": issue_data
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to get issue: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def jira_add_comment(client: JiraClient, args: dict[str, Any]) -> str:
    """Add a comment to a Jira issue."""
    issue_key = args["issue_key"]
    comment_text = args["comment"]
    
    payload = {
        "body": markdown_to_adf(comment_text)
    }
    
    try:
        result = await client.post(f"/issue/{issue_key}/comment", json=payload)
        comment_id = result.get("id", "")
        
        return json.dumps({
            "success": True,
            "comment_id": comment_id,
            "message": f"Added comment to {issue_key}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to add comment: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


async def jira_transition_issue(client: JiraClient, args: dict[str, Any]) -> str:
    """Transition a Jira issue to a new status."""
    issue_key = args["issue_key"]
    transition_name = args["transition_name"]
    
    try:
        # Get available transitions
        transitions_result = await client.get(f"/issue/{issue_key}/transitions")
        transitions = transitions_result.get("transitions", [])
        
        # Find matching transition
        transition_id = None
        for t in transitions:
            if t.get("name", "").lower() == transition_name.lower():
                transition_id = t.get("id")
                break
        
        if not transition_id:
            available = [t.get("name") for t in transitions]
            return json.dumps({
                "success": False,
                "error": f"Transition '{transition_name}' not available",
                "available_transitions": available
            }, indent=2)
        
        # Execute transition
        await client.post(
            f"/issue/{issue_key}/transitions",
            json={"transition": {"id": transition_id}}
        )
        
        return json.dumps({
            "success": True,
            "issue_key": issue_key,
            "transition": transition_name,
            "message": f"Transitioned {issue_key} to {transition_name}"
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed to transition issue: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)
