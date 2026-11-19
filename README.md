# qvoidz RPM Repository

A small x86_64 DNF repository for Fedora. RPM payloads are synchronized from upstream releases and are **not rebuilt or repackaged**.

## Packages

- [WeChat](https://weixin.qq.com/) — Tencent's official Linux RPM
- [FlClash](https://github.com/chen08209/FlClash) — upstream Linux x86_64 RPM
- [Fcitx5 WeTypeX](https://github.com/panxuc/fcitx5-wetypex) — upstream x86_64 RPM

The WeTypeX proprietary runtime is not included in its upstream RPM. Follow the upstream setup instructions and accept its license separately.

## Fedora installation

After GitHub Pages has been enabled and the first workflow deployment has succeeded:

```bash
sudo curl -fsSL https://raw.githubusercontent.com/qvoidz/rpm-packages/main/qvoidz.repo -o /etc/yum.repos.d/qvoidz.repo
sudo dnf makecache
sudo dnf install wechat flclash fcitx5-wetypex
```

Update normally with:

```bash
sudo dnf upgrade
```

## Automation

GitHub Actions checks upstream releases daily and can also be started manually from the Actions tab. It downloads the original RPMs, validates their RPM metadata and upstream SHA-256 digest when supplied, then regenerates DNF repository metadata and publishes the static repository through GitHub Pages.

Only the latest x86_64 RPM for each application is kept in the published repository.

## Trust model

The repository is served over HTTPS. Upstream RPM bytes are preserved, so this repository does not re-sign them with a project key; consequently `gpgcheck=0` is used. The synchronization workflow validates GitHub release SHA-256 digests where provided. Tencent's version-independent download is checked for valid RPM metadata and x86_64 architecture.

This is a personal, unofficial repository and is not affiliated with the upstream projects.
