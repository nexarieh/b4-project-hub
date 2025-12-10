# B4 Project Hub - Claude Context

## Project Purpose
Knowledge base for B4 (Beam4K) project - Nexar's 4K smart dashcam. Used by team leader to track status, priorities, and generate content.

## Key Files
- `README.md` - Main knowledge base with links, status, priorities, specs, decisions, session notes
- `SETUP.md` - MCP setup instructions

## MCP Integration
This project uses `mcp-atlassian` for Confluence/Jira access. If MCP tools aren't available:
1. Run `claude mcp list` to check status
2. If not configured, follow `SETUP.md`
3. Restart Claude Code after setup

## Confluence Spaces
- EMB space: Engineering/embedded team docs
- Release plan page ID: 4832722963

## Jira
- Project: FS (Firmware/Software)
- Board: 268

## Workflow
1. Use MCP tools to fetch latest from Confluence/Jira
2. Update README.md with current status
3. Track decisions and session notes in README.md
