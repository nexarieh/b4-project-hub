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
    """Fetch FW and MCU releases from JIRA FS project."""
    import re

    url = 'https://getnexar.atlassian.net/rest/api/3/project/FS/versions'
    response = requests.get(url, auth=auth)

    if response.status_code != 200:
        return [], []

    versions = response.json()

    fw_releases = []
    mcu_releases = []

    for v in versions:
        name = v.get('name', '')
        release_data = {
            'name': name,
            'released': v.get('released', False),
            'releaseDate': v.get('releaseDate', ''),
            'description': v.get('description', '')[:50] if v.get('description') else '',
            'url': f"https://getnexar.atlassian.net/projects/FS/versions/{v.get('id')}"
        }

        # Categorize releases
        name_lower = name.lower()
        if name_lower.startswith('mcu-'):
            mcu_releases.append(release_data)
        elif 'fw2-b4' in name_lower or 'b4 dvt' in name_lower:
            fw_releases.append(release_data)

    def fw_version_key(r):
        # Extract version number like 7.4.60 from "fw2-b4-v7.4.60"
        match = re.search(r'v?(\d+)\.(\d+)\.(\d+)', r['name'])
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return (0, 0, 0)

    def mcu_version_key(r):
        # Extract hex version like 0x291 from "MCU-0x291"
        match = re.search(r'0x([0-9a-fA-F]+)', r['name'])
        if match:
            return int(match.group(1), 16)
        return 0

    # Sort and limit to 5 each
    fw_releases.sort(key=fw_version_key, reverse=True)
    mcu_releases.sort(key=mcu_version_key, reverse=True)

    return fw_releases[:7], mcu_releases[:7]


