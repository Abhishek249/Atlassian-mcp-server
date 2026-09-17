import asyncio
import json
from atlassian_mcp_server.config import Settings
from atlassian_mcp_server.jira_client import JiraClient
from atlassian_mcp_server.tools import jira_create_issue

async def main():
    settings = Settings()
    client = JiraClient(settings)
    
    # Create the SRE ticket for WO_JOB_MGMT_URL
    args = {
        "project_key": "PH",
        "summary": "[SRE] Add WO_JOB_MGMT_URL to DevInt .env for pcp-workers",
        "issue_type": "Task",
        "description": """## Context
PR https://github.com/picarro/pcp-workers/pull/46 (PH-2286) requires WO_JOB_MGMT_URL environment variable for WO callback sensors.

## Problem
The current DevInt .env file for pcp-workers is missing this variable. Without it, the autofov-code-location container will fail to start.

## Required Action
Add the following to DevInt .env file on 10.51.50.91:

```
# WO callback sensors
WO_JOB_MGMT_URL=http://10.51.50.91:8001
```

## Location
- Host: 10.51.50.91 (CDP2-DEVINT)
- Service: pcp-workers
- File: .env (same directory as docker-compose.yml)

## Timeline
Needed BEFORE PH-2286 PR is merged and deployed to DevInt.

## Impact
- If not set: AutoFOV will fail to start
- Blocking: All boundary aggregation jobs

## References
- PR: https://github.com/picarro/pcp-workers/pull/46
- See repo: DEPLOYMENT-NOTE-WO-URL.md
""",
        "priority": "High",
        "labels": ["sre", "devint", "deployment"]
    }
    
    result = await jira_create_issue(client, args)
    print(result)

asyncio.run(main())
