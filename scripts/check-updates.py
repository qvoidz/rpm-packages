#!/usr/bin/env python3
"""Detect new upstream releases and bump the COPR spec files.

Packages and their upstream sources:

- flclash        GitHub releases of chen08209/FlClash (tag v<version>,
                 asset FlClash-<version>-linux-amd64.rpm). COPR package name
                 is FlClash (spec Name:), same as upstream's own RPM;
                 the folder/spec-file name stays lowercase "flclash".
- fcitx5-wetypex GitHub releases of panxuc/fcitx5-wetypex
                 (tag v<version>-<upstream_rel>, asset
                 fcitx5-wetypex-<version>-<upstream_rel>.x86_64.rpm).
- flyline        GitHub releases of HalFrgrd/flyline (tag v<version>, asset
                 libflyline-v<version>-x86_64-unknown-linux-gnu.tar.gz).
- wechat         Tencent's version-independent download URL. Only the RPM
                 header is fetched (HTTP Range request) to sniff the newest
                 version, so no multi-hundred-MB download is needed.
- workbuddy      Tencent's WorkBuddy update API returns version + full RPM
                 download URL (no GitHub releases). The RPM header is sniffed
                 the same way as WeChat as a sanity check.
- linuxqq        Tencent's official desktop download config
                 (cdn-go.cn/.../rainbow/pcConfig.json) lists the current
                 Linux RPM URL; the version is parsed from the asset
                 filename (QQ_<version>_<date>_x86_64_01.rpm). The spec
                 signs that URL at build time via Tencent's public
                 GetSign API and repacks the payload (bare links 403).
- wemeet         Tencent Meeting's download API
                 (meeting.tencent.com/web-service/query-download-info)
                 returns version + full .deb URL. The .deb is repacked
                 into an RPM.
- iptvnator      GitHub releases of 4gray/iptvnator (tag v<version>,
                 asset iptvnator-<version>-linux-x86_64.rpm).
- waydroid-script casualsnek/waydroid_script has no git tags: the version
                 is the default-branch commit date (YYYYMMDD) and the pinned
                 commit hash is rewritten into %global commit.
- telegram-desktop GitHub releases of telegramdesktop/tdesktop
                 (tag v<version>, Linux portable asset
                 td-setup-linux-x64-<version>.tar.xz).
- opencode       GitHub releases of sst/opencode (tag v<version>, asset
                 opencode-linux-x64.tar.gz).
- opencode-desktop Same release as opencode; the desktop Electron RPM
                 (upstream package name "opencode") is repacked under the
                 name opencode-desktop to coexist with the CLI package.
- claude-code    Anthropic's GCS release channel: the "stable" pointer file
                 names the version; the binary is <v>/linux-x64/claude.
- pi             GitHub releases of earendil-works/pi (tag v<version>,
                 asset pi-linux-x64.tar.gz).
- codex          GitHub releases of openai/codex (tag rust-v<version>,
                 asset codex-x86_64-unknown-linux-musl.tar.gz).
- magpie         GitHub releases of yetone/magpie-releases (tag v<version>,
                 raw binaries magpie-linux-amd64 + magpie-cli-linux-amd64).
- ccswitch       GitHub releases of farion1231/cc-switch (tag v<version>,
                 asset CC-Switch-v<version>-Linux-x86_64.rpm; repacked
                 under the package name "ccswitch").
- codebuddy-ide  Tencent's update API
                 (copilot.tencent.com/v2/update?platform=ide-linux-x64)
                 returns version + .deb URL (domestic channel).

When a newer upstream version is found, the matching spec file is rewritten
(Version / Release / changelog) and the package names are reported through
the `changed` GitHub Actions output so CI can commit and trigger a COPR
build for exactly those packages.

Usage:
  python3 scripts/check-updates.py             # detect + bump specs
  python3 scripts/check-updates.py --dry-run   # detect only, no writes
  python3 scripts/check-updates.py --selftest  # offline rpm_vercmp checks
"""
import json
import locale
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]

FLCLASH_REPO = "chen08209/FlClash"
WETYPEX_REPO = "panxuc/fcitx5-wetypex"
FLYLINE_REPO = "HalFrgrd/flyline"
WECHAT_URL = ("https://dldir1v6.qq.com/weixin/Universal/Linux/"
              "WeChatLinux_x86_64.rpm")
WORKBUDDY_API = ("https://copilot.tencent.com/v2/update"
                 "?platform=workbuddy-linux-x64-rpm")
WORKBUDDY_DOWNLOAD_HOST = "https://download.codebuddy.cn/"
QQ_CONFIG_URL = ("https://cdn-go.cn/qq-web/im.qq.com_new/latest/"
                 "rainbow/pcConfig.json")
WEMEET_API = ("https://meeting.tencent.com/web-service/query-download-info"
              "?q=%5B%7B%22package-type%22%3A%22app%22%2C%22channel%22%3A%22"
              "0300000000%22%2C%22platform%22%3A%22linux%22%2C%22arch%22%3A%22"
              "x86_64%22%2C%22decorators%22%3A%5B%22deb%22%5D%7D%5D"
              "&nonce=123456789abcdefg")
WECHAT_HEADER_RANGE = "bytes=0-2097151"  # RPM lead + signature + header

