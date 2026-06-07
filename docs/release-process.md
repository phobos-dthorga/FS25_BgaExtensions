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
6. Run `tools/release.ps1`.

The helper script:

- reads the version from `modDesc.xml` if `-Version` is omitted
- builds a versioned zip in `dist/`
- creates a `vX.Y.Z.W` tag
- pushes the tag
- creates a GitHub pre-release by default
- refuses to overwrite an existing tag or release

GitHub CI currently builds validation artifacts only. It does not create releases, because `tools/release.ps1` remains the release owner. Do not add a release-creating tag workflow until the local helper is retired or changed to delegate release creation to GitHub Actions.

Use `-Stable` only when the project is genuinely ready to leave pre-release for that version. Use `-Draft` when notes need manual editing before publication.

## Release Notes Checklist

Release notes are public-facing changelog entries. Keep them concise and player-facing.

Every release note should include:

- dependency requirements
- what changed
- known warnings or log lines when they affect the released package
- performance target status when relevant

Release notes should not include disposable-save instructions, smoke-test checklists, local machine paths, live-mods-folder bookkeeping, or one-off handoff notes. Put those in GitHub Issues or internal docs instead.

For release testing, prefer one rolling issue for the current prerelease smoke-test checklist. Update its version number and checklist as the prerelease advances instead of opening a new overlapping issue.

Before creating any issue, search open and closed issues in this repository for the same bug, test track, feature, or compatibility topic. Create a new issue only when the topic is majorly new or unique. If a suitable issue already exists, update that issue's version, checklist, labels, or status instead.

## Historical Rule

Never overwrite an old GitHub release asset to make history look cleaner. If a package needs correction, bump the version and publish a hotfix release.
