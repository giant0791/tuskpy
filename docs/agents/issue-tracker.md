# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

- **Map**: one issue with the label `wayfinder:map`.
- **Child ticket**: a GitHub sub-issue of the map. Add it with `gh api -X POST repos/{owner}/{repo}/issues/<map>/sub_issues -F sub_issue_id=<ticket database id>`. Get the database id with `gh api repos/{owner}/{repo}/issues/<n> --jq .id`.
- **Blocking**: GitHub's native "blocked by" relationship. Add it with `gh api -X POST repos/{owner}/{repo}/issues/<blocked>/dependencies/blocked_by -F issue_id=<blocker database id>`.
- **Claim**: `gh issue edit <n> --add-assignee @me`.
- **Frontier**: the open sub-issues of the map that have no assignee and no open "blocked by" issues. List them with `gh api repos/{owner}/{repo}/issues/<map>/sub_issues` and check each one with `gh api repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by`.
