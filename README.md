# qvoidz RPM Packages

Personal Fedora RPM packaging and release-tracking repository.

## Packages

| Package | Upstream | Packaging status |
|---|---|---|
| fcitx5-wetypex | https://github.com/panxuc/fcitx5-wetypex | Repackages the upstream RPM for COPR. |
| flclash | https://github.com/chen08209/FlClash | Repackages the upstream RPM for COPR. |
| wechat | https://weixin.qq.com/ | Repackages Tencent's official x86_64 RPM; version and SHA-256 are pinned in the SPEC. |

## Policy

- Prefer upstream source and release artifacts.
- Pin versions and verify SHA-256 checksums.
- Do not bundle proprietary runtime assets unless their license explicitly permits redistribution.
- Keep package build scripts and runtime dependencies auditable.
- Test packages on Fedora before enabling automatic updates.

This repository is not affiliated with either upstream project.
