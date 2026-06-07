# Issue Management

Issues are the home for active testing, investigation, and follow-up work that should not clutter public-facing release notes.

## Duplicate Avoidance

Before creating any issue:

1. Search open and closed issues in this repository.
2. Check for matching release versions, fillTypes, placeables, log lines, model names, and dependency names.
3. Update an existing issue when the new information is just a newer version, repeated symptom, revised checklist, or same feature family.
4. Create a new issue only when the topic is majorly new or unique.

## Rolling Test Track

Use one rolling prerelease smoke-test issue for the current package line.

When a new prerelease supersedes the previous one:

- update the issue title version
- update the checklist
- add or replace the release link
- comment with important findings
- close it only when that testing track is genuinely finished

Do not create a fresh smoke-test issue for every version unless the new version introduces a separate test family that would make the existing issue confusing.

## Public Release Boundary

Release pages should read as public changelogs. Keep these in issues instead:

- disposable-save instructions
- smoke-test checklists
- local log-review handoffs
- local filesystem paths
- work-in-progress testing notes

