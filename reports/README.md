# Reports Generator

Formatted reports for stakeholders and meetings.

## Report Types

### Weekly Status Report
- Sprint progress
- Key accomplishments
- Blockers and risks
- Next week priorities

### Release Report
- Version summary
- Features included
- Known issues
- Test results

### Bug Report
- Open bugs by severity
- Bug trends
- Fix rate
- Oldest open bugs

### Executive Summary
- High-level project status
- Milestone progress
- Key metrics
- Risk assessment

## Output Formats

| Format | Use Case |
|--------|----------|
| Markdown | README, Confluence |
| HTML | Email, browser |
| PDF | Attachments, printing |
| JSON | API, dashboard |

## Planned Scripts

### weekly_report.py
- Compile data from all sources
- Format for stakeholders
- Optional email send

### release_report.py
- Generate release notes
- Include JIRA tickets
- Test summary

### generate_pdf.py
- Convert markdown to PDF
- Apply branding/template

## Templates
```
reports/
├── templates/
│   ├── weekly.md.j2
│   ├── release.md.j2
│   └── executive.md.j2
└── output/
    └── (generated reports)
```

## Usage
```bash
# Generate weekly report
python3 weekly_report.py --week 51 --format markdown

# Generate release report
python3 release_report.py --version 7.4.60 --format pdf

# Email report
python3 weekly_report.py --week 51 --email stakeholders@company.com
```