IPTVNATOR_REPO = "4gray/iptvnator"
WAYDROID_REPO = "casualsnek/waydroid_script"
NERDFONTS_REPO = "ryanoasis/nerd-fonts"
LAZYVIM_REPO = "LazyVim/LazyVim"
LAZYVIM_STARTER_COMMIT = "803bc181d7c0d6d5eeba9274d9be49b287294d99"
ZED_REPO = "zed-industries/zed"
STARSHIP_REPO = "starship/starship"
QQMUSIC_PAGE = "https://y.qq.com/download/download.html"
WPS_ROLLING_URL = ("https://wdl1.pcfg.cache.wpscdn.com/wpsdl/wpsoffice/"
                   "download/linux/wps-office.rpm")
WPS_HEADER_RANGE = "bytes=0-4194303"  # WPS RPM header blob is ~3 MB
DINGTALK_GRAY_JSON = ("https://dtapp-pub.dingtalk.com/dingtalk-desktop/"
                      "xc_dingtalk_update/linux_deb/Update/other/amd64/"
                      "linux_dingtalk_update_package_gray.json")
TELEGRAM_REPO = "telegramdesktop/tdesktop"
ZCODE_MANIFEST_URL = ("https://zcode.z.ai/api/v1/releases/electron/manifest"
                      "?platform=linux-x64&channel=stable")
OPENCODE_REPO = "sst/opencode"
CLAUDE_GCS_BASE = ("https://storage.googleapis.com/claude-code-dist-"
                   "86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases")
PI_REPO = "earendil-works/pi"
CODEX_REPO = "openai/codex"
MAGPIE_REPO = "yetone/magpie-releases"
CCSWITCH_REPO = "farion1231/cc-switch"
CODEBUDDY_IDE_API = ("https://copilot.tencent.com/v2/update"
                     "?platform=ide-linux-x64&version=1.0.0"
                     "&x-machine-id=default")

USER_AGENT = {"User-Agent": "qvoidz-rpm-packages-spec-bumper"}
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

CHANGED = []


def github_json(url):
    headers = dict(USER_AGENT)
    headers["Accept"] = "application/vnd.github+json"
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def latest_release(owner_repo):
    return github_json(f"https://api.github.com/repos/{owner_repo}/releases/latest")


def rpm_vercmp(a, b):
    """RPM version comparison (subset of the upstream rpmvercmp algorithm).

    Returns 1 if a > b, -1 if a < b, 0 if equal.
    """
    if a == b:
        return 0
    ai = bi = 0
    alen, blen = len(a), len(b)
    while ai < alen or bi < blen:
        while ai < alen and not a[ai].isalnum():
            ai += 1
        while bi < blen and not b[bi].isalnum():
            bi += 1
        if ai >= alen and bi >= blen:
            return 0
        if ai >= alen:
            return -1
        if bi >= blen:
            return 1
        numa = a[ai].isdigit()
        numb = b[bi].isdigit()
        if numa and not numb:
            return 1
        if numb and not numa:
            return -1
        if numa:
            ea = ai
            while ea < alen and a[ea].isdigit():
                ea += 1
            eb = bi
            while eb < blen and b[eb].isdigit():
                eb += 1
            va, vb = int(a[ai:ea]), int(b[bi:eb])
            if va != vb:
                return 1 if va > vb else -1
            ai, bi = ea, eb
        else:
            ea = ai
            while ea < alen and a[ea].isalpha():
                ea += 1
            eb = bi
            while eb < blen and b[eb].isalpha():
                eb += 1
            va, vb = a[ai:ea], b[bi:eb]
            if va != vb:
                return 1 if va > vb else -1
            ai, bi = ea, eb
    return 0


def read_spec(pkg):
    return (ROOT / pkg / f"{pkg}.spec").read_text(encoding="utf-8")


def write_spec(pkg, text):
    (ROOT / pkg / f"{pkg}.spec").write_text(text, encoding="utf-8")


def spec_field(text, name):
    match = re.search(rf"(?m)^{name}:\s*(\S+)", text)
    if not match:
        raise RuntimeError(f"{name} field not found in spec")
    return match.group(1)


def changelog_date():
    # rpm changelogs require English weekday/month abbreviations.
    locale.setlocale(locale.LC_ALL, "C")
    return time.strftime("%a %b %d %Y")


def bump_spec(pkg, text, version, release, message, changelog_release=None):
    """Rewrite Version/Release and prepend a changelog entry."""
    text = re.sub(r"(?m)^(Version:\s*)\S+", rf"\g<1>{version}", text, count=1)
    text = re.sub(r"(?m)^(Release:\s*)\S+", rf"\g<1>{release}", text, count=1)
    if changelog_release is None:
        changelog_release = release.split("%", 1)[0]
    if not changelog_release:
        raise ValueError("A concrete changelog Release value is required")
    entry = (f"* {changelog_date()} COPR Builder <copr@example.invalid> "
             f"- {version}-{changelog_release}\n"
             f"- {message}\n")
    return text.replace("%changelog\n", "%changelog\n" + entry, 1)


def waydroid_release_for_update(current_version, current_commit,
                               version, commit, current_release):
    """Calculate a new Release when the pinned Waydroid commit changes."""
    order = rpm_vercmp(version, current_version)
    if order < 0 or (order == 0 and commit == current_commit):
        return None
    if order > 0:
        return "1%{?dist}"
    match = re.match(r"^(\d+)", current_release)
    if not match:
        raise RuntimeError(
            f"Cannot increment Waydroid RPM Release: {current_release}")
    return f"{int(match.group(1)) + 1}%{{?dist}}"


