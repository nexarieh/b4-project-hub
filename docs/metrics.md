# Metrics Tracking

Historical data and trends for project performance.

## Tracked Metrics

### Velocity
- Story points completed per sprint
- Tickets closed per week
- Sprint completion rate

### Quality
- Bug count over time
- Bug severity distribution
- Time to fix (by severity)
- Regression rate

### Code
- Lines of code changed
- Code coverage (if available)
- PR merge time
- Review turnaround

### Process
- Cycle time (created → done)
- Lead time (in progress → done)
- Blocker duration

## Planned Scripts

### collect_metrics.py
- Pull data from JIRA, GitHub
- Store in metrics.json (append mode)
- Run daily via cron

### analyze_trends.py
- Calculate averages, trends
- Identify anomalies
- Generate insights

### export_charts.py
- Generate PNG charts
- For dashboard/reports

## Data Storage
```
metrics/
├── data/
│   ├── velocity.json
│   ├── bugs.json
│   └── code.json
└── charts/
    └── (generated PNGs)
```

## Usage
```bash
# Collect today's metrics
python3 collect_metrics.py

# Analyze last 30 days
python3 analyze_trends.py --days 30

# Generate charts
python3 export_charts.py --output charts/
```
