# Cursor MCP Integration Setup Guide

## ✅ Status: MCP Server is Ready!

The Atlassian MCP server is now fully functional and tested. It exposes 6 Jira tools to AI assistants via the Model Context Protocol.

## Quick Start

### 1. Verify Server Works

```bash
cd /Users/ajain/pcp-repos/atlassian-mcp-server
python3 test_mcp_integration.py
```

You should see:
```
✅ Server initialized successfully!
✅ Found 6 tools
🎉 MCP Server is fully operational!
```

### 2. Cursor Configuration

The MCP server is already configured in Cursor at:
```
~/.cursor/mcp_config.json
```

Current configuration:
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "python3",
      "args": ["-m", "atlassian_mcp_server"],
      "cwd": "/Users/ajain/pcp-repos/atlassian-mcp-server",
      "env": {
        "ATLASSIAN_CLOUD_ID": "picarro.atlassian.net",
        "ATLASSIAN_EMAIL": "ajain@picarro.com",
        "ATLASSIAN_API_TOKEN": "ATATT3x...",
        "JIRA_DEFAULT_PROJECT": "PH",
        "MCP_LOG_LEVEL": "INFO",
        "PYTHONPATH": "/Users/ajain/pcp-repos/atlassian-mcp-server/src"
      }
    }
  }
}
```

### 3. Restart Cursor

After any changes to `mcp_config.json`, restart Cursor completely to pick up the new configuration.

### 4. Test in Chat

Once Cursor restarts, you can use natural language to interact with Jira:

**Examples:**
- "Search for PH issues assigned to me"
- "Create a new PH task titled 'Fix login bug' with priority High"
- "Show me details for issue PH-2305"
- "Add a comment to PH-2301 saying 'Starting work on this'"
- "Transition PH-2300 to In Progress"

The AI will automatically:
1. Understand your request
2. Choose the appropriate Jira tool
3. Call the MCP server with correct parameters
4. Return formatted results

## Available Tools

| Tool | Description |
|------|-------------|
| `jira_create_issue` | Create new Jira issues with fields |
| `jira_update_issue` | Update existing issue fields |
| `jira_search_issues` | Search using JQL queries |
| `jira_get_issue` | Get detailed issue information |
| `jira_add_comment` | Add comments to issues |
| `jira_transition_issue` | Move issues between statuses |

## Technical Details

### Architecture
- **Protocol**: Model Context Protocol (MCP) 2024-11-05
- **Transport**: stdio (JSON-RPC over stdin/stdout)
- **SDK**: FastMCP 4.x (MCP SDK v2)
- **Language**: Python 3.11+

### How It Works

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│   Cursor    │ stdio   │  MCP Server  │  HTTPS  │    Jira    │
│  (AI Chat)  ├────────►│   (Python)   ├────────►│ REST API   │
└─────────────┘         └──────────────┘         └────────────┘
       │                        │                       │
       │ 1. User asks question  │                       │
       │────────────────────────┤                       │
       │                        │ 2. AI chooses tool    │
       │◄───────────────────────┤                       │
       │                        │ 3. MCP call           │
       │────────────────────────►                       │
       │                        │ 4. API request        │
       │                        ├──────────────────────►│
       │                        │ 5. API response       │
       │                        │◄──────────────────────┤
       │ 6. Formatted result    │                       │
       │◄───────────────────────┤                       │
```

### Code Structure

```
atlassian-mcp-server/
├── src/atlassian_mcp_server/
│   ├── __init__.py
│   ├── server.py          # FastMCP server with @mcp.tool() decorators
│   ├── config.py          # Pydantic settings from env vars
│   ├── jira_client.py     # Async HTTP client for Jira API
│   └── tools.py           # Jira tool implementations
├── test_mcp_integration.py # Integration test
└── pyproject.toml
```

## Troubleshooting

### MCP Server Not Found in Cursor

1. Check config path: `cat ~/.cursor/mcp_config.json`
2. Verify Python path: `which python3`
3. Test server manually: `python3 test_mcp_integration.py`
4. Check Cursor logs: `~/.cursor/logs/`

### Tools Not Appearing

1. Restart Cursor completely (Cmd+Q, then reopen)
2. Check server is running: Look for MCP status in Cursor UI
3. Verify PYTHONPATH in config includes `src/` directory

### API Authentication Errors

1. Check token is valid: Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Verify email matches: Must be your Atlassian account email
3. Test with standalone script: `python3 create_ticket_simple.py`

### JQL Search Syntax

Common queries:
```
project = PH AND assignee = currentUser()
project = PH AND status = "Ready for QA"
project = CDP AND created >= -7d
assignee = currentUser() AND status != Done
```

## Migration Notes

### Changes from v1

We migrated from MCP SDK v1 to v2:
- ✅ Replaced `@server.list_tools()` with `@mcp.tool()` decorators
- ✅ Removed manual JSON Schema definitions (auto-generated from type hints)
- ✅ Simplified tool registration (no more dispatch chains)
- ✅ Updated to use `FastMCP` high-level API
- ✅ Changed from `asyncio.run()` to synchronous `mcp.run()`

### What's New

- **Auto-generated schemas**: Function signatures → JSON Schema
- **Better DX**: Docstrings → tool descriptions
- **Type safety**: Pydantic validation on all inputs
- **Cleaner code**: 70% less boilerplate

## Next Steps

### Potential Enhancements

1. **Add more Jira tools**:
   - Bulk operations
   - Attachment management
   - Sprint operations
   - Project creation

2. **Add Confluence support**:
   - Page creation/updates
   - Search
   - Space management

3. **Caching**:
   - Cache project metadata
   - Cache issue types
   - Reduce API calls

4. **Better error messages**:
   - Suggest valid values
   - Auto-retry on rate limits

## Support

- **Repo**: https://github.com/Abhishek249/Atlassian-mcp-server
- **MCP Docs**: https://modelcontextprotocol.io
- **FastMCP Docs**: https://gofastmcp.com
- **Jira API**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/

---

Last updated: 2026-09-16
Status: ✅ Production Ready
