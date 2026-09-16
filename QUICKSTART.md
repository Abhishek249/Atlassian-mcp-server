# Quick Start Guide

## Prerequisites
- Python 3.11 or higher
- Atlassian Cloud account
- Jira API token

## Setup (5 minutes)

### 1. Get Your Atlassian API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Give it a name (e.g., "MCP Server")
4. Copy the token (save it securely - you won't see it again!)

### 2. Install the Server

```bash
# Clone the repository
cd /Users/ajain/pcp-repos/atlassian-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use your favorite editor
```

Edit `.env`:
```bash
ATLASSIAN_CLOUD_ID=picarro.atlassian.net
ATLASSIAN_EMAIL=your-email@picarro.com
ATLASSIAN_API_TOKEN=your-token-here
JIRA_DEFAULT_PROJECT=PH
```

### 4. Test the Server

```bash
# Run the server
python -m atlassian_mcp_server
```

You should see:
```
2026-09-16 13:00:00 - atlassian_mcp_server.server - INFO - Starting Atlassian MCP Server...
2026-09-16 13:00:00 - atlassian_mcp_server.server - INFO - Server running on stdio
```

Press Ctrl+C to stop.

### 5. Configure Cursor

Add to `~/.cursor/mcp_config.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "/Users/ajain/pcp-repos/atlassian-mcp-server/venv/bin/python",
      "args": ["-m", "atlassian_mcp_server"],
      "env": {
        "ATLASSIAN_CLOUD_ID": "picarro.atlassian.net",
        "ATLASSIAN_EMAIL": "your-email@picarro.com",
        "ATLASSIAN_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

### 6. Restart Cursor

1. Close Cursor completely
2. Reopen Cursor
3. The Atlassian MCP server should now be available!

## Usage Examples

### Create a Jira Issue

In Cursor chat:
```
Create a Jira issue in project PH:
- Title: "Test MCP integration"
- Type: Task
- Description: "Testing my custom MCP server"
- Priority: High
```

### Search Issues

```
Search for all PH issues assigned to me that are in progress
```

### Get Issue Details

```
Get details for PH-2301
```

### Add Comment

```
Add a comment to PH-2301: "Working on this now"
```

## Troubleshooting

### Server Won't Start

**Check Python version:**
```bash
python3 --version  # Should be 3.11+
```

**Check dependencies:**
```bash
pip list | grep mcp
```

**Check environment variables:**
```bash
source venv/bin/activate
python -c "from atlassian_mcp_server.config import Settings; s = Settings(); print(s.atlassian_cloud_id)"
```

### Authentication Errors

**Verify credentials:**
```bash
curl -u "your-email@picarro.com:your-token" \
  https://picarro.atlassian.net/rest/api/3/myself
```

Should return your user info.

### Cursor Not Finding Server

**Check MCP config location:**
```bash
ls -la ~/.cursor/mcp_config.json
```

**Check server path:**
```bash
which python  # Make sure it's the venv python
```

**Check Cursor logs:**
- Open Cursor
- Help → Toggle Developer Tools
- Look for MCP errors in console

## Next Steps

- [ ] Create a test issue
- [ ] Search for issues
- [ ] Add comments
- [ ] Update issue status
- [ ] Explore other tools

## Resume Points

✅ Built production-ready MCP server
✅ Implemented REST API integration (Jira)
✅ Added authentication & rate limiting
✅ Async I/O with Python asyncio
✅ Type safety with Pydantic
✅ Error handling & resilience
✅ Documentation & examples

**GitHub:** github.com/yourusername/atlassian-mcp-server

---

Need help? Check the main README.md or open an issue!
