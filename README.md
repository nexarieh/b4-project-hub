# B4 (Beam4K) Project Hub

> **Team Leader's Knowledge Base** - Nexar's next-generation 4K smart dashcam
>
> Last updated: 2025-12-10 (Confluence synced)

---

## Quick Links

### Confluence / Jira
| Resource | Link | Notes |
|----------|------|-------|
| Release Plan | [Release plan for Beam4k](https://getnexar.atlassian.net/wiki/spaces/EMB/pages/4832722963/Release+plan+for+Beam4k) | Main release planning doc |
| Jira Backlog | [FS Board Backlog](https://getnexar.atlassian.net/jira/software/c/projects/FS/boards/268/backlog) | Sprint planning & backlog |

### GitHub Repos
| Repo | Local Path | Notes |
|------|------------|-------|
| nexar-chicony | `~/Git-new/nexar-chicony` | Main B4 firmware/software repo |
| nexar_n1 | `~/Git-new/nexar_n1` | N1 reference (for comparison) |

### Slack Channels
| Channel | Link | Purpose |
|---------|------|---------|
| #eng-beam4k | [Open](https://app.slack.com/client/T02KEL8KX/C0824FCA2GM) | Main engineering channel |
| #hw-beam4k | [Open](https://app.slack.com/client/T02KEL8KX/C054VJU0AC9) | Hardware team |
| #general-beam4k | [Open](https://app.slack.com/client/T02KEL8KX/C08M9J1S9CG) | General B4 discussions |

### Other Tools
| Tool | Link | Notes |
|------|------|-------|
| `[ADD]` | | |

---

## Project Status

**Current Phase:** Field Test 3 / MVP Development

| Metric | Status | Notes |
|--------|--------|-------|
| MVP Readiness | In Progress | MVP milestone active |
| PVT Sign-off | BLOCKED | Waiting for PVT samples from Chicony |
| Field Test 3 | QA | Sounds, Local stream, bug fixes |

---

## Priorities

### P0 - Critical (Address NOW)
- [ ] PVT sign-off blocked - need PVT samples from Chicony (FS-3185)

### P1 - This Sprint (Field Test 3)
- [ ] Sounds (FS-3272)
- [ ] Local stream (FS-2990)
- [ ] Bug fixes

### P2 - MVP Milestone
- [ ] Remote streaming (FS-2494)
- [ ] Manual clips (FS-3245)
- [ ] Guardian mode (VX-2343)
- [ ] Thumbnails for trimming (VX-2319)
- [ ] All settings options
- [ ] Acko assets support (sounds, logo)
- [ ] Acko cloud env support

### Backlog (Full Product)
- [ ] Wifi offloading (FS-2493)
- [ ] Vision Pipeline
- [ ] Rear camera

---

## Milestones & Timeline

| Milestone | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| DVT signoff | - | ✅ Done | Vanilla image, APIs, HW Validator, CV flow |
| PVT 0.5 | - | ✅ Done | Linux image |
| PVT 1.0 | - | ✅ Done | Partition A, LTE, SDK, nx_updater, Logstore, Lite SHM |
| Initial Field Test | - | ✅ Done | Onboarding, Events, OTA, Recording, Connectivity, etc. |
| Field Test 2 | - | ✅ Done | |
| Field Test 3 | - | 🔵 QA | Sounds, Local stream |
| PVT sign-off | TBD | 🔴 Blocked | Waiting for Chicony PVT samples |
| MVP (Mass Production) | ??? | 🟡 In Progress | Remote streaming, clips, guardian mode, etc. |
| Full Product | TBD | 📋 Backlog | Wifi offload, Vision, Rear cam |

---

## Technical Specs

### Hardware
| Component | Spec | Notes |
|-----------|------|-------|
| Resolution | 4K | |
| Sensor | `[TBD]` | |
| Storage | `[TBD]` | |

### Firmware
| Version | Date | Status | Notes |
|---------|------|--------|-------|
| `[CURRENT]` | | Active | |

### Comparison with Existing Products
| Feature | N1 | B2 | B2 Mini | B4 (Beam4K) |
|---------|----|----|---------|-------------|
| Resolution | | | | 4K |
| AI Features | | | | |

---

## Decisions Log

> Important decisions with context. Newest first.

### [DATE] - Decision Title
- **Context:** Why this decision was needed
- **Decision:** What was decided
- **Alternatives considered:** What else was on the table
- **Owner:** Who made the call

---

## Session Notes

> Running log of work sessions and insights. Newest first.

### 2025-12-10 - Confluence Integration & Status Sync
- **MCP Atlassian Setup Complete**: Fixed API token authentication
  - Old token had issues (possibly corrupted)
  - Created new token "claude-confluence" (expires Dec 14, 2025)
  - Updated `~/.claude.json` with working credentials
  - Both Confluence and Jira APIs now working
- **Synced Release Plan from Confluence** (page ID: 4832722963, version 34)
  - Current phase: Field Test 3 / MVP Development
  - **Blocker**: PVT sign-off waiting on Chicony samples
  - FT3 in QA: Sounds, Local stream
  - MVP features in progress: Remote streaming, Manual clips, Guardian mode, Thumbnails, Acko support
- **Key JIRA tickets identified**:
  - FT3: FS-3272, FS-2990
  - PVT sign-off: FS-3185
  - MVP: FS-2494, FS-3245, VX-2343, VX-2319
  - Full product: FS-2493
- **Next session**:
  - Pull detailed JIRA issue status
  - Track FT3 QA progress
  - Follow up on Chicony PVT samples blocker

### 2025-12-10 - Initial Setup
- Created this knowledge base
- Structure: Single markdown file with sections for links, status, priorities, specs, decisions, and session notes
- Goals:
  - Get quick picture of project status
  - Track what to promote/deal with ASAP vs later
  - Help create content (release plans, sprint planning)
- Next: Populate links and current status

---

## Content Generation Templates

<details>
<summary>Sprint Planning Template</summary>

```markdown
## Sprint [N] - [Start Date] to [End Date]

### Goals
1.

### Carried Over from Last Sprint
-

### New Items
-

### Risks/Dependencies
-
```
</details>

<details>
<summary>Release Notes Template</summary>

```markdown
## B4 Release [VERSION] - [DATE]

### Highlights
-

### New Features
-

### Bug Fixes
-

### Known Issues
-
```
</details>

---

*This file is AI-readable. When returning to this project, Claude can read this file to get full context.*
