%global debug_package %{nil}
%global __os_install_post %{nil}
# Tencent's CDN (qqdl.gtimg.cn) rejects datacenter IPs, so no build machine
# (COPR builder, GitHub runner, ...) can fetch the payload. This RPM is
# therefore an empty shell, mirroring flatpak's "extra-data" approach: at
# INSTALL time %post downloads the official RPM on the end user's machine
# (which can reach the CDN), extracts the payload into the filesystem and
# records a file list under /var/lib/linuxqq for clean upgrade/uninstall.
# Version bumps only rewrite Version + qq_rpm_url below (done automatically
# by scripts/check-updates.py from Tencent's download config), so the whole
# maintenance flow stays fully automatic.
#
# Trade-offs vs. a regular repack:
#   - the payload files are not owned by RPM (not in `rpm -V`, dnf history
#     shows a tiny package); integrity relies on the TLS connection to the
#     official Tencent CDN, same as downloading from im.qq.com manually;
#   - installing requires network access to qqdl.gtimg.cn.

Name:           linuxqq
Version:        3.2.35
Release:        1%{?dist}
Summary:        QQ desktop client from Tencent (NTQQ)
License:        LicenseRef-Tencent-QQ-Software-License
URL:            https://im.qq.com/linuxqq/
# Official x86_64 RPM; bumped automatically by scripts/check-updates.py.
%global qq_rpm_url https://qqdl.gtimg.cn/qqfile/QQNTV2/9.9.37/release/816b3c79/QQ_3.2.35_261103_x86_64_01.rpm

ExclusiveArch:  x86_64

# Requires mirror the upstream RPM's dependency list (Fedora-native names).
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libnotify
Requires:       libuuid
Requires:       nss
Requires:       xdg-utils
# Needed by the install-time downloader scriptlet.
Requires:       curl
Requires:       cpio

%description
QQ (NTQQ) desktop client for Linux, distributed by Tencent.

This is an installer shell package: because Tencent's download CDN refuses
datacenter IPs, the payload cannot be fetched at package build time. Instead,
the official RPM is downloaded from Tencent on your machine during
installation (like flatpak's extra-data), extracted in place, and tracked
with a file list for clean upgrades and uninstall.

%pre
# Nothing to clean: on upgrade %post diffs the old and new file lists and
# removes only files dropped by the new upstream version, so a failed
# download never destroys a working installation.

%post
tmpdir=$(mktemp -d /var/tmp/linuxqq-XXXXXX) || exit 1
trap 'rm -rf "$tmpdir"' EXIT

echo "linuxqq: downloading %{qq_rpm_url} ..."
curl -fsSL --retry 5 --retry-delay 3 -o "$tmpdir/qq.rpm" '%{qq_rpm_url}' \
    || { echo "linuxqq: download failed; check your network and run: dnf reinstall linuxqq" >&2; exit 1; }
test -s "$tmpdir/qq.rpm" || { echo "linuxqq: empty download" >&2; exit 1; }

mkdir -p /var/lib/linuxqq

# Payload paths relative to / (files, symlinks and directories).
list_payload() {
    rpm2cpio "$tmpdir/qq.rpm" | cpio -it --quiet \
        | sed 's|^\./||' | grep -v '/$' | sort
}

# On upgrade, remove payload entries that the new upstream version no longer
# ships (old file list minus new list), then extract over the old files.
if [ -f /var/lib/linuxqq/filelist ]; then
    sort /var/lib/linuxqq/filelist > "$tmpdir/old.list"
    list_payload > "$tmpdir/new.list"
    comm -23 "$tmpdir/old.list" "$tmpdir/new.list" > "$tmpdir/stale.list"
    # Files/symlinks first, then empty directories deepest-first.
    while IFS= read -r f; do
        [ -n "$f" ] && rm -f "/$f"
    done < "$tmpdir/stale.list"
    while IFS= read -r f; do
        [ -n "$f" ] && rmdir "/$f" 2>/dev/null || :
    done < <(sort -r "$tmpdir/stale.list")
fi

(cd / && rpm2cpio "$tmpdir/qq.rpm" | cpio -idm --quiet --no-absolute-filenames)

list_payload > /var/lib/linuxqq/filelist.new \
    && mv /var/lib/linuxqq/filelist.new /var/lib/linuxqq/filelist

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lib/linuxqq/filelist ]; then
        # Files/symlinks first, then empty directories deepest-first.
        while IFS= read -r f; do
            [ -n "$f" ] && rm -f "/$f"
        done < /var/lib/linuxqq/filelist
        while IFS= read -r f; do
            [ -n "$f" ] && rmdir "/$f" 2>/dev/null || :
        done < <(sort -r /var/lib/linuxqq/filelist)
        rm -f /var/lib/linuxqq/filelist
    fi
    rmdir /var/lib/linuxqq 2>/dev/null || :
    rm -rf /opt/QQ
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files
%ghost %dir /var/lib/linuxqq
%ghost /var/lib/linuxqq/filelist

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-1
- Installer shell package: download the official Tencent RPM at install time
  (Tencent's CDN blocks build machines), like flatpak's extra-data
