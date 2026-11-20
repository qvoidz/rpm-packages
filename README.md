# qvoidz RPM Packages

COPR-backed Fedora packages for x86_64 that **reuse upstream RPMs as-is**: the payloads are unpacked byte-for-byte (`rpm2cpio | cpio`) and repackaged, never rebuilt. A GitHub Actions workflow tracks upstream releases daily, bumps the spec files automatically, and triggers COPR builds, so users get normal `dnf upgrade` updates.

## Packages

- [WeChat](https://weixin.qq.com/) — Tencent's official Linux RPM (no GitHub releases)
- [WorkBuddy](https://www.workbuddy.cn/) — Tencent's official Linux RPM, discovered via the update API `copilot.tencent.com/v2/update?platform=workbuddy-linux-x64-rpm` (no GitHub releases)
- [FlClash](https://github.com/chen08209/FlClash) — upstream Linux x86_64 RPM
- [Fcitx5 WeTypeX](https://github.com/panxuc/fcitx5-wetypex) — upstream x86_64 RPM
- [Flyline](https://github.com/HalFrgrd/flyline) — wraps the upstream prebuilt bash loadable from the release tarball (no upstream RPM; built by COPR)
- [Linux QQ](https://im.qq.com/linuxqq/) — Tencent's official NTQQ RPM, mirrored into this repo's GitHub releases (`scripts/mirror-linuxqq.py`) because Tencent's CDN rejects datacenter IPs
- [Tencent Meeting](https://meeting.tencent.com/) — repacks the official x86_64 .deb into an RPM (no upstream RPM; built by COPR)

The WeTypeX proprietary runtime is not included in its upstream RPM. Follow the upstream setup instructions and accept its license separately.

## How "reuse the upstream RPM" works

COPR builds packages from a spec file, so each directory contains a small repack spec:

1. `Source0` points at the upstream RPM URL (GitHub release asset, or Tencent's version-independent download for WeChat / the update-API URL for WorkBuddy). COPR's `rpkg` SRPM builder downloads URL sources automatically.
2. `%install` unpacks it verbatim (`rpm2cpio %{SOURCE0} | cpio -idm`) and ships the identical file list. No binary is modified — this is also why `debug_package` is disabled and every repack spec disables `__os_install_post` (brp-strip/compress/check-rpaths would modify or reject the upstream binaries).
3. `%post`/`%postun` only refresh desktop/icon caches.

## Automatic updates

The [`copr-auto-update` workflow](.github/workflows/copr-auto-update.yml) runs daily (`scripts/check-updates.py`):

| Package | How the latest version is found |
| --- | --- |
| FlClash | GitHub API `releases/latest` (tag `v<version>`) |
| fcitx5-wetypex | GitHub API `releases/latest` (tag `v<version>-<rel>`, both fields updated) |
| flyline | GitHub API `releases/latest` (tag `v<version>`) |
| WeChat | HTTP `Range` request fetching only the RPM header (~2 MB) of Tencent's rolling download, version sniffed with `rpm -qp` |
| WorkBuddy | Tencent update API (JSON: version + RPM download URL); the RPM header is sniffed as a sanity check and both `Version` and `Source0` are rewritten |
| linuxqq | Tencent's official desktop download config (`pcConfig.json`); version parsed from the asset filename. The RPM itself is mirrored into a GitHub release of this repo by `scripts/mirror-linuxqq.py` (run it from a machine with China network access: it downloads the RPM, uploads the `linuxqq-<version>` release, bumps the spec and pushes) |
| wemeet | Tencent Meeting download API (`query-download-info`: version + .deb URL, both rewritten) |

When an upstream version is newer than the spec, the workflow:

1. rewrites the spec (`Version`, `Release`, changelog entry) and commits it as `github-actions[bot]`;
2. calls `copr-cli buildscm` for exactly the changed packages, so COPR rebuilds and publishes them;
3. users then see the update with plain `sudo dnf upgrade`.

The repo also keeps an independent [GitHub Pages DNF mirror](.github/workflows/publish-dnf-repo.yml) (`scripts/sync-dnf-repo.py`); it can be removed if you only use COPR.

## Fedora installation (COPR)

After the one-time setup below:

```bash
sudo dnf copr enable qvoidz/rpm-packages
sudo dnf install wechat workbuddy flclash fcitx5-wetypex flyline linuxqq wemeet
sudo dnf upgrade   # normal updates from then on
```

Alternative (static mirror without COPR):

```bash
sudo curl -fsSL https://raw.githubusercontent.com/qvoidz/rpm-packages/main/qvoidz.repo -o /etc/yum.repos.d/qvoidz.repo
sudo dnf makecache
sudo dnf install wechat workbuddy flclash fcitx5-wetypex
```

## One-time COPR setup

1. The COPR project is `qvoidz/rpm-packages` (currently only `fedora-45-x86_64`). `ExclusiveArch: x86_64` in the specs makes other archs skip automatically.
2. Get your API token from <https://copr.fedorainfracloud.org/api/> (after `copr-cli login`).
3. Add three repository secrets: `COPR_LOGIN`, `COPR_TOKEN`, `COPR_USERNAME` (from that token page).
4. Run the `Update packages on COPR` workflow once manually (`workflow_dispatch`) to do the initial builds; after that it is fully automatic.

Without the secrets the workflow still bumps and commits specs, it just skips triggering builds (warning is shown in the log).

## Trust model

COPR serves packages over HTTPS. Upstream RPM bytes are preserved, not re-signed with a project key. FlClash, WeTypeX and flyline assets are additionally verified against GitHub release asset names (and digests where the API provides them); WeChat and WorkBuddy are fetched from Tencent over HTTPS and validated for RPM metadata and x86_64 architecture (the WorkBuddy API's `sha256hash` field is not used, as it has been observed not to match the served file). This is a personal, unofficial repository and is not affiliated with the upstream projects.
