# Summary Agents

Tools for generating project status summaries and reports.

## Planned Scripts

### status_report.py
- Pulls data from JIRA, Confluence, and Slack
- Generates current project status
- Identifies blockers and risks

### bug_tracker.py
- Tracks bugs from BR (Bug Report) project
- Epic: Beam4 (BR-123)
- Shows tested/fix versions
- Groups by severity and component

### weekly_summary.py
- Compiles weekly progress report
- Sprint completion metrics
- Key accomplishments and blockers

## Data Sources
- JIRA: FS project (firmware), BR project (bugs), VX project
- Confluence: Release plan, Sprint planning pages
- Slack: Channel activity

## Output Formats
- Markdown (for README updates)
- JSON (for dashboard)
- Confluence (for publishing)

## Usage
```bash
# Generate current status
python3 status_report.py --output status.md

# Get bug list
python3 bug_tracker.py --epic Beam4 --format table

# Weekly summary
python3 weekly_summary.py --week 51
```
