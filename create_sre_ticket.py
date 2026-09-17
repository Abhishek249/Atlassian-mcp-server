import asyncio
import base64
import httpx
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    atlassian_cloud_id: str = "picarro.atlassian.net"
    atlassian_email: str = "ajain@picarro.com"
    atlassian_api_token: str = "ATATT3xFfGF0tgoXR6UAPPQCHoEyj9QQH78vSZ2-iwd4nBtnPMjZj5zsAMFVTH8HqhT3_CN8uQJaLX_Zm5yiLdaV3XKIbIkwsjcOmBqtkeUwm7McJLm_4JNLWQI5EbThIrz_IaY6TwbvIWQOFx5dBTmGqPyBNUhlkL3LxDwVCMGWk5vfqD_4v44=145948F5"

async def create_jira_ticket():
    settings = Settings()
    base_url = f"https://{settings.atlassian_cloud_id}/rest/api/3"
    
    # Create auth header
    auth_string = f"{settings.atlassian_email}:{settings.atlassian_api_token}"
    auth_bytes = auth_string.encode("utf-8")
    auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Create ticket payload
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
                        "content": [{"type": "text", "text": "PR https://github.com/picarro/pcp-workers/pull/46 (PH-2286) requires WO_JOB_MGMT_URL environment variable for WO callback sensors."}]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Required Action"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Add the following to DevInt .env file on 10.51.50.91:"}]
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [{"type": "text", "text": "WO_JOB_MGMT_URL=http://10.51.50.91:8001"}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Timeline: Needed BEFORE PH-2286 PR is deployed to DevInt."}]
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Impact: Without this, AutoFOV code-location will fail to start, blocking all boundary aggregation jobs."}]
                    }
                ]
            },
            "priority": {"name": "High"},
            "labels": ["sre", "devint", "deployment"]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/issue",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()
        
        issue_key = result.get("key", "")
        issue_id = result.get("id", "")
        url = f"https://{settings.atlassian_cloud_id}/browse/{issue_key}"
        
        print(f"✅ Created Jira ticket: {issue_key}")
        print(f"📋 URL: {url}")
        print(f"🎫 Issue ID: {issue_id}")
        return result

if __name__ == "__main__":
    asyncio.run(create_jira_ticket())
