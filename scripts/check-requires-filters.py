#!/usr/bin/env python3
"""Guard the bundled-ELF dependency filters found by Fedora 45 install tests.

Two filter schemes exist in this repository:

1. Closed scheme (current standard for closed-source repacks):
   %global __requires_exclude ^.*$  plus an explicit Requires list generated
   mechanically from `rpm -qpR` on the payload (Fedora-provided sonames are
   declared; bundled private libraries resolve via $ORIGIN runpath). Here the
   automatic filter hides EVERYTHING, so the guard instead asserts that the
   spec declares the root host dependency (glibc) explicitly. The full host
   soname list is generated mechanically at build time and verified by the
   Fedora 45 container install/verify tests (scripts/verify-packages.sh),
   which is the real completeness check; a static guard cannot re-run that.

2. Narrow scheme (legacy, e.g. musl payloads): the filter enumerates only
   bundled/private sonames, so it must NOT swallow host requirements that
   rpm's automatic dependency scan would otherwise expose.
"""
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

# Root host dependency every ELF payload needs. Under the closed filter it is
# hidden along with everything else, so the spec must declare it explicitly,
# either as a soname Requires (libc.so.6, with or without a symbol version)
# or as a package Requires (glibc).
GLIBC_SONAME = "libc.so.6"
GLIBC_PACKAGES = ("glibc",)

CLOSED_FILTER = re.compile(r"^\^\.\*\$$")


def is_closed_filter(pattern: str) -> bool:
    return CLOSED_FILTER.match(pattern.strip()) is not None


def declares_glibc(text: str) -> bool:
    if GLIBC_SONAME in text:
        return True
    return any(
        re.search(rf"(?m)^Requires:\s*{re.escape(pkg)}\s*$", text)
        for pkg in GLIBC_PACKAGES
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
        if is_closed_filter(match.group(1)):
            if not declares_glibc(text):
                failures.append(
                    f"{spec_name}: closed filter hides every host requirement "
                    f"but the spec declares neither {GLIBC_SONAME} nor "
                    f"{GLIBC_PACKAGES} explicitly")
        else:
            # Narrow filter: the legacy host requirements must stay visible.
            for host_req in (GLIBC_SONAME, "libgtk-3.so.0"):
                if pattern.search(f"{host_req}()(64bit)"):
                    failures.append(
                        f"{spec_name}: filter hides host requirement {host_req}")
        print(f"Checked {spec_name}: {len(requirements)} bundled sonames")
    if failures:
        print("\n".join(f"ERROR: {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Bundled runtime dependency filters passed ({len(CASES)} specs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
