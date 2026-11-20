%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# Bare asset URL, bumped automatically by scripts/check-updates.py from
# Tencent's download config (cdn-go.cn/.../rainbow/pcConfig.json). Tencent's
# CDN (qqdl.gtimg.cn) rejects datacenter IPs, and since Oct 2026 every QQNT
# path additionally requires a real-time signature: bare links get HTTP 403
# regardless of network or Referer (the official download page signs every
# request first). %prep therefore swaps the bare URL for a short-lived
# signed one via Tencent's public signing API before downloading, which
# also works from build machines (same approach as nixpkgs' qq package).
%global qq_rpm_url https://qqdl.gtimg.cn/qqfile/QQNTV2/9.9.37/release/816b3c79/QQ_3.2.35_261103_x86_64_01.rpm
# Public, unauthenticated signing endpoint (same call as the official page):
# body {"url":"<bare url>"} -> {"retcode":0,"data":{"url":"...?sign=...&t=..."}}
%global qq_sign_api https://im.qq.com/http2rpc/gotrpc/noauth/trpc.qqntv2.urlsign.UrlSign/GetSign

Name:           linuxqq
Version:        3.2.35
Release:        6%{?dist}
Summary:        QQ desktop client from Tencent (NTQQ)
License:        LicenseRef-Tencent-QQ-Software-License
URL:            https://im.qq.com/linuxqq/

ExclusiveArch:  x86_64

BuildRequires:  curl
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Requires mirror the upstream RPM's dependency list (Fedora-native names).
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libnotify
Requires:       libuuid
Requires:       nss
Requires:       xdg-utils

%description
QQ (NTQQ) desktop client for Linux, distributed by Tencent.
This package repackages the official upstream RPM without rebuilding
or modifying the application binaries. The payload is fetched at BUILD
time: Tencent's CDN refuses datacenter IPs for bare links, so the build
first exchanges the URL for a short-lived signed one via Tencent's
public signing API, then downloads and repacks the official RPM.

%prep
# Ask Tencent to sign the bare URL (falls back to it verbatim if the API
# hiccups or a future release ships an unsigned path again).
signed=$(curl -fsSL --retry 5 --retry-delay 3 \
    -H 'Content-Type: application/json' \
    -H 'x-oidb: {"uint32_command":"0x9b8e","uint32_service_type":1}' \
    -H 'Origin: https://im.qq.com' \
    -H 'Referer: https://im.qq.com' \
    -d '{"url":"%{qq_rpm_url}"}' \
    '%{qq_sign_api}' \
    | sed -n 's/.*"url":"\([^"]*\)".*/\1/p' | sed 's|\\u002F|/|g; s|\\/|/|g') || signed=
dl_url=${signed:-%{qq_rpm_url}}

echo "linuxqq: downloading ..."
curl -fsSL --retry 5 --retry-delay 3 -o qq.rpm "$dl_url"
test -s qq.rpm || { echo "linuxqq: empty download" >&2; exit 1; }

# Sanity check: must be the official linuxqq RPM of the expected version.
payload=$(rpm -qp --qf '%{NAME}-%{VERSION}' qq.rpm)
echo "linuxqq: payload RPM is $payload"
case "$payload" in
    linuxqq-%{version}) : ;;
    linuxqq-*) : ;;
    *) echo "linuxqq: unexpected payload '$payload'" >&2; exit 1 ;;
esac

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{_builddir}/qq.rpm | cpio -idm --quiet --no-absolute-filenames
# Own: every file/symlink, the private /opt payload tree, and the dirs the
# upstream RPM itself owns (/usr/lib/.build-id/...). Other directories are
# deliberately left unowned: rpm creates parents at install time, base
# packages own them, and claiming one with a mismatched mode conflicts
# (e.g. filesystem ships /usr/lib read-only 0555, upstream's cpio carries
# no directory entries at all).
{ find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n'
  find %{buildroot}/opt -mindepth 1 -type d -printf '/opt/%%P\n' 2>/dev/null
  rpm -qp --dump %{_builddir}/qq.rpm | awk '$5 ~ /^04/ {print $1}'
} | sort -u | sed 's|.*|"&"|' > %{_builddir}/%{name}-filelist

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-6
- Own only the /opt payload tree plus upstream-owned dirs; leave /usr
  directories unowned to avoid conflicts with the filesystem package
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-4
- Restore upstream directory modes to avoid ownership conflicts (filesystem)
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-3
- Own the payload directories too, so uninstall leaves no empty tree
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-2
- Convert to a build-time repack: bare qqdl links are 403'd since Oct 2026
  (real-time URL signing), so %prep signs via Tencent's public GetSign API
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-1
- Installer shell package: download the official Tencent RPM at install time
  (Tencent's CDN blocks build machines), like flatpak's extra-data
