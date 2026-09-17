import asyncio
import base64
import httpx
import json

async def get_project_info():
    base_url = "https://picarro.atlassian.net/rest/api/3"
    email = "ajain@picarro.com"
    token = "ATATT3xFfGF0tgoXR6UAPPQCHoEyj9QQH78vSZ2-iwd4nBtnPMjZj5zsAMFVTH8HqhT3_CN8uQJaLX_Zm5yiLdaV3XKIbIkwsjcOmBqtkeUwm7McJLm_4JNLWQI5EbThIrz_IaY6TwbvIWQOFx5dBTmGqPyBNUhlkL3LxDwVCMGWk5vfqD_4v44=145948F5"
    
    auth_string = f"{email}:{token}"
    auth_b64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Accept": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        # Get project metadata including issue types
        response = await client.get(
            f"{base_url}/project/PH",
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code == 200:
            project = response.json()
            print(f"Project: {project.get('name')}")
            print(f"\nAvailable Issue Types:")
            for issue_type in project.get('issueTypes', []):
                print(f"  - {issue_type.get('name')} (id: {issue_type.get('id')})")
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(get_project_info())
