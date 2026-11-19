#!/usr/bin/env python3
"""Sync upstream x86_64 RPMs and prepare a static DNF repository."""
import json
import os
import pathlib
import re
import subprocess
import urllib.request

ROOT = pathlib.Path("public")
PKGDIR = ROOT / "x86_64"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def request(url):
    headers = {"User-Agent": "qvoidz-rpm-repository"}
    if "api.github.com" in url and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
        headers["Accept"] = "application/vnd.github+json"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()

def download(url, target):
    data = request(url)
    target.write_bytes(data)

def rpm_info(path):
    fmt = "%{NAME}\n%{VERSION}\n%{RELEASE}\n%{ARCH}\n"
    output = subprocess.check_output(["rpm", "-qp", "--qf", fmt, str(path)], text=True)
    name, version, release, arch = output.strip().splitlines()
    if arch != "x86_64":
        raise RuntimeError(f"{path.name}: expected x86_64, got {arch}")
    return name, version, release, arch

def latest_release(owner_repo):
    return json.loads(request(f"https://api.github.com/repos/{owner_repo}/releases/latest"))

def choose_asset(release, pattern):
    matches = [a for a in release["assets"] if re.fullmatch(pattern, a["name"])]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one asset matching {pattern}, found {[a['name'] for a in matches]}")
    return matches[0]

def sync_release(owner_repo, pattern, expected_name):
    release = latest_release(owner_repo)
    asset = choose_asset(release, pattern)
    target = PKGDIR / asset["name"]
    download(asset["browser_download_url"], target)
    name, version, release_no, arch = rpm_info(target)
    if name != expected_name:
        raise RuntimeError(f"{asset['name']}: expected package {expected_name}, got {name}")
    digest = asset.get("digest", "")
    if digest.startswith("sha256:"):
        import hashlib
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest.split(":", 1)[1]:
            raise RuntimeError(f"SHA-256 mismatch for {asset['name']}")
    print(f"{name} {version}-{release_no}.{arch} from {release['html_url']}")

def sync_wechat():
    target = PKGDIR / "wechat-upstream.rpm"
    download("https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_x86_64.rpm", target)
    name, version, release_no, arch = rpm_info(target)
    if name.lower() not in ("wechat", "weixin"):
        raise RuntimeError(f"Unexpected Tencent RPM package name: {name}")
    target.rename(PKGDIR / f"{name}-{version}-{release_no}.{arch}.rpm")
    print(f"{name} {version}-{release_no}.{arch}")

def main():
    PKGDIR.mkdir(parents=True, exist_ok=True)
    # Keep only the currently published x86_64 build of each application.
    for p in PKGDIR.glob("*.rpm"):
        p.unlink()
    sync_release("chen08209/FlClash", r"FlClash-dev-[0-9][^/]*-linux-amd64\.rpm", "flclash")
    sync_release("panxuc/fcitx5-wetypex", r"fcitx5-wetypex-[0-9][^/]*\.x86_64\.rpm", "fcitx5-wetypex")
    sync_wechat()
    (ROOT / "index.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>qvoidz Fedora RPM Repository</title>"
        "<h1>qvoidz Fedora RPM Repository</h1><p>DNF repository for x86_64 Fedora systems.</p>"
        "<p>Packages are synchronized from their upstream RPM releases.</p>\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
