# GitHub Agents

Track PRs, commits, and code changes in B4 repositories.

## Target Repos

| Repo | Path | Purpose |
|------|------|---------|
| nexar-chicony | ~/Git-new/nexar-chicony | Main B4 firmware/software |
| nexar_n1 | ~/Git-new/nexar_n1 | N1 reference |

## Planned Scripts

### pr_tracker.py
- List open PRs with status
- Track review progress
- Identify stale PRs (>3 days no activity)
- Link PRs to JIRA tickets

### commit_analyzer.py
- Recent commits by author
- Commits per component/folder
- Commit frequency trends

### release_notes.py
- Generate release notes from commits
- Group by type (feature, fix, refactor)
- Extract JIRA ticket references

## Usage
```bash
# List open PRs
python3 pr_tracker.py --repo nexar-chicony

# Analyze commits since last release
python3 commit_analyzer.py --since v7.4.53

# Generate release notes
python3 release_notes.py --from v7.4.53 --to HEAD
```

## Requirements
- GitHub CLI (gh) installed and authenticated
- Git access to repos