def require_asset(release, name):
    assets = [a["name"] for a in release.get("assets", [])]
    if name not in assets:
        raise RuntimeError(
            f"{release.get('tag_name')}: expected asset {name}, "
            f"found {assets}")


def sync_flclash(dry_run):
    # Folder/spec-file name is "flclash"; the COPR package (spec Name:) is
    # "FlClash", same as upstream's own RPM, so upgrades apply in place.
    spec = read_spec("flclash")
    current = spec_field(spec, "Version")
    release = latest_release(FLCLASH_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected FlClash tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"FlClash: up to date ({current})"
    require_asset(release, f"FlClash-{version}-linux-amd64.rpm")
    if not dry_run:
        write_spec("flclash", bump_spec(
            "flclash", spec, version, "1%{?dist}",
            f"Update to upstream FlClash {tag}"))
    # CHANGED entries are COPR package names: the CI workflow appends them to
    # $COPR_WEBHOOK_BASE/$pkg/ to fire per-package rebuild webhooks.
    CHANGED.append("FlClash")
    return f"FlClash: {current} -> {version}"


def sync_wetypex(dry_run):
    spec = read_spec("fcitx5-wetypex")
    current_version = spec_field(spec, "Version")
    current_rel = re.search(r"(?m)^%global upstream_rel\s+(\S+)", spec)
    if not current_rel:
        raise RuntimeError("%global upstream_rel not found in fcitx5 spec")
    current_rel = current_rel.group(1)
    release = latest_release(WETYPEX_REPO)
    tag = release["tag_name"]
    match = re.fullmatch(r"v(\d[\w.]*)-(\d+)", tag)
    if not match:
        raise RuntimeError(f"Unexpected fcitx5-wetypex tag format: {tag}")
    version, upstream_rel = match.group(1), match.group(2)
    newer = (rpm_vercmp(version, current_version) > 0
             or (version == current_version and int(upstream_rel) > int(current_rel)))
    if not newer:
        return f"fcitx5-wetypex: up to date ({current_version}-{current_rel})"
    require_asset(release, f"fcitx5-wetypex-{version}-{upstream_rel}.x86_64.rpm")
    if not dry_run:
        spec = spec.replace(
            f"%global upstream_rel {current_rel}",
            f"%global upstream_rel {upstream_rel}", 1)
        write_spec("fcitx5-wetypex", bump_spec(
            "fcitx5-wetypex", spec, version, "%{upstream_rel}%{?dist}",
            f"Update to upstream {tag}", changelog_release=upstream_rel))
    CHANGED.append("fcitx5-wetypex")
    return f"fcitx5-wetypex: {current_version}-{current_rel} -> {version}-{upstream_rel}"


def rpm_header_sniff(url, range_=None):
    """Fetch only the RPM header (HTTP Range request) and read name/version."""
    req = urllib.request.Request(
        url, headers={**USER_AGENT, "Range": range_ or WECHAT_HEADER_RANGE})
    with urllib.request.urlopen(req, timeout=120) as response:
        data = response.read()
    with tempfile.NamedTemporaryFile(suffix=".rpm", delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        try:
            import rpm  # python3-rpm (installed in CI; also on Fedora)
            ts = rpm.TransactionSet()
            ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES | rpm._RPMVSF_NODIGESTS)
            with open(path, "rb") as fd:
                header = ts.hdrFromFdno(fd.fileno())
            return str(header["name"]), str(header["version"])
        except ImportError:
            output = subprocess.check_output(
                ["rpm", "-qp", "--qf", "%{NAME} %{VERSION}", path],
                text=True)
            name, version = output.split()
            return name, version
    finally:
        os.unlink(path)


def wechat_header_version():
    return rpm_header_sniff(WECHAT_URL)


def sync_wechat(dry_run):
    spec = read_spec("wechat")
    current = spec_field(spec, "Version")
    name, version = wechat_header_version()
    if name.lower() not in ("wechat", "weixin"):
        raise RuntimeError(f"Unexpected Tencent RPM package name: {name}")
    if rpm_vercmp(version, current) <= 0:
        return f"wechat: up to date ({current})"
    if not dry_run:
        write_spec("wechat", bump_spec(
            "wechat", spec, version, "1%{?dist}",
            f"Update to upstream WeChat {version}"))
    CHANGED.append("wechat")
    return f"wechat: {current} -> {version}"


def sync_flyline(dry_run):
    spec = read_spec("flyline")
    current = spec_field(spec, "Version")
    release = latest_release(FLYLINE_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected flyline tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"flyline: up to date ({current})"
    require_asset(release, f"libflyline-v{version}-x86_64-unknown-linux-gnu.tar.gz")
    if not dry_run:
        write_spec("flyline", bump_spec(
            "flyline", spec, version, "1%{?dist}",
            f"Update to upstream Flyline {tag}"))
    CHANGED.append("flyline")
    return f"flyline: {current} -> {version}"


def sync_workbuddy(dry_run):
    spec = read_spec("workbuddy")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(WORKBUDDY_API, headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        info = json.load(response)
    version, url = info["version"], info["url"]
    if not re.fullmatch(r"[0-9][0-9.]*", version):
        raise RuntimeError(f"Unexpected WorkBuddy version: {version}")
    if (not url.startswith(WORKBUDDY_DOWNLOAD_HOST)
            or version not in url
            or not url.endswith(".rpm")):
        raise RuntimeError(f"Unexpected WorkBuddy download URL: {url}")
    if rpm_vercmp(version, current) <= 0:
        return f"workbuddy: up to date ({current})"
    # Sanity check both package identity and version before bumping.
    name, payload_version = rpm_header_sniff(url)
    if name != "workbuddy":
        raise RuntimeError(f"Unexpected WorkBuddy RPM package name: {name}")
    # Since 5.11.6 Tencent moved the build id (e.g. 44396970) from the RPM
    # Version into the Release, so the payload version (5.11.6) is a dotted
    # prefix of the API version (5.11.6.44396970). Accept that shape as a
    # match while still catching genuinely wrong payloads.
    if not (rpm_vercmp(payload_version, version) == 0
            or version.startswith(payload_version + ".")):
        raise RuntimeError(
            f"WorkBuddy API version {version} does not match RPM payload "
            f"version {payload_version}")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{url}", spec, count=1)
        write_spec("workbuddy", bump_spec(
            "workbuddy", spec, version, "1%{?dist}",
            f"Update to upstream WorkBuddy {version}"))
    CHANGED.append("workbuddy")
    return f"workbuddy: {current} -> {version}"


def sync_linuxqq(dry_run):
    """Linux QQ: parse the official desktop download config.

    The config lists the current Linux RPM asset; the version is taken from
    the asset filename (QQ_<version>_<date>_x86_64_01.rpm). Tencent's CDN
    rejects datacenter IPs for bare links and (since Oct 2026) requires
    per-request signing, so .github/workflows/mirror.yml signs and mirrors
    the payload to GitHub Releases (running BEFORE this daily update, so
    the asset exists before the bump triggers a COPR build) and the spec's
    Source0 points at the mirrored asset. Bumping therefore only rewrites
    Version and the %global qq_rpm_url line -- no payload is ever fetched
    here.
    """
    spec = read_spec("linuxqq")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(QQ_CONFIG_URL, headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        config = json.load(response)
    urls = re.findall(r"https://qqdl\.gtimg\.cn/[^\"\\]+\.rpm",
                      json.dumps(config, ensure_ascii=False))
    matches = [u for u in dict.fromkeys(urls)
               if re.search(r"QQ_[\d.]+_\d+_x86_64_\d+\.rpm$", u)]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one Linux x86_64 QQ RPM in the config, "
            f"found {matches}")
    official_url = matches[0]
    match = re.search(r"QQ_([\d.]+)_\d+_x86_64", official_url)
    if not match:
        raise RuntimeError(f"Cannot parse QQ version from URL: {official_url}")
    version = match.group(1)
    if rpm_vercmp(version, current) <= 0:
        return f"linuxqq: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^%global qq_rpm_url .*$",
                      rf"%global qq_rpm_url {official_url}", spec, count=1)
        write_spec("linuxqq", bump_spec(
            "linuxqq", spec, version, "1%{?dist}",
            f"Update to upstream Linux QQ {version} (build-time signed download)"))
    CHANGED.append("linuxqq")
    return f"linuxqq: {current} -> {version}"


def sync_wemeet(dry_run):
    """Tencent Meeting: query the official download-info API for the .deb."""
    spec = read_spec("wemeet")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(WEMEET_API, headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        info = json.load(response)["info-list"][0]
    version, url = info["version"], info["url"]
    if not re.fullmatch(r"[0-9][0-9.]*", version):
        raise RuntimeError(f"Unexpected Wemeet version: {version}")
    if (not url.startswith("https://updatecdn.meeting.qq.com/")
            or version not in url
            or not url.endswith(".deb")):
        raise RuntimeError(f"Unexpected Wemeet download URL: {url}")
    if rpm_vercmp(version, current) <= 0:
        return f"wemeet: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{url}", spec, count=1)
        write_spec("wemeet", bump_spec(
            "wemeet", spec, version, "1%{?dist}",
            f"Update to upstream Tencent Meeting {version}"))
    CHANGED.append("wemeet")
    return f"wemeet: {current} -> {version}"


def sync_iptvnator(dry_run):
    """IPTVnator: GitHub releases (tag v<version>, x86_64 RPM asset)."""
    spec = read_spec("iptvnator")
    current = spec_field(spec, "Version")
    release = latest_release(IPTVNATOR_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected iptvnator tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"iptvnator: up to date ({current})"
    require_asset(release, f"iptvnator-{version}-linux-x86_64.rpm")
    if not dry_run:
        write_spec("iptvnator", bump_spec(
            "iptvnator", spec, version, "1%{?dist}",
            f"Update to upstream iptvnator {tag}"))
    CHANGED.append("iptvnator")
    return f"iptvnator: {current} -> {version}"


def sync_waydroid(dry_run):
    """waydroid_script: track the default-branch commit.

    Version = commit date (YYYYMMDD). Multiple commits on the same date
    increment RPM Release so later commits are not silently skipped.
    """
    spec = read_spec("waydroid-script")
    current = spec_field(spec, "Version")
    current_commit_match = re.search(r"(?m)^%global commit\s+(\S+)", spec)
    if not current_commit_match:
        raise RuntimeError("%global commit not found in waydroid-script spec")
    current_commit = current_commit_match.group(1)
    current_release = spec_field(spec, "Release")
    info = github_json(f"https://api.github.com/repos/{WAYDROID_REPO}"
                       "/commits/HEAD")
    sha = info["sha"]
    date = info["commit"]["committer"]["date"]
    version = date[:10].replace("-", "")
    if not re.fullmatch(r"20[0-9]{6}", version):
        raise RuntimeError(f"Unexpected waydroid_script commit date: {date}")
    release = waydroid_release_for_update(
        current, current_commit, version, sha, current_release)
    if release is None:
        return f"waydroid-script: up to date ({current}, {sha[:12]})"
    if not dry_run:
        spec = re.sub(r"(?m)^%global commit .*$",
                      rf"%global commit {sha}", spec, count=1)
        write_spec("waydroid-script", bump_spec(
            "waydroid-script", spec, version, release,
            f"Update to waydroid_script master {sha[:12]}"))
    CHANGED.append("waydroid-script")
    return f"waydroid-script: {current} -> {version} ({sha[:12]})"


def sync_nerdfonts(dry_run):
    """Nerd Fonts Cascadia Code: releases/latest tag v<version>."""
    spec = read_spec("nerd-fonts-cascadia-code")
    current = spec_field(spec, "Version")
    release = latest_release(NERDFONTS_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected nerd-fonts tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"nerd-fonts-cascadia-code: up to date ({current})"
    require_asset(release, "CascadiaCode.zip")
    if not dry_run:
        spec = re.sub(
            r"(?m)^(Source0:\s*).*$",
            rf"\g<1>https://github.com/{NERDFONTS_REPO}/releases/download/"
            rf"v{version}/CascadiaCode.zip", spec, count=1)
        write_spec("nerd-fonts-cascadia-code", bump_spec(
            "nerd-fonts-cascadia-code", spec, version, "1%{?dist}",
            f"Update to upstream Nerd Fonts {tag}"))
    CHANGED.append("nerd-fonts-cascadia-code")
    return f"nerd-fonts-cascadia-code: {current} -> {version}"


def sync_lazyvim(dry_run):
    """LazyVim: package the official starter template.

    Version follows the LazyVim/LazyVim release tag (v<version>); the
    starter template commit is pinned via %global starter_commit.
    """
    spec = read_spec("lazyvim")
    current = spec_field(spec, "Version")
    release = latest_release(LAZYVIM_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected LazyVim tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"lazyvim: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^%global starter_commit .*$",
                      rf"%global starter_commit {LAZYVIM_STARTER_COMMIT}",
                      spec, count=1)
        write_spec("lazyvim", bump_spec(
            "lazyvim", spec, version, "1%{?dist}",
            f"Update to upstream LazyVim {tag} (starter template unchanged)"))
    CHANGED.append("lazyvim")
    return f"lazyvim: {current} -> {version}"


def sync_zed(dry_run):
    """Zed: GitHub releases (tag v<version>, zed-linux-x86_64.tar.gz)."""
    spec = read_spec("zed")
    current = spec_field(spec, "Version")
    release = latest_release(ZED_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected zed tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"zed: up to date ({current})"
    require_asset(release, "zed-linux-x86_64.tar.gz")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{ZED_REPO}/releases/download/"
                      rf"v{version}/zed-linux-x86_64.tar.gz", spec, count=1)
        write_spec("zed", bump_spec(
            "zed", spec, version, "1%{?dist}",
            f"Update to upstream Zed {tag}"))
    CHANGED.append("zed")
    return f"zed: {current} -> {version}"


def sync_starship(dry_run):
    """Starship: GitHub releases (tag v<version>, static musl tarball)."""
    spec = read_spec("starship")
    current = spec_field(spec, "Version")
    release = latest_release(STARSHIP_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected starship tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"starship: up to date ({current})"
    asset = f"starship-x86_64-unknown-linux-musl.tar.gz"
    require_asset(release, asset)
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{STARSHIP_REPO}/releases/"
                      rf"download/v{version}/{asset}", spec, count=1)
        write_spec("starship", bump_spec(
            "starship", spec, version, "1%{?dist}",
            f"Update to upstream Starship {tag}"))
    CHANGED.append("starship")
    return f"starship: {current} -> {version}"


def sync_qqmusic(dry_run):
    """QQ Music: parse the official download page for the signed redirect.

    The page embeds a file_redirect.fcg URL that mints a fresh signed
    download link on every request; the version lives in the file=
    parameter (qqmusic_<version>_amd64.deb).
    """
    spec = read_spec("qqmusic")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(QQMUSIC_PAGE, headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        page = response.read().decode("utf-8", "replace")
    hits = re.findall(
        r"https://c\.y\.qq\.com/cgi-bin/file_redirect\.fcg\?[^\"'>\s]*"
        r"file=ecosfile_plink%2Fmusic_clntupate%2Flinux%2Fother%2F"
        r"qqmusic_([0-9.]+)_amd64\.deb[^\"'>\s]*",
        page.replace("&amp;", "&"))
    if not hits:
        raise RuntimeError("No QQ Music deb redirect URL on the download page")
    version = hits[0]
    if not re.fullmatch(r"[0-9][0-9.]*", version):
        raise RuntimeError(f"Unexpected QQ Music version: {version}")
    if rpm_vercmp(version, current) <= 0:
        return f"qqmusic: up to date ({current})"
    redirect = re.search(
        r"https://c\.y\.qq\.com/cgi-bin/file_redirect\.fcg\?[^\"'>\s]*"
        rf"file=ecosfile_plink%2Fmusic_clntupate%2Flinux%2Fother%2F"
        rf"qqmusic_{re.escape(version)}_amd64\.deb[^\"'>\s]*",
        page.replace("&amp;", "&")).group(0)
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{redirect}",
                      spec, count=1)
        write_spec("qqmusic", bump_spec(
            "qqmusic", spec, version, "1%{?dist}",
            f"Update to upstream QQ Music {version}"))
    CHANGED.append("qqmusic")
    return f"qqmusic: {current} -> {version}"


def sync_wps(dry_run):
    """WPS Office: version-independent rolling RPM; sniff the header."""
    spec = read_spec("wps-office")
    current = spec_field(spec, "Version")
    name, version = rpm_header_sniff(WPS_ROLLING_URL, WPS_HEADER_RANGE)
    if name != "wps-office":
        raise RuntimeError(f"Unexpected rolling RPM name: {name}")
    if rpm_vercmp(version, current) <= 0:
        return f"wps-office: up to date ({current})"
    if not dry_run:
        write_spec("wps-office", bump_spec(
            "wps-office", spec, version, "1%{?dist}",
            f"Update to upstream WPS Office {version} (rolling RPM)"))
    CHANGED.append("wps-office")
    return f"wps-office: {current} -> {version}"


def sync_dingtalk(dry_run):
    """DingTalk: derive version from the update JSON's description.

    The gray update JSON lags behind actual releases but is the only
    machine-readable source. "版本：X-Release.Y" maps to the Release
    deb URL com.alibabainc.dingtalk_X.Y_amd64.deb, which is verified
    with a range request before bumping.
    """
    spec = read_spec("dingtalk")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(DINGTALK_GRAY_JSON, headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        info = json.load(response)
    desc = info["install"]["description"]
    match = re.search(r"版本：([0-9.]+)-Release\.([0-9]+)", desc)
    if not match:
        raise RuntimeError(f"Cannot parse DingTalk version from: {desc[:80]}")
    version = f"{match.group(1)}.{match.group(2)}"
    url = ("https://dtapp-pub.dingtalk.com/dingtalk-desktop/"
           f"xc_dingtalk_update/linux_deb/Release/"
           f"com.alibabainc.dingtalk_{version}_amd64.deb")
    head = urllib.request.Request(url, headers={**USER_AGENT,
                                   "Range": "bytes=0-1023"})
    urllib.request.urlopen(head, timeout=60)  # 404 -> raise, no bump
    if rpm_vercmp(version, current) <= 0:
        return f"dingtalk: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{url}", spec, count=1)
        write_spec("dingtalk", bump_spec(
            "dingtalk", spec, version, "1%{?dist}",
            f"Update to upstream DingTalk {version}"))
    CHANGED.append("dingtalk")
    return f"dingtalk: {current} -> {version}"


def sync_telegram(dry_run):
    """Telegram Desktop: GitHub releases of telegramdesktop/tdesktop
    (tag v<version>, Linux portable asset td-setup-linux-x64-<version>.tar.xz).
    """
    spec = read_spec("telegram-desktop")
    current = spec_field(spec, "Version")
    release = latest_release(TELEGRAM_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected telegram-desktop tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"telegram-desktop: up to date ({current})"
    require_asset(release, f"td-setup-linux-x64-{version}.tar.xz")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{TELEGRAM_REPO}/releases/download/"
                      rf"v{version}/td-setup-linux-x64-{version}.tar.xz",
                      spec, count=1)
        write_spec("telegram-desktop", bump_spec(
            "telegram-desktop", spec, version, "1%{?dist}",
            f"Update to upstream Telegram Desktop {tag}"))
    CHANGED.append("telegram-desktop")
    return f"telegram-desktop: {current} -> {version}"


def sync_zcode(dry_run):
    """ZCode: Z.ai release manifest API (YAML with version + CDN file URLs).

    Linux installers are not on GitHub Releases; the manifest endpoint
    https://zcode.z.ai/api/v1/releases/electron/manifest
    ?platform=linux-x64&channel=stable lists the versioned RPM on
    cdn-zcode.z.ai. Both Version and Source0 are rewritten on update.
    """
    spec = read_spec("zcode")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(ZCODE_MANIFEST_URL, headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        manifest = response.read().decode("utf-8", "replace")
    version_hit = re.search(r"(?m)^version:\s*([0-9][0-9.]*)\s*$", manifest)
    url_hit = re.search(
        r"(?m)^\s*-\s*url:\s*(https://cdn-zcode\.z\.ai/\S+\.rpm)\s*$",
        manifest)
    if not version_hit or not url_hit:
        raise RuntimeError("ZCode manifest missing version or rpm URL")
    version = version_hit.group(1)
    if rpm_vercmp(version, current) <= 0:
        return f"zcode: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{url_hit.group(1)}",
                      spec, count=1)
        write_spec("zcode", bump_spec(
            "zcode", spec, version, "1%{?dist}",
            f"Update to upstream ZCode {version}"))
    CHANGED.append("zcode")
    return f"zcode: {current} -> {version}"


def sync_opencode(dry_run):
    """opencode CLI: GitHub releases (tag v<version>, opencode-linux-x64.tar.gz)."""
    spec = read_spec("opencode")
    current = spec_field(spec, "Version")
    release = latest_release(OPENCODE_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected opencode tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"opencode: up to date ({current})"
    require_asset(release, "opencode-linux-x64.tar.gz")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{OPENCODE_REPO}/releases/download/"
                      rf"v{version}/opencode-linux-x64.tar.gz", spec, count=1)
        write_spec("opencode", bump_spec(
            "opencode", spec, version, "1%{?dist}",
            f"Update to upstream opencode {tag}"))
    CHANGED.append("opencode")
    return f"opencode: {current} -> {version}"


def sync_opencode_desktop(dry_run):
    """opencode desktop (Electron): same GitHub release as the CLI, but the
    upstream RPM's own package name is "opencode"; this COPR package is
    registered as opencode-desktop.
    """
    spec = read_spec("opencode-desktop")
    current = spec_field(spec, "Version")
    release = latest_release(OPENCODE_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected opencode-desktop tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"opencode-desktop: up to date ({current})"
    require_asset(release, "opencode-desktop-linux-x86_64.rpm")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{OPENCODE_REPO}/releases/download/"
                      rf"v{version}/opencode-desktop-linux-x86_64.rpm",
                      spec, count=1)
        write_spec("opencode-desktop", bump_spec(
            "opencode-desktop", spec, version, "1%{?dist}",
            f"Update to upstream opencode desktop {tag}"))
    CHANGED.append("opencode-desktop")
    return f"opencode-desktop: {current} -> {version}"


def sync_claude_code(dry_run):
    """Claude Code: Anthropic's GCS release channel.

    The "stable" pointer file names the version the official native
    installer ships; the binary lives at <channel>/<version>/linux-x64/claude.
    """
    spec = read_spec("claude-code")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(f"{CLAUDE_GCS_BASE}/stable", headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        version = response.read().decode("utf-8", "replace").strip()
    if not re.fullmatch(r"[0-9][0-9.]*", version):
        raise RuntimeError(f"Unexpected Claude Code stable version: {version}")
    if rpm_vercmp(version, current) <= 0:
        return f"claude-code: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>{CLAUDE_GCS_BASE}/{version}/linux-x64/claude",
                      spec, count=1)
        write_spec("claude-code", bump_spec(
            "claude-code", spec, version, "1%{?dist}",
            f"Update to upstream Claude Code {version} (stable channel)"))
    CHANGED.append("claude-code")
    return f"claude-code: {current} -> {version}"


def sync_pi(dry_run):
    """pi: GitHub releases of earendil-works/pi (tag v<version>,
    asset pi-linux-x64.tar.gz). The npm package @mariozechner/pi is an
    unrelated vLLM tool, not this project.
    """
    spec = read_spec("pi")
    current = spec_field(spec, "Version")
    release = latest_release(PI_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected pi tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"pi: up to date ({current})"
    require_asset(release, "pi-linux-x64.tar.gz")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{PI_REPO}/releases/download/"
                      rf"v{version}/pi-linux-x64.tar.gz", spec, count=1)
        write_spec("pi", bump_spec(
            "pi", spec, version, "1%{?dist}",
            f"Update to upstream pi {tag}"))
    CHANGED.append("pi")
    return f"pi: {current} -> {version}"


def sync_codex(dry_run):
    """Codex CLI: GitHub releases of openai/codex (tag rust-v<version>,
    asset codex-x86_64-unknown-linux-musl.tar.gz)."""
    spec = read_spec("codex")
    current = spec_field(spec, "Version")
    release = latest_release(CODEX_REPO)
    tag = release["tag_name"]
    match = re.fullmatch(r"rust-v([0-9][\w.]*)", tag)
    if not match:
        raise RuntimeError(f"Unexpected codex tag format: {tag}")
    version = match.group(1)
    if rpm_vercmp(version, current) <= 0:
        return f"codex: up to date ({current})"
    require_asset(release, "codex-x86_64-unknown-linux-musl.tar.gz")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{CODEX_REPO}/releases/download/"
                      rf"rust-v{version}/codex-x86_64-unknown-linux-musl.tar.gz",
                      spec, count=1)
        write_spec("codex", bump_spec(
            "codex", spec, version, "1%{?dist}",
            f"Update to upstream Codex {tag}"))
    CHANGED.append("codex")
    return f"codex: {current} -> {version}"


def sync_magpie(dry_run):
    """Magpie: GitHub releases of yetone/magpie-releases (tag v<version>,
    raw binaries magpie-linux-amd64 + magpie-cli-linux-amd64, both required)."""
    spec = read_spec("magpie")
    current = spec_field(spec, "Version")
    release = latest_release(MAGPIE_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected magpie tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"magpie: up to date ({current})"
    require_asset(release, "magpie-linux-amd64")
    require_asset(release, "magpie-cli-linux-amd64")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{MAGPIE_REPO}/releases/download/"
                      rf"v{version}/magpie-linux-amd64", spec, count=1)
        spec = re.sub(r"(?m)^(Source1:\s*).*$",
                      rf"\g<1>https://github.com/{MAGPIE_REPO}/releases/download/"
                      rf"v{version}/magpie-cli-linux-amd64", spec, count=1)
        write_spec("magpie", bump_spec(
            "magpie", spec, version, "1%{?dist}",
            f"Update to upstream Magpie {tag}"))
    CHANGED.append("magpie")
    return f"magpie: {current} -> {version}"


def sync_ccswitch(dry_run):
    """ccswitch: GitHub releases of farion1231/cc-switch (tag v<version>,
    asset CC-Switch-v<version>-Linux-x86_64.rpm). The COPR package is
    registered as "ccswitch" (spec Name:); the folder stays ccswitch too.
    """
    spec = read_spec("ccswitch")
    current = spec_field(spec, "Version")
    release = latest_release(CCSWITCH_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected ccswitch tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"ccswitch: up to date ({current})"
    require_asset(release, f"CC-Switch-v{version}-Linux-x86_64.rpm")
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$",
                      rf"\g<1>https://github.com/{CCSWITCH_REPO}/releases/download/"
                      rf"v{version}/CC-Switch-v{version}-Linux-x86_64.rpm",
                      spec, count=1)
        write_spec("ccswitch", bump_spec(
            "ccswitch", spec, version, "1%{?dist}",
            f"Update to upstream CC Switch {tag}"))
    CHANGED.append("ccswitch")
    return f"ccswitch: {current} -> {version}"


def sync_codebuddy_ide(dry_run):
    """CodeBuddy IDE: Tencent's update API
    (copilot.tencent.com/v2/update?platform=ide-linux-x64) returns the
    version and the full .deb URL on download.codebuddy.cn (domestic
    channel; the international backend has no Linux configuration).
    Both Version and Source0 are rewritten on update.
    """
    spec = read_spec("codebuddy-ide")
    current = spec_field(spec, "Version")
    req = urllib.request.Request(CODEBUDDY_IDE_API, headers=USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as response:
        info = json.load(response)
    version, url = info["version"], info["url"]
    if not re.fullmatch(r"[0-9][0-9.]*", version):
        raise RuntimeError(f"Unexpected CodeBuddy IDE version: {version}")
    if (not url.startswith("https://download.codebuddy.cn/")
            or version not in url
            or not url.endswith(".deb")):
        raise RuntimeError(f"Unexpected CodeBuddy IDE download URL: {url}")
    if rpm_vercmp(version, current) <= 0:
        return f"codebuddy-ide: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{url}", spec, count=1)
        write_spec("codebuddy-ide", bump_spec(
            "codebuddy-ide", spec, version, "1%{?dist}",
            f"Update to upstream CodeBuddy IDE {version}"))
    CHANGED.append("codebuddy-ide")
    return f"codebuddy-ide: {current} -> {version}"


def selftest():
    cases = [
        ("0.9.4", "0.9.4", 0),
        ("0.9.9", "0.9.10", -1),
        ("0.9.10", "0.9.9", 1),
        ("4.1.13.26", "4.1.13.26", 0),
        ("4.2.0.1", "4.1.13.26", 1),
        ("1.0", "1", 1),
        ("3.0.1.684", "3.0.1.684", 0),
        ("1.0a", "1.0", 1),
    ]
    for a, b, expected in cases:
        result = rpm_vercmp(a, b)
        assert result == expected, f"rpm_vercmp({a}, {b}) = {result}, want {expected}"

    assert waydroid_release_for_update(
        "20261121", "a" * 40, "20261121", "a" * 40, "1%{?dist}") is None
    assert waydroid_release_for_update(
        "20261121", "a" * 40, "20261121", "b" * 40, "1%{?dist}") == "2%{?dist}"
    assert waydroid_release_for_update(
        "20261120", "a" * 40, "20261121", "b" * 40, "4%{?dist}") == "1%{?dist}"
    assert waydroid_release_for_update(
        "20261122", "a" * 40, "20261121", "b" * 40, "1%{?dist}") is None

    changelog = bump_spec(
        "test", "%changelog\n", "1.2.3", "%{upstream_rel}%{?dist}",
        "test macro-based Release", changelog_release="9")
    assert " - 1.2.3-9\n" in changelog, changelog
    print("selftest OK")


def main():
    dry_run = "--dry-run" in sys.argv
    if "--selftest" in sys.argv:
        selftest()
        return
    checks = [
        ("FlClash", sync_flclash),
        ("fcitx5-wetypex", sync_wetypex),
        ("flyline", sync_flyline),
        ("wechat", sync_wechat),
        ("workbuddy", sync_workbuddy),
        ("linuxqq", sync_linuxqq),
        ("wemeet", sync_wemeet),
        ("iptvnator", sync_iptvnator),
        ("waydroid-script", sync_waydroid),
        ("nerd-fonts-cascadia-code", sync_nerdfonts),
        ("lazyvim", sync_lazyvim),
        ("zed", sync_zed),
        ("starship", sync_starship),
        ("qqmusic", sync_qqmusic),
        ("wps-office", sync_wps),
        ("dingtalk", sync_dingtalk),
        ("telegram-desktop", sync_telegram),
        ("zcode", sync_zcode),
        ("opencode", sync_opencode),
        ("opencode-desktop", sync_opencode_desktop),
        ("claude-code", sync_claude_code),
        ("pi", sync_pi),
        ("codex", sync_codex),
        ("magpie", sync_magpie),
        ("ccswitch", sync_ccswitch),
        ("codebuddy-ide", sync_codebuddy_ide),
    ]
    errors = []
    for package, check in checks:
        try:
            print(check(dry_run))
        except Exception as exc:
            # An outage or format change at one upstream must not prevent
            # unrelated packages from updating during this scheduled run.
            errors.append(package)
            print(
                f"ERROR: {package} update check failed "
                f"({type(exc).__name__}): {exc}",
                file=sys.stderr)

    changed = sorted(set(CHANGED))
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as fd:
            fd.write("changed=" + " ".join(changed) + "\n")
            fd.write("errors=" + " ".join(errors) + "\n")
    if changed:
        print(f"CHANGED: {' '.join(changed)}")
    if errors:
        print(f"UPSTREAM_CHECK_ERRORS: {' '.join(errors)}")


if __name__ == "__main__":
    main()