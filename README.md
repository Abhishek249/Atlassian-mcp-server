# Atlassian MCP Server

A Model Context Protocol (MCP) server for Atlassian products (Jira & Confluence), enabling AI assistants to interact with your Atlassian workspace.

## Features

### Jira
- ✅ Create issues with custom fields
- ✅ Update issue status, assignee, and fields
- ✅ Search issues with JQL
- ✅ Get issue details with comments
- ✅ Add comments to issues
- ✅ Transition issues between states

### Confluence
- ✅ Create pages with rich content
- ✅ Update page content
- ✅ Search pages
- ✅ Get page content and metadata

## Architecture

```
┌─────────────────┐
│  Cursor/Claude  │
│   (MCP Client)  │
└────────┬────────┘
         │ MCP Protocol (JSON-RPC over stdio)
         ↓
┌─────────────────┐
│  MCP Server     │
│  (Python)       │
├─────────────────┤
│ • Tool handlers │
│ • Auth manager  │
│ • Rate limiting │
└────────┬────────┘
         │ REST API
         ↓
┌─────────────────┐
│  Atlassian      │
│  Cloud APIs     │
└─────────────────┘
```

## Installation

```bash
# Clone the repository
git clone <your-repo>
cd atlassian-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

Create a `.env` file or set environment variables:

```bash
# Required
ATLASSIAN_CLOUD_ID=your-domain.atlassian.net
ATLASSIAN_EMAIL=your-email@company.com
ATLASSIAN_API_TOKEN=your-api-token

# Optional
JIRA_DEFAULT_PROJECT=PH  # Default project key
MCP_LOG_LEVEL=INFO
```

### Getting Your API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "MCP Server")
4. Copy the token immediately (you won't see it again)

## Usage

### With Cursor

Add to your Cursor MCP settings (`~/.cursor/mcp_config.json`):

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "atlassian_mcp_server"],
      "env": {
        "ATLASSIAN_CLOUD_ID": "your-domain.atlassian.net",
        "ATLASSIAN_EMAIL": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-token"
      }
    }
  }
}
```

### Standalone Testing

```bash
# Run in development mode
python -m atlassian_mcp_server

# Test with MCP inspector
npx @modelcontextprotocol/inspector python -m atlassian_mcp_server
```

## Available Tools

### Jira Tools

#### `jira_create_issue`
Create a new Jira issue.

**Parameters:**
- `project_key` (required): Project key (e.g., "PH", "CDP")
- `summary` (required): Issue title
- `issue_type` (required): Issue type (Task, Bug, Story, etc.)
- `description` (optional): Issue description (Atlassian Document Format)
- `priority` (optional): Priority name (High, Medium, Low)
- `assignee_email` (optional): Assignee email address
- `labels` (optional): Array of label strings

**Example:**
```python
{
  "project_key": "PH",
  "summary": "Add WO_JOB_MGMT_URL to DevInt",
  "issue_type": "Task",
  "description": "Enable processing_status updates...",
  "priority": "High",
  "labels": ["sre", "devint"]
}
```

#### `jira_update_issue`
Update an existing Jira issue.

**Parameters:**
- `issue_key` (required): Issue key (e.g., "PH-2301")
- `summary` (optional): New title
- `description` (optional): New description
- `assignee_email` (optional): New assignee
- `priority` (optional): New priority
- `status` (optional): New status (triggers transition)

#### `jira_search_issues`
Search for issues using JQL.

**Parameters:**
- `jql` (required): Jira Query Language string
- `max_results` (optional): Max results (default: 50)

**Example:**
```python
{
  "jql": "project = PH AND status = 'In Progress' AND assignee = currentUser()",
  "max_results": 20
}
```

#### `jira_get_issue`
Get detailed information about an issue.

**Parameters:**
- `issue_key` (required): Issue key (e.g., "PH-2301")
- `include_comments` (optional): Include comments (default: true)

#### `jira_add_comment`
Add a comment to an issue.

**Parameters:**
- `issue_key` (required): Issue key
- `comment` (required): Comment text (markdown supported)

#### `jira_transition_issue`
Transition an issue to a new status.

**Parameters:**
- `issue_key` (required): Issue key
- `transition_name` (required): Target status name

### Confluence Tools

#### `confluence_create_page`
Create a new Confluence page.

**Parameters:**
- `space_key` (required): Space key
- `title` (required): Page title
- `content` (required): Page content (Atlassian Document Format)
- `parent_page_id` (optional): Parent page ID

#### `confluence_update_page`
Update an existing Confluence page.

**Parameters:**
- `page_id` (required): Page ID
- `title` (optional): New title
- `content` (optional): New content
- `version` (required): Current page version (for optimistic locking)

#### `confluence_search_pages`
Search for Confluence pages.

**Parameters:**
- `query` (required): Search query (CQL)
- `max_results` (optional): Max results (default: 25)

#### `confluence_get_page`
Get a Confluence page's content and metadata.

**Parameters:**
- `page_id` (required): Page ID

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Type checking
mypy src/

# Linting
ruff check src/

# Format code
black src/
```

## Error Handling

The server implements comprehensive error handling:

- **Authentication errors**: Clear messages when credentials are invalid
- **Rate limiting**: Automatic backoff and retry with exponential delay
- **Network errors**: Graceful degradation with informative error messages
- **Validation errors**: Parameter validation before API calls

## Rate Limiting

The server respects Atlassian's rate limits:
- Jira Cloud: 10 requests/second per user
- Confluence Cloud: 5 requests/second per user

Automatic throttling and retry logic is implemented.

## Security

- ✅ API tokens stored in environment variables (never in code)
- ✅ Secure communication over HTTPS only
- ✅ Token validation on startup
- ✅ Input sanitization to prevent injection attacks
- ✅ No logging of sensitive data

## Resume Highlights

**Key Technical Skills Demonstrated:**
- Model Context Protocol (MCP) implementation
- REST API integration (Atlassian Cloud APIs)
- Authentication & authorization (API tokens, OAuth)
- Async I/O with Python's asyncio
- Error handling & resilience patterns
- Rate limiting & throttling
- Type safety with Python type hints
- Test-driven development
- Documentation & API design

**Technologies:**
- Python 3.11+
- MCP SDK (@modelcontextprotocol/sdk)
- Atlassian REST APIs (Jira, Confluence)
- JSON-RPC 2.0
- HTTP/REST
- Environment-based configuration

## License

MIT

## Author

Ajay Jain

## Contributing

Contributions welcome! Please open an issue or PR.

## Roadmap

- [ ] OAuth 2.0 support (in addition to API tokens)
- [ ] Jira Service Management integration
- [ ] Bitbucket integration
- [ ] Webhook support for real-time updates
- [ ] Caching for frequently accessed data
- [ ] Bulk operations support
- [ ] Advanced JQL query builder
