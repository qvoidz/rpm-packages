# qvoidz RPM Packages

Personal Fedora RPM packaging and release-tracking repository.

## Packages

| Package | Upstream | Packaging status |
|---|---|---|
| fcitx5-wetypex | https://github.com/panxuc/fcitx5-wetypex | Upstream already publishes Fedora RPMs; local COPR recipe is being prepared after auditing its RPM metadata and build/install scripts. |
| flclash | https://github.com/chen08209/FlClash | Upstream already publishes Fedora RPMs; local COPR recipe is being prepared after auditing its RPM metadata and build/install scripts. |

## Policy

- Prefer upstream source and release artifacts.
- Pin versions and verify SHA-256 checksums.
- Do not bundle proprietary runtime assets unless their license explicitly permits redistribution.
- Keep package build scripts and runtime dependencies auditable.
- Test packages on Fedora before enabling automatic updates.

This repository is not affiliated with either upstream project.
