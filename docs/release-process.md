# Release Process

Every shipped mod version should have a GitHub release. Old releases remain published as the project timeline.

## Version Rhythm

Use this pattern while the mod is still pre-release:

| Version shape | Meaning |
| --- | --- |
| `0.2.x.0` | Small feature slice or new playable behavior. |
| `0.2.x.1`, `0.2.x.2` | Hotfixes for the previous slice, usually log cleanup or small XML corrections. |
| Docs-only commit | No release required unless it changes test instructions, dependency expectations, or packaged files. |

All current releases should be GitHub pre-releases.

## Release Steps

1. Make the code/docs changes.
2. Bump `mod/modDesc.xml` only when the packaged mod behavior or testable contract changes.
3. Validate XML and packaging.
4. Commit and push the version bump.
5. Let GitHub CI pass on the pushed commit.
6. Use the GitHub Actions `Release` workflow, or push a matching `vX.Y.Z.W`
   tag after CI is green.

## Automated Release Workflow

`.github/workflows/release.yml` is the release owner for GitHub releases.

The workflow:

- compiles Python and Lua files;
- builds every package in `tools/package_manifest.json` with versioned names;
- validates every package;
- writes `SHA256SUMS.txt` and `package-set.json`;
- creates or verifies a `vX.Y.Z.W` tag for manual dispatches;
- publishes all package zips plus release metadata as GitHub release assets;
- publishes as a prerelease by default.

For manual dispatch, leave the version empty to use the package version from
`mod/modDesc.xml`, or enter the same version to make the intent explicit. The
workflow refuses to release when the requested version, tag version, and package
version disagree.

Manual dispatches should use the hybrid release-note inputs:

- `summary`: one short public-facing summary of the release.
- `notes`: extra curated context that should appear before the package list.
- `testing`: concise validation or runtime test notes.
- `known_issues`: known warnings, limitations, or required follow-up.

The workflow combines those curated notes with a generated commit changelog
since the previous `v*` tag, package sizes, SHA256 hashes, and prerelease/stable
status. If a curated field is omitted, the release still publishes with useful
generated notes, but `Testing` will say `Not provided.` and `Known Issues` will
say `None documented.`.

Use `stable` only when the project is genuinely ready to leave pre-release for
that version. Use `draft` when notes need manual editing before publication.

`tools/release.ps1` remains a local fallback, but the preferred path is GitHub
Actions so package sets, checksums, metadata, and release assets are produced
the same way every time.

## Release Notes Checklist

Release notes are public-facing changelog entries. Keep them concise and player-facing.

Every release note should include:

- a short public-facing summary
- dependency requirements
- what changed
- validation or runtime test notes
- known warnings or log lines when they affect the released package
- performance target status when relevant

Release notes should not include disposable-save instructions, smoke-test checklists, local machine paths, live-mods-folder bookkeeping, or one-off handoff notes. Put those in GitHub Issues or internal docs instead.

For release testing, prefer one rolling issue for the current prerelease smoke-test checklist. Update its version number and checklist as the prerelease advances instead of opening a new overlapping issue.

Before creating any issue, search open and closed issues in this repository for the same bug, test track, feature, or compatibility topic. Create a new issue only when the topic is majorly new or unique. If a suitable issue already exists, update that issue's version, checklist, labels, or status instead.

## Historical Rule

Never overwrite an old GitHub release asset to make history look cleaner. If a package needs correction, bump the version and publish a hotfix release.
