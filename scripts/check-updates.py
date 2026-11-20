#!/usr/bin/env python3
"""Detect new upstream releases and bump the COPR spec files.

Packages and their upstream sources:

- flclash        GitHub releases of chen08209/FlClash (tag v<version>,
                 asset FlClash-dev-<version>-linux-amd64.rpm).
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
                 filename (QQ_<version>_<date>_x86_64_01.rpm).
- wemeet         Tencent Meeting's download API
                 (meeting.tencent.com/web-service/query-download-info)
                 returns version + full .deb URL. The .deb is repacked
                 into an RPM.

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


def bump_spec(pkg, text, version, release, message):
    """Rewrite Version/Release and prepend a changelog entry."""
    text = re.sub(r"(?m)^(Version:\s*)\S+", rf"\g<1>{version}", text, count=1)
    text = re.sub(r"(?m)^(Release:\s*)\S+", rf"\g<1>{release}", text, count=1)
    entry = (f"* {changelog_date()} COPR Builder <copr@example.invalid> "
             f"- {version}-{release.split('%')[0]}\n"
             f"- {message}\n")
    return text.replace("%changelog\n", "%changelog\n" + entry, 1)


def require_asset(release, name):
    assets = [a["name"] for a in release.get("assets", [])]
    if name not in assets:
        raise RuntimeError(
            f"{release.get('tag_name')}: expected asset {name}, "
            f"found {assets}")


def sync_flclash(dry_run):
    spec = read_spec("flclash")
    current = spec_field(spec, "Version")
    release = latest_release(FLCLASH_REPO)
    tag = release["tag_name"]
    if not tag.startswith("v"):
        raise RuntimeError(f"Unexpected FlClash tag format: {tag}")
    version = tag[1:]
    if rpm_vercmp(version, current) <= 0:
        return f"flclash: up to date ({current})"
    require_asset(release, f"FlClash-dev-{version}-linux-amd64.rpm")
    if not dry_run:
        write_spec("flclash", bump_spec(
            "flclash", spec, version, "1%{?dist}",
            f"Update to upstream FlClash {tag}"))
    CHANGED.append("flclash")
    return f"flclash: {current} -> {version}"


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
            f"Update to upstream {tag}"))
    CHANGED.append("fcitx5-wetypex")
    return f"fcitx5-wetypex: {current_version}-{current_rel} -> {version}-{upstream_rel}"


def rpm_header_sniff(url):
    """Fetch only the RPM header (HTTP Range request) and read name/version."""
    req = urllib.request.Request(
        url, headers={**USER_AGENT, "Range": WECHAT_HEADER_RANGE})
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
    # Sanity check the payload header before bumping.
    name, _ = rpm_header_sniff(url)
    if name != "workbuddy":
        raise RuntimeError(f"Unexpected WorkBuddy RPM package name: {name}")
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
    the asset filename (QQ_<version>_<date>_x86_64_01.rpm). The RPM header is
    NOT sniffed because Tencent's CDN rejects some datacenter IPs (including
    GitHub-hosted runners and COPR builders); the URL must only be valid.
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
    url = matches[0]
    match = re.search(r"QQ_([\d.]+)_\d+_x86_64", url)
    if not match:
        raise RuntimeError(f"Cannot parse QQ version from URL: {url}")
    version = match.group(1)
    if rpm_vercmp(version, current) <= 0:
        return f"linuxqq: up to date ({current})"
    if not dry_run:
        spec = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{url}", spec, count=1)
        write_spec("linuxqq", bump_spec(
            "linuxqq", spec, version, "1%{?dist}",
            f"Update to upstream Linux QQ {version}"))
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
    print("selftest OK")


def main():
    dry_run = "--dry-run" in sys.argv
    if "--selftest" in sys.argv:
        selftest()
        return
    messages = [
        sync_flclash(dry_run),
        sync_wetypex(dry_run),
        sync_flyline(dry_run),
        sync_wechat(dry_run),
        sync_workbuddy(dry_run),
        sync_linuxqq(dry_run),
        sync_wemeet(dry_run),
    ]
    for message in messages:
        print(message)
    changed = sorted(set(CHANGED))
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as fd:
            fd.write("changed=" + " ".join(changed) + "\n")
    if changed:
        print(f"CHANGED: {' '.join(changed)}")


if __name__ == "__main__":
    main()
