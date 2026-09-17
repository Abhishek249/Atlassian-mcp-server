import asyncio
import base64
import httpx
import json

async def create_jira_ticket():
    base_url = "https://picarro.atlassian.net/rest/api/3"
    email = "ajain@picarro.com"
    token = "ATATT3xFfGF0tgoXR6UAPPQCHoEyj9QQH78vSZ2-iwd4nBtnPMjZj5zsAMFVTH8HqhT3_CN8uQJaLX_Zm5yiLdaV3XKIbIkwsjcOmBqtkeUwm7McJLm_4JNLWQI5EbThIrz_IaY6TwbvIWQOFx5dBTmGqPyBNUhlkL3LxDwVCMGWk5vfqD_4v44=145948F5"
    
    auth_string = f"{email}:{token}"
    auth_b64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
    }
    
    # Use issue type ID instead of name
    payload = {
        "fields": {
            "project": {"key": "PH"},
            "summary": "[SRE] Add WO_JOB_MGMT_URL to DevInt .env for pcp-workers",
            "issuetype": {"id": "3"},  # Task
            "description": "PR #46 (PH-2286) requires WO_JOB_MGMT_URL environment variable.\n\nRequired Action: Add to DevInt .env on 10.51.50.91:\nWO_JOB_MGMT_URL=http://10.51.50.91:8001\n\nTimeline: Before deploying PH-2286 to DevInt\nImpact: Without this, AutoFOV will fail to start"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/issue",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 201:
            result = response.json()
            issue_key = result.get("key", "")
            url = f"https://picarro.atlassian.net/browse/{issue_key}"
            print(f"✅ SUCCESS! Created Jira ticket: {issue_key}")
            print(f"📋 URL: {url}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()

if __name__ == "__main__":
    asyncio.run(create_jira_ticket())
