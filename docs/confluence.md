# Confluence Agents

Scripts and tools for managing Confluence pages automatically.

## Planned Scripts

### release_plan.py
- Reads/updates the Release Plan page
- Syncs JIRA ticket status
- Page ID: 4832722963

### sprint_planning.py
- Creates/updates sprint planning pages
- Template: DD/MM/YYYY - Sprint [Letter] WW## Planning
- Parent page: 4495736869 (2025)
- Pulls JIRA ticket data
- Formats using standard Confluence structure

## Usage
```bash
# Update release plan
python3 release_plan.py --sync

# Create new sprint planning draft
python3 sprint_planning.py --week 51 --draft
```

## Configuration
Uses credentials from `~/.claude.json` (MCP Atlassian config)
