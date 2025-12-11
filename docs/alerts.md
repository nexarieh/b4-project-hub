# Alerts System

Automated monitoring and notifications for project health.

## Alert Types

### JIRA Alerts
- Stale tickets (no update >7 days)
- Blocked tickets without resolution
- Unassigned high-priority tickets
- SLA breaches (tickets open too long)

### GitHub Alerts
- PRs pending review >2 days
- Failed CI/CD builds
- Merge conflicts

### Milestone Alerts
- Approaching deadlines
- Scope creep detection
- Blocker accumulation

## Planned Scripts

### stale_ticket_check.py
- Scan JIRA for stale tickets
- Send notifications (Slack/email)

### build_monitor.py
- Monitor CI/CD status
- Alert on failures

### daily_health_check.py
- Run all checks
- Generate health report
- Send daily digest

## Configuration
```yaml
# alerts_config.yaml
stale_threshold_days: 7
sla_days:
  P0: 1
  P1: 3
  P2: 7
  P3: 14
slack_webhook: ${SLACK_WEBHOOK_URL}
```

## Usage
```bash
# Run all checks
python3 daily_health_check.py

# Check specific alert type
python3 stale_ticket_check.py --project FS --notify slack
```
