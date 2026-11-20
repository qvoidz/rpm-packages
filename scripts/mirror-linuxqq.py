#!/usr/bin/env python3
"""Mirror the official Linux QQ RPM into this repo's GitHub releases.

Tencent's CDN (qqdl.gtimg.cn) serves 403 to datacenter IPs, so COPR builders
and GitHub Actions cannot download the RPM directly. This script must run on
a machine with China network access (e.g. the user's own machine). It:

1. reads the official download config (pcConfig.json) for the current
   x86_64 RPM URL and version;
2. skips everything if release `linuxqq-<version>` already has the asset;
3. downloads the RPM and uploads it as a GitHub release asset
   (release tag `linuxqq-<version>`);
4. bumps linuxqq.spec (Version + Source0), commits and pushes.

After a successful run, the normal CI (check-updates.py) / copr-cli
buildscm can build linuxqq from the mirrored source.

Usage:
  python3 scripts/mirror-linuxqq.py            # mirror + bump spec + push
  python3 scripts/mirror-linuxqq.py --build    # also trigger the COPR build
  python3 scripts/mirror-linuxqq.py --dry-run  # report state, download nothing

Auth: GITHUB_TOKEN environment variable, or the token stored by git
credential helper for https://github.com (used by `git push`).
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
QQ_CONFIG_URL = ("https://cdn-go.cn/qq-web/im.qq.com_new/latest/"
                 "rainbow/pcConfig.json")
REPO = "qvoidz/rpm-packages"
API = f"https://api.github.com/repos/{REPO}"
UA = {"User-Agent": "qvoidz-rpm-packages-qq-mirror"}


def github_token():
    """Return the GitHub token: $GITHUB_TOKEN or git credential helper."""
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    out = subprocess.check_output(
        ["git", "credential", "fill"],
        input="url=https://github.com\n\n", text=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(pathlib.Path.home()),
             "LC_ALL": "C"})
    creds = dict(line.split("=", 1) for line in out.splitlines()
                 if "=" in line)
    return creds.get("password") or creds.get("token") or None


def api_request(path, token, method="GET", data=None, raw=False):
    headers = dict(UA)
    headers["Accept"] = "application/vnd.github+json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, headers=headers,
                                 method=method,
                                 data=json.dumps(data).encode() if data else None)
    with urllib.request.urlopen(req, timeout=120) as response:
        if raw:
            return response.read()
        return json.load(response)


def current_official():
    with urllib.request.urlopen(urllib.request.Request(
            QQ_CONFIG_URL, headers=UA), timeout=60) as response:
        config = json.load(response)
    urls = re.findall(r"https://qqdl\.gtimg\.cn/[^\"\\]+\.rpm",
                      json.dumps(config, ensure_ascii=False))
    matches = [u for u in dict.fromkeys(urls)
               if re.search(r"QQ_[\d.]+_\d+_x86_64_\d+\.rpm$", u)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one x86_64 QQ RPM URL, found {matches}")
    url = matches[0]
    version = re.search(r"QQ_([\d.]+)_\d+_x86_64", url).group(1)
    return version, url


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--build", action="store_true",
                        help="trigger the COPR build after mirroring")
    args = parser.parse_args()

    version, official_url = current_official()
    asset_name = official_url.rsplit("/", 1)[1]
    tag = f"linuxqq-{version}"
    print(f"official: {version} ({official_url})")

    token = github_token()
    try:
        release = api_request(f"/releases/tags/{tag}", token)
        assets = [a["name"] for a in release.get("assets", [])]
        if asset_name in assets:
            print(f"release {tag} already has {asset_name}; nothing to do")
            return
        upload_url = release["upload_url"].split("{")[0]
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        release = None
        upload_url = None

    if args.dry_run:
        print(f"dry-run: would mirror {asset_name} into release {tag}")
        return

    # 1. Download the RPM (needs China network access).
    target = ROOT / ".workbuddy" / "tmp"
    target.mkdir(parents=True, exist_ok=True)
    rpm_path = target / asset_name
    print(f"downloading {asset_name} ...")
    urllib.request.urlretrieve(official_url, rpm_path)
    size = rpm_path.stat().st_size
    if size < 100 * 1024 * 1024:
        raise RuntimeError(f"downloaded file too small ({size} bytes)")
    print(f"downloaded {size / 1e6:.0f} MB")

    # 2. Create the release if needed.
    if release is None:
        body = (f"Mirror of Tencent's official Linux QQ RPM {version}.\n\n"
                f"Source: {official_url}\n\n"
                "Tencent's CDN rejects datacenter IPs, so COPR fetches the "
                "upstream artifact from here instead.")
        release = api_request("/releases", token, method="POST", data={
            "tag_name": tag,
            "target_commitish": "main",
            "name": f"Linux QQ {version} (upstream mirror)",
            "body": body,
        })
        print(f"created release {tag}")

    # 3. Upload the asset.
    upload = urllib.request.Request(
        upload_url + f"?name={asset_name}", method="POST",
        data=rpm_path.read_bytes(),
        headers={**UA, "Authorization": f"Bearer {token}",
                 "Content-Type": "application/x-rpm"})
    with urllib.request.urlopen(upload, timeout=600) as response:
        info = json.load(response)
    print(f"uploaded {info['name']} ({info['size'] / 1e6:.0f} MB)")
    rpm_path.unlink()

    # 4. Bump the spec, commit and push.
    spec_path = ROOT / "linuxqq" / "linuxqq.spec"
    text = spec_path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(Version:\s*)\S+", rf"\g<1>{version}", text, count=1)
    mirror_url = (f"https://github.com/{REPO}/releases/download/"
                  f"{tag}/{asset_name}")
    text = re.sub(r"(?m)^(Source0:\s*).*$", rf"\g<1>{mirror_url}",
                  text, count=1)
    spec_path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", "linuxqq/linuxqq.spec"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m",
                    f"linuxqq: mirror upstream {version}"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT, check=True)
    print("spec bumped and pushed")

    if args.build:
        subprocess.run(
            ["copr-cli", "buildscm", "--nowait",
             "--clone-url", f"https://github.com/{REPO}",
             "--spec", "linuxqq/linuxqq.spec", "qvoidz/rpm-packages"],
            cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
