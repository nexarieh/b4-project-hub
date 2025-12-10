# B4 (Beam4K) Project Hub

Nexar's next-generation 4K smart dashcam - Team Leader's Knowledge Base

## Dashboard

```bash
cd dashboard && python3 fetch_data.py && python3 -m http.server 8081
```
Open http://localhost:8081

## Quick Links

| Resource | Link |
|----------|------|
| Release Plan | [Confluence](https://getnexar.atlassian.net/wiki/spaces/EMB/pages/4832722963) |
| JIRA Board | [FS-268 Backlog](https://getnexar.atlassian.net/jira/software/c/projects/FS/boards/268/backlog) |
| BR Bugs | [Beam4 Bugs](https://getnexar.atlassian.net/jira/software/c/projects/BR/boards/287/backlog?issueParent=109691) |
| Sprint WW51 | [Planning Page](https://getnexar.atlassian.net/wiki/spaces/EMB/pages/5143494660) |
| Serial Numbers | [FT Tracking Sheet](https://docs.google.com/spreadsheets/d/1ZAwoMznI-whqYJFvrwy9SrFTTNGQiMq62E_86qvR_sw/edit?gid=243956152#gid=243956152) |
| ODM Export | [Google Drive](https://drive.google.com/drive/folders/1lFlqGslitGcLlwvC3xXvD4WrOqcWQ6Fh) |
| #eng-beam4k | [Slack](https://app.slack.com/client/T02KEL8KX/C0824FCA2GM) |

## Current Status

**Phase:** Field Test 3 / MVP Development
**Blocker:** PVT sign-off waiting on Chicony samples

## Top 5 Priorities (WW51)

| # | Priority | Ticket |
|---|----------|--------|
| 1 | FT: OBD issue | TBD |
| 2 | FT: Support HWK (MCU) | FS-3051 |
| 3 | MVP: Remote stream bugs | FS-3375 |
| 4 | MVP: Encryption | FS-3283 |
| 5 | MVP: HTTP Server "teepee" | FS-2677 |

## Agent Folders

| Folder | Purpose |
|--------|---------|
| `confluence/` | Confluence page editors |
| `slack/` | Slack channel analyzers |
| `summary/` | Status reports & bug tracking |
| `dashboard/` | Browser dashboard (working) |
| `github/` | PR tracking, commits |
| `alerts/` | Stale tickets, build failures |
| `metrics/` | Velocity, bug trends |
| `reports/` | Weekly/release reports |

## Setup

See [SETUP.md](SETUP.md) for MCP Atlassian configuration.

**Token expires:** Dec 14, 2025
