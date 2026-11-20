#!/usr/bin/env python3
"""Guard the bundled-ELF dependency filters found by Fedora 45 install tests."""
from __future__ import annotations

import re
import sys
from pathlib import Path

CASES = {
    "dingtalk/dingtalk.spec": [
        "libmeeting_sdk.so()(64bit)",
        "libprgbase.so()(64bit)",
        "libsodium.so.23()(64bit)",
        "libssl.so.1.1()(64bit)",
        "libssl.so.1.1(OPENSSL_1_1_0)(64bit)",
        "libssl.so.1.1(OPENSSL_1_1_1)(64bit)",
        "libswresample.so.5()(64bit)",
        "libswresample.so.5(LIBSWRESAMPLE_5)(64bit)",
        "libswscale.so.8()(64bit)",
        "libswscale.so.8(LIBSWSCALE_8)(64bit)",
        "libsync.so()(64bit)",
        "libutforpc.so()(64bit)",
        "libxcb-util.so.0()(64bit)",
    ],
    "fcitx5-wetypex/fcitx5-wetypex.spec": [
        "libkqueue.so.0()(64bit)",
    ],
    "netease-cloud-music/netease-cloud-music.spec": [
        "libutil-setid.so.0()(64bit)",
        "libutil-setid.so.0(SAMBA_4.7.6_UBUNTU)(64bit)",
        "libutil-tdb.so.0()(64bit)",
        "libutil-tdb.so.0(SAMBA_4.7.6_UBUNTU)(64bit)",
        "libvpx.so.5()(64bit)",
        "libwacom.so.2()(64bit)",
        "libwebp.so.6()(64bit)",
        "libwinbind-client.so.0()(64bit)",
        "libwinbind-client.so.0(SAMBA_4.7.6_UBUNTU)(64bit)",
        "libwind-samba4.so.0()(64bit)",
        "libwind-samba4.so.0(HEIMDAL_WIND_1.0)(64bit)",
        "libx264.so.152()(64bit)",
        "libx265.so.146()(64bit)",
    ],
    "qqmusic/qqmusic.spec": [
        "libffmpeg.so()(64bit)",
    ],
    "wechat/wechat.spec": [
        "libmmcronet.so()(64bit)",
        "libmmmojo.so()(64bit)",
        "libowl.so()(64bit)",
        "libroam_migration.so()(64bit)",
        "libtxffmpeg.so()(64bit)",
        "libvoipChannel.so()(64bit)",
        "libvoipCodec.so()(64bit)",
        "libvoipComm.so()(64bit)",
        "libwxocr.so()(64bit)",
        "libwxtrans.so()(64bit)",
        "libxeditor_app.so()(64bit)",
        "libxfile.so()(64bit)",
        "libxfile_pdfium.so()(64bit)",
    ],
    "wemeet/wemeet.spec": [
        "libwemeet_framework.so()(64bit)",
        "libwemeet_migration.so()(64bit)",
        "libwemeet_module_api.so()(64bit)",
        "libwemeet_platform.so()(64bit)",
        "libwemeet_qt.so()(64bit)",
        "libwemeet_util.so()(64bit)",
        "libxcast.so()(64bit)",
        "libxcast_codec.so()(64bit)",
        "libxnn.so()(64bit)",
        "libxnn_core.so()(64bit)",
        "libxnn_media.so()(64bit)",
        "libxnn_media.so(libxnn_media)(64bit)",
        "libyuv.so()(64bit)",
    ],
    "workbuddy/workbuddy.spec": [
        "libffmpeg.so()(64bit)",
    ],
    "wps-office/wps-office.spec": [
        "libwppapi.so()(64bit)",
        "libwppcore.so()(64bit)",
        "libwpsapi.so()(64bit)",
        "libwpsapiex.so()(64bit)",
        "libwpsbox.so()(64bit)",
        "libwpscore.so()(64bit)",
        "libwpsio.so()(64bit)",
        "libwpsuil.so()(64bit)",
        "libwpswordtool.so()(64bit)",
        "libxercesc3.so()(64bit)",
    ],
}

# These host requirements must remain visible to Fedora's dependency solver.
HOST_REQUIREMENTS = (
    "libc.so.6(GLIBC_2.34)(64bit)",
    "libgtk-3.so.0()(64bit)",
)

def main() -> int:
    failures: list[str] = []
    for spec_name, requirements in CASES.items():
        path = Path(spec_name)
        if not path.is_file():
            failures.append(f"{spec_name}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^%global __requires_exclude\s+(.+)$", text, re.MULTILINE)
        if not match:
            failures.append(f"{spec_name}: missing __requires_exclude")
            continue
        try:
            pattern = re.compile(match.group(1))
        except re.error as exc:
            failures.append(f"{spec_name}: invalid __requires_exclude: {exc}")
            continue
        for requirement in requirements:
            if not pattern.search(requirement):
                failures.append(f"{spec_name}: filter does not match {requirement}")
        for requirement in HOST_REQUIREMENTS:
            if pattern.search(requirement):
                failures.append(f"{spec_name}: filter hides host requirement {requirement}")
        print(f"Checked {spec_name}: {len(requirements)} bundled sonames")
    if failures:
        print("\n".join(f"ERROR: {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Bundled runtime dependency filters passed ({len(CASES)} specs).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
