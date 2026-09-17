import asyncio
import json
import sys
sys.path.insert(0, '/app/src')

from atlassian_mcp_server.config import Settings
from atlassian_mcp_server.jira_client import JiraClient

async def main():
    settings = Settings()
    client = JiraClient(settings)
    
    # Create the SRE ticket
    payload = {
        "fields": {
            "project": {"key": "PH"},
            "summary": "[SRE] Add WO_JOB_MGMT_URL to DevInt .env for pcp-workers",
            "issuetype": {"name": "Task"},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "PR https://github.com/picarro/pcp-workers/pull/46 (PH-2286) requires WO_JOB_MGMT_URL environment variable."}]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Required Action"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Add to DevInt .env on 10.51.50.91:"}]
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [{"type": "text", "text": "WO_JOB_MGMT_URL=http://10.51.50.91:8001"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Needed BEFORE PH-2286 is deployed to DevInt."}]
                    }
                ]
            },
            "priority": {"name": "High"},
            "labels": ["sre", "devint", "deployment"]
        }
    }
    
    result = await client.post("/issue", json=payload)
    issue_key = result.get("key", "")
    url = f"https://{settings.atlassian_cloud_id}/browse/{issue_key}"
    print(f"✅ Created ticket: {issue_key}")
    print(f"📋 URL: {url}")
    return result

asyncio.run(main())