def fetch_jira_issues(auth, jql, max_results=50):
    """Fetch issues from JIRA."""
    url = 'https://getnexar.atlassian.net/rest/api/3/search/jql'
    params = {
        'jql': jql,
        'maxResults': max_results,
        'fields': 'summary,status,priority,assignee,created,updated,fixVersions,versions,labels'
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
        # Get affected versions (version found)
        versions = fields.get('versions', [])
        version_found = versions[0].get('name', '-') if versions else '-'
        bugs.append({
            'key': issue['key'],
            'summary': fields.get('summary', '')[:60],
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'priority': fields.get('priority', {}).get('name', 'Unknown') if fields.get('priority') else 'Unknown',
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'version': version_found,
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
        # Get affected versions (version discovered)
        versions = fields.get('versions', [])
        version_discovered = versions[0].get('name', '-') if versions else '-'
        tickets.append({
            'key': issue['key'],
            'summary': fields.get('summary', '')[:55],
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'priority': fields.get('priority', {}).get('name', 'Unknown') if fields.get('priority') else 'Unknown',
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
            'version': version_discovered,
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


def fetch_top_priorities(auth):
    """Fetch top 5 priority issues from active sprint on FS board."""
    # FS board ID is 268
    board_id = 268

    # Get active sprint
    url = f'https://getnexar.atlassian.net/rest/agile/1.0/board/{board_id}/sprint?state=active'
    response = requests.get(url, auth=auth)

    if response.status_code != 200:
        return {'priorities': [], 'sprint_id': None, 'sprint_name': None}

    sprints = response.json().get('values', [])
    if not sprints:
        return {'priorities': [], 'sprint_id': None, 'sprint_name': None}

    active_sprint_id = sprints[0]['id']
    active_sprint_name = sprints[0].get('name', 'Active Sprint')
    sprint_start = sprints[0].get('startDate', '')[:10] if sprints[0].get('startDate') else None
    sprint_end = sprints[0].get('endDate', '')[:10] if sprints[0].get('endDate') else None

    # Fetch ALL sprint issues for velocity chart (no B4 filter)
    sprint_issues = []
    url_search = 'https://getnexar.atlassian.net/rest/api/3/search/jql'
    jql = f'sprint = {active_sprint_id} AND issuetype in (Task, Story, Bug)'
    params = {'jql': jql, 'maxResults': 200, 'fields': 'summary,status,issuetype,resolutiondate,created'}
    response = requests.get(url_search, auth=auth, params=params)
    if response.status_code == 200:
        for issue in response.json().get('issues', []):
            fields = issue['fields']
            sprint_issues.append({
                'key': issue['key'],
                'summary': fields.get('summary', '')[:60],
                'status': fields.get('status', {}).get('name', ''),
                'type': fields.get('issuetype', {}).get('name', ''),
                'resolved': fields.get('resolutiondate', '')[:10] if fields.get('resolutiondate') else None,
                'created': fields.get('created', '')[:10] if fields.get('created') else None
            })

    # Fetch P1 issues first, then P2 if needed (B4 issues only, exclude Dropped)
    url = 'https://getnexar.atlassian.net/rest/api/3/search/jql'
    priorities = []

    # Get P1 issues first
    jql = f'sprint = {active_sprint_id} AND (summary ~ "B4" OR labels = Beam4k) AND priority = "P1 - High" AND status not in (Done, Closed, Dropped) ORDER BY created DESC'
    params = {'jql': jql, 'maxResults': 5, 'fields': 'summary,priority'}
    response = requests.get(url, auth=auth, params=params)
    if response.status_code == 200:
        for issue in response.json().get('issues', []):
            fields = issue['fields']
            priorities.append({
                'title': fields.get('summary', '')[:50],
                'ticket': issue['key'],
                'priority': fields.get('priority', {}).get('name', ''),
                'url': f"https://getnexar.atlassian.net/browse/{issue['key']}"
            })

    # If we don't have 5 yet, get P2 issues
    if len(priorities) < 5:
        jql = f'sprint = {active_sprint_id} AND (summary ~ "B4" OR labels = Beam4k) AND priority = "P2 - Medium" AND status not in (Done, Closed, Dropped) ORDER BY created DESC'
        params = {'jql': jql, 'maxResults': 5 - len(priorities), 'fields': 'summary,priority'}
        response = requests.get(url, auth=auth, params=params)
        if response.status_code == 200:
            for issue in response.json().get('issues', []):
                fields = issue['fields']
                priorities.append({
                    'title': fields.get('summary', '')[:50],
                    'ticket': issue['key'],
                    'priority': fields.get('priority', {}).get('name', ''),
                    'url': f"https://getnexar.atlassian.net/browse/{issue['key']}"
                })

    return {
        'priorities': priorities[:5],
        'sprint_id': active_sprint_id,
        'sprint_name': active_sprint_name,
        'sprint_start': sprint_start,
        'sprint_end': sprint_end,
        'sprint_issues': sprint_issues
    }


def fetch_velocity_data(auth):
    """Fetch weekly velocity data for last 8 weeks."""
    from datetime import timedelta

    velocity = []
    today = datetime.now()
    url = 'https://getnexar.atlassian.net/rest/api/3/search/jql'

    # Get initial counts (before our 8-week window)
    first_week_start = today - timedelta(weeks=7, days=today.weekday())

    # Initial open tickets (Task, Story, Bug only - exclude New, Backlog)
    jql = f'project = FS AND labels = Beam4k AND issuetype in (Task, Story, Bug) AND status not in (Done, Closed, New, Backlog) AND created < "{first_week_start.strftime("%Y-%m-%d")}"'
    params = {'jql': jql, 'maxResults': 200, 'fields': 'key'}
    response = requests.get(url, auth=auth, params=params)
    initial_open = len(response.json().get('issues', [])) if response.status_code == 200 else 0

    # Initial open bugs (exclude Done, Closed, Dropped, New, Backlog)
    jql = f'project = FS AND labels = Beam4k AND issuetype = Bug AND status not in (Done, Closed, Dropped, New, Backlog) AND created < "{first_week_start.strftime("%Y-%m-%d")}"'
    params = {'jql': jql, 'maxResults': 200, 'fields': 'key'}
    response = requests.get(url, auth=auth, params=params)
    initial_bugs = len(response.json().get('issues', [])) if response.status_code == 200 else 0

    for weeks_ago in range(7, -1, -1):  # 8 weeks, oldest to newest
        week_start = today - timedelta(weeks=weeks_ago, days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_label = week_start.strftime('%m/%d')

        # Resolved tickets this week (only Task, Story, Bug)
        jql = f'project = FS AND labels = Beam4k AND issuetype in (Task, Story, Bug) AND resolutiondate >= "{week_start.strftime("%Y-%m-%d")}" AND resolutiondate <= "{week_end.strftime("%Y-%m-%d")}"'
        params = {'jql': jql, 'maxResults': 200, 'fields': 'key'}
        response = requests.get(url, auth=auth, params=params)
        resolved = len(response.json().get('issues', [])) if response.status_code == 200 else 0

        # Created tickets this week (only Task, Story, Bug - exclude New, Backlog)
        jql = f'project = FS AND labels = Beam4k AND issuetype in (Task, Story, Bug) AND status not in (New, Backlog) AND created >= "{week_start.strftime("%Y-%m-%d")}" AND created <= "{week_end.strftime("%Y-%m-%d")}"'
        params = {'jql': jql, 'maxResults': 200, 'fields': 'key'}
        response = requests.get(url, auth=auth, params=params)
        created = len(response.json().get('issues', [])) if response.status_code == 200 else 0

        # Resolved bugs this week (Done, Closed, or Dropped)
        jql = f'project = FS AND labels = Beam4k AND issuetype = Bug AND resolutiondate >= "{week_start.strftime("%Y-%m-%d")}" AND resolutiondate <= "{week_end.strftime("%Y-%m-%d")}"'
        params = {'jql': jql, 'maxResults': 200, 'fields': 'key'}
        response = requests.get(url, auth=auth, params=params)
        bugs_resolved = len(response.json().get('issues', [])) if response.status_code == 200 else 0

        # Created bugs this week (exclude New/Backlog - only count active bugs)
        jql = f'project = FS AND labels = Beam4k AND issuetype = Bug AND status not in (New, Backlog) AND created >= "{week_start.strftime("%Y-%m-%d")}" AND created <= "{week_end.strftime("%Y-%m-%d")}"'
        params = {'jql': jql, 'maxResults': 200, 'fields': 'key'}
        response = requests.get(url, auth=auth, params=params)
        bugs_created = len(response.json().get('issues', [])) if response.status_code == 200 else 0

        velocity.append({
            'week': week_label,
            'resolved': resolved,
            'created': created,
            'bugs_resolved': bugs_resolved,
            'bugs_created': bugs_created
        })

    return {'data': velocity, 'initial_open': initial_open, 'initial_bugs': initial_bugs}


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
    fw_releases, mcu_releases = fetch_releases(auth)
    print(f"  Found {len(fw_releases)} FW releases, {len(mcu_releases)} MCU releases")

    # Fetch velocity data
    print("Fetching velocity data (8 weeks)...")
    velocity_result = fetch_velocity_data(auth)
    print(f"  Done")

    # Fetch top priorities from active sprint
    print("Fetching top priorities...")
    priorities_result = fetch_top_priorities(auth)
    if isinstance(priorities_result, dict):
        priorities = priorities_result['priorities']
        active_sprint_id = priorities_result['sprint_id']
        active_sprint_name = priorities_result['sprint_name']
        sprint_start = priorities_result.get('sprint_start')
        sprint_end = priorities_result.get('sprint_end')
        sprint_issues = priorities_result.get('sprint_issues', [])
    else:
        priorities = priorities_result
        active_sprint_id = None
        active_sprint_name = None
        sprint_start = None
        sprint_end = None
        sprint_issues = []
    print(f"  Found {len(priorities)} priorities, {len(sprint_issues)} sprint issues")

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
            {'name': 'Full Product', 'status': 'backlog', 'date': 'TBD'},
            {'name': 'MVP', 'status': 'in_progress', 'date': '2026-01-02'},
            {'name': 'PVT sign-off', 'status': 'blocked', 'date': 'TBD'},
            {'name': 'Field Test 3', 'status': 'in_progress', 'date': '2025-12-11'},
            {'name': 'Field Test 2', 'status': 'done', 'date': '2025-12-03'},
            {'name': 'Initial FT', 'status': 'done', 'date': '2025-11-17'},
            {'name': 'PVT 1.0', 'status': 'done', 'date': '2025-10-20'},
            {'name': 'PVT 0.5', 'status': 'done', 'date': '2025-09-29'},
            {'name': 'DVT signoff', 'status': 'done', 'date': '2025-09-08'},
        ],
        'priorities': priorities,
        'fw_releases': fw_releases,
        'mcu_releases': mcu_releases,
        'velocity': velocity_result['data'],
        'initial_open': velocity_result['initial_open'],
        'initial_bugs': velocity_result['initial_bugs'],
        'sprint_data': {
            'name': active_sprint_name,
            'start': sprint_start,
            'end': sprint_end,
            'issues': sprint_issues
        },
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
            'gh_review_prs': 'https://github.com/pulls?q=is%3Aopen+is%3Apr+review-requested%3Anexarieh+org%3Agetnexar',
            'active_sprint': f'https://getnexar.atlassian.net/jira/software/c/projects/FS/boards/268?selectedIssue=&sprint={active_sprint_id}' if active_sprint_id else None,
            'active_sprint_name': active_sprint_name
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
