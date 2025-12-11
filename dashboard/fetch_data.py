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


def fetch_latest_sprint_page(auth):
    """Find the latest sprint planning page from Confluence."""
    import re

    # Use CQL search for sprint planning pages
    url = 'https://getnexar.atlassian.net/wiki/rest/api/content/search'
    params = {
        'cql': 'space=EMB AND title~"Sprint" AND title~"Planning"',
        'limit': 50
    }

    response = requests.get(url, auth=auth, params=params)
    if response.status_code != 200:
        return None, None

    pages = response.json().get('results', [])

    # Filter for sprint planning pages (pattern: "DD/MM/YYYY - Sprint X WWnn Planning")
    sprint_pages = []
    for page in pages:
        title = page.get('title', '')
        # Match pattern like "15/12/2025 - Sprint Y WW51 Planning"
        match = re.search(r'WW(\d+)', title)
        if match:
            ww_num = int(match.group(1))
            sprint_pages.append({
                'id': page['id'],
                'title': title,
                'ww': ww_num
            })

    if not sprint_pages:
        return None, None

    # Sort by WW number descending and get the latest
    sprint_pages.sort(key=lambda x: x['ww'], reverse=True)
    latest = sprint_pages[0]

    return latest['id'], latest['title']


def fetch_releases(auth):
    """Fetch releases from JIRA FS project."""
    url = 'https://getnexar.atlassian.net/rest/api/3/project/FS/versions'
    response = requests.get(url, auth=auth)

    if response.status_code != 200:
        return []

    versions = response.json()

    # Filter for B4/Beam4 releases and sort by release date desc
    releases = []
    for v in versions:
        name = v.get('name', '')
        # Include B4/Beam4 versions or recent fw2-b4 versions
        if 'b4' in name.lower() or 'beam4' in name.lower():
            releases.append({
                'name': name,
                'released': v.get('released', False),
                'releaseDate': v.get('releaseDate', ''),
                'description': v.get('description', '')[:50] if v.get('description') else '',
                'url': f"https://getnexar.atlassian.net/projects/FS/versions/{v.get('id')}"
            })

    # Sort by version number (highest first)
    import re
    def version_key(r):
        # Extract version number like 7.4.60 from "fw2-b4-v7.4.60"
        match = re.search(r'v?(\d+)\.(\d+)\.(\d+)', r['name'])
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return (0, 0, 0)

    releases.sort(key=version_key, reverse=True)
    # Match milestone count (11 rows)
    result = releases[:11]
    while len(result) < 11:
        result.append({'name': '', 'released': None, 'releaseDate': '', 'description': '', 'url': '#'})
    return result


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

    # Fetch latest sprint planning page
    print("Finding latest sprint planning page...")
    sprint_id, sprint_title = fetch_latest_sprint_page(auth)
    if sprint_id:
        print(f"  Found: {sprint_title}")
    else:
        sprint_id = "5143494660"  # Fallback to WW51
        sprint_title = "Sprint Planning"
        print("  Using fallback")

    # Fetch releases
    print("Fetching B4 releases...")
    releases = fetch_releases(auth)
    print(f"  Found {len(releases)} releases")

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
            {'name': 'DVT signoff', 'status': 'done', 'date': '2025-09-08'},
            {'name': 'PVT 0.5', 'status': 'done', 'date': '2025-09-29'},
            {'name': 'PVT 1.0', 'status': 'done', 'date': '2025-10-20'},
            {'name': 'Initial FT', 'status': 'done', 'date': '2025-11-17'},
            {'name': 'Field Test 2', 'status': 'done', 'date': '2025-12-03'},
            {'name': 'Field Test 3', 'status': 'in_progress', 'date': '2025-12-11'},
            {'name': 'PVT sign-off', 'status': 'blocked', 'date': 'TBD'},
            {'name': 'MVP', 'status': 'in_progress', 'date': '2026-01-02'},
            {'name': 'Full Product', 'status': 'backlog', 'date': 'TBD'},
            {'name': '', 'status': 'empty', 'date': ''},
            {'name': '', 'status': 'empty', 'date': ''}
        ],
        'priorities': [
            {'title': 'FT Readiness: OBD issue', 'ticket': 'TBD'},
            {'title': 'MVP: Remote stream bugs', 'ticket': 'FS-3375'},
            {'title': 'MVP: Encryption', 'ticket': 'FS-3283'},
            {'title': 'MVP: HTTP Server "Teepee"', 'ticket': 'FS-2677'},
            {'title': 'Integrate new Logstore', 'ticket': 'FS-3322'}
        ],
        'releases': releases,
        'bugs': bugs,
        'tickets': tickets,
        'metrics': {
            'total_bugs': len(bugs),
            'total_tickets': len(tickets),
            'bug_status': bug_counts,
            'ticket_status': status_counts
        },
        'links': {
            'timeline': 'https://getnexar.atlassian.net/jira/software/c/projects/FS/boards/268/timeline?statuses=2%2C4&timeline=MONTHS',
            'releases_page': 'https://getnexar.atlassian.net/projects/FS?selectedItem=com.atlassian.jira.jira-projects-plugin%3Arelease-page&status=no-filter',
            'release_plan': 'https://getnexar.atlassian.net/wiki/spaces/EMB/pages/4832722963',
            'jira_board': 'https://getnexar.atlassian.net/jira/software/c/projects/FS/boards/268/backlog',
            'chicony_jira': 'https://nexar-chicony.atlassian.net/jira/core/projects/B4/board?filter=&groupBy=status',
            'dastic_jira': 'https://nexar-chicony.atlassian.net/jira/core/projects/DAS/board?filter=&groupBy=status',
            'br_bugs': 'https://getnexar.atlassian.net/jira/software/c/projects/BR/boards/287/backlog?issueParent=109691',
            'sprint_planning': f'https://getnexar.atlassian.net/wiki/spaces/EMB/pages/{sprint_id}',
            'sprint_title': sprint_title,
            'serial_numbers': 'https://docs.google.com/spreadsheets/d/1ZAwoMznI-whqYJFvrwy9SrFTTNGQiMq62E_86qvR_sw/edit?gid=243956152#gid=243956152',
            'odm_export': 'https://drive.google.com/drive/folders/1lFlqGslitGcLlwvC3xXvD4WrOqcWQ6Fh',
            'slack_eng': 'https://app.slack.com/client/T02KEL8KX/C0824FCA2GM',
            'slack_general': 'https://app.slack.com/client/T02KEL8KX/C08M9J1S9CG',
            'jenkins': 'https://ci.nexar.cloud/job/Firmware/job/build-nexar-chicony/job/b4hw-fw2/',
            'gh_chicony': 'https://github.com/getnexar/nexar-chicony',
            'gh_sdk': 'https://github.com/getnexar/nexar-client-sdk',
            'gh_hub': 'https://github.com/nexarieh/b4-project-hub',
            'gh_my_prs': 'https://github.com/pulls?q=is%3Aopen+is%3Apr+author%3Anexarieh+org%3Agetnexar',
            'gh_review_prs': 'https://github.com/pulls?q=is%3Aopen+is%3Apr+review-requested%3Anexarieh+org%3Agetnexar'
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
