#!/usr/bin/env python3
"""
B4 Dashboard Data Fetcher
Pulls data from JIRA and saves as JSON for the dashboard.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth


def get_credentials():
    """Load credentials from Claude config."""
    config_path = os.path.expanduser('~/.claude.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    proj_config = config.get('projects', {}).get('/home/ubuntu/Git-new/b4-project-hub', {})
    mcp_config = proj_config.get('mcpServers', {}).get('atlassian', {})
    env = mcp_config.get('env', {})

    return {
        'username': env.get('JIRA_USERNAME'),
        'token': env.get('JIRA_API_TOKEN')
    }


def fetch_jira_issues(auth, jql, max_results=50):
    """Fetch issues from JIRA."""
    url = 'https://getnexar.atlassian.net/rest/api/3/search/jql'
    params = {
        'jql': jql,
        'maxResults': max_results,
        'fields': 'summary,status,priority,assignee,created,updated,fixVersions,labels'
    }

    response = requests.get(url, auth=auth, params=params)
    if response.status_code == 200:
        return response.json().get('issues', [])
    return []


def fetch_b4_bugs(auth):
    """Fetch B4 bugs from BR project."""
    jql = 'project = BR AND (summary ~ "Beam4" OR summary ~ "B4") AND status not in (Done, Closed) ORDER BY created DESC'
    issues = fetch_jira_issues(auth, jql, 30)

    bugs = []
    for issue in issues:
        fields = issue['fields']
        bugs.append({
            'key': issue['key'],
            'summary': fields.get('summary', '')[:60],
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'priority': fields.get('priority', {}).get('name', 'Unknown') if fields.get('priority') else 'Unknown',
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'created': fields.get('created', '')[:10],
            'url': f"https://getnexar.atlassian.net/browse/{issue['key']}"
        })

    return bugs


def fetch_fs_tickets(auth):
    """Fetch B4 tickets from FS project."""
    jql = 'project = FS AND (summary ~ "B4" OR summary ~ "Beam4K") AND status not in (Done, Closed) ORDER BY priority ASC, updated DESC'
    issues = fetch_jira_issues(auth, jql, 40)

    tickets = []
    for issue in issues:
        fields = issue['fields']
        tickets.append({
            'key': issue['key'],
            'summary': fields.get('summary', '')[:55],
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'priority': fields.get('priority', {}).get('name', 'Unknown') if fields.get('priority') else 'Unknown',
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'url': f"https://getnexar.atlassian.net/browse/{issue['key']}"
        })

    return tickets


def get_status_counts(tickets):
    """Count tickets by status."""
    counts = {}
    for t in tickets:
        status = t['status']
        counts[status] = counts.get(status, 0) + 1
    return counts


def main():
    print("B4 Dashboard Data Fetcher")
    print("=" * 40)

    # Get credentials
    creds = get_credentials()
    if not creds['username'] or not creds['token']:
        print("Error: Could not load credentials from ~/.claude.json")
        return

    auth = HTTPBasicAuth(creds['username'], creds['token'])

    # Create data directory
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)

    # Fetch bugs
    print("Fetching BR bugs...")
    bugs = fetch_b4_bugs(auth)
    print(f"  Found {len(bugs)} bugs")

    # Fetch FS tickets
    print("Fetching FS tickets...")
    tickets = fetch_fs_tickets(auth)
    print(f"  Found {len(tickets)} tickets")

    # Calculate metrics
    status_counts = get_status_counts(tickets)
    bug_counts = get_status_counts(bugs)

    # Build dashboard data
    dashboard_data = {
        'updated': datetime.now().isoformat(),
        'project': {
            'name': 'Beam4K (B4)',
            'phase': 'Field Test 3 / MVP Development',
            'blocker': 'PVT sign-off waiting on Chicony samples'
        },
        'milestones': [
            {'name': 'DVT signoff', 'status': 'done'},
            {'name': 'PVT 0.5', 'status': 'done'},
            {'name': 'PVT 1.0', 'status': 'done'},
            {'name': 'Initial FT', 'status': 'done'},
            {'name': 'Field Test 2', 'status': 'done'},
            {'name': 'Field Test 3', 'status': 'in_progress'},
            {'name': 'PVT sign-off', 'status': 'blocked'},
            {'name': 'MVP', 'status': 'in_progress'},
            {'name': 'Full Product', 'status': 'backlog'}
        ],
        'priorities': [
            {'title': 'FT Readiness: OBD issue', 'ticket': 'TBD'},
            {'title': 'FT Readiness: Support HWK (MCU)', 'ticket': 'FS-3051'},
            {'title': 'MVP: Remote stream bugs', 'ticket': 'FS-3375'},
            {'title': 'MVP: Encryption', 'ticket': 'FS-3283'},
            {'title': 'MVP: HTTP Server "Teepee"', 'ticket': 'FS-2677'}
        ],
        'bugs': bugs,
        'tickets': tickets,
        'metrics': {
            'total_bugs': len(bugs),
            'total_tickets': len(tickets),
            'bug_status': bug_counts,
            'ticket_status': status_counts
        },
        'links': {
            'release_plan': 'https://getnexar.atlassian.net/wiki/spaces/EMB/pages/4832722963',
            'jira_board': 'https://getnexar.atlassian.net/jira/software/c/projects/FS/boards/268/backlog',
            'br_bugs': 'https://getnexar.atlassian.net/jira/software/c/projects/BR/boards/287/backlog?issueParent=109691',
            'sprint_ww51': 'https://getnexar.atlassian.net/wiki/spaces/EMB/pages/5143494660',
            'serial_numbers': 'https://docs.google.com/spreadsheets/d/1ZAwoMznI-whqYJFvrwy9SrFTTNGQiMq62E_86qvR_sw/edit?gid=243956152#gid=243956152',
            'odm_export': 'https://drive.google.com/drive/folders/1lFlqGslitGcLlwvC3xXvD4WrOqcWQ6Fh',
            'slack_eng': 'https://app.slack.com/client/T02KEL8KX/C0824FCA2GM'
        }
    }

    # Save data
    output_file = data_dir / 'dashboard.json'
    with open(output_file, 'w') as f:
        json.dump(dashboard_data, f, indent=2)

    print(f"\nData saved to: {output_file}")
    print(f"Total bugs: {len(bugs)}")
    print(f"Total tickets: {len(tickets)}")


if __name__ == '__main__':
    main()
