# Slack Agents

Tools for analyzing B4 Slack channels and extracting insights.

## Target Channels

| Channel | ID | Purpose |
|---------|---|---------|
| #eng-beam4k | C0824FCA2GM | Main engineering discussions |
| #hw-beam4k | C054VJU0AC9 | Hardware team |
| #general-beam4k | C08M9J1S9CG | General B4 discussions |

## Planned Scripts

### channel_analyzer.py
- Fetches messages from specified channels
- Extracts key topics, decisions, blockers
- Identifies action items and mentions

### daily_digest.py
- Generates daily summary of channel activity
- Highlights important threads
- Tracks unresolved questions

## Requirements
- Slack Bot Token with channels:history scope
- MCP Slack server (optional)

## Usage
```bash
# Analyze last 24 hours
python3 channel_analyzer.py --channel eng-beam4k --hours 24

# Generate daily digest
python3 daily_digest.py --date today
```
