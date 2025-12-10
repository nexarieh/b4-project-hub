# B4 Project Hub - Setup

## MCP Atlassian Integration

This project uses the `mcp-atlassian` MCP server to access Confluence and Jira.

### Prerequisites

1. Install mcp-atlassian:
   ```bash
   pip install mcp-atlassian
   ```

2. Get your Atlassian API token from: https://id.atlassian.com/manage-profile/security/api-tokens

### Setup MCP Server

Run this command from the project directory (`~/Git-new/b4-project-hub`):

```bash
claude mcp add atlassian -- mcp-atlassian \
  --confluence-url https://getnexar.atlassian.net/wiki \
  --jira-url https://getnexar.atlassian.net
```

Then add environment variables to the config. Edit `~/.claude.json` and find the `projects` -> `/home/ubuntu/Git-new/b4-project-hub` -> `mcpServers` -> `atlassian` section, and add:

```json
"env": {
  "CONFLUENCE_USERNAME": "your.email@getnexar.com",
  "CONFLUENCE_API_TOKEN": "your-api-token",
  "JIRA_USERNAME": "your.email@getnexar.com",
  "JIRA_API_TOKEN": "your-api-token"
}
```

### Verify Setup

```bash
claude mcp list
```

Should show:
```
atlassian: mcp-atlassian ... - ✓ Connected
```

### Restart Required

After setup, restart Claude Code for tools to be available.

## Available MCP Tools

Once configured, Claude will have access to:

- **Confluence**: Search pages, get page content, create/update pages
- **Jira**: Search issues, get issue details, create/update issues
