%global debug_package %{nil}
%global __os_install_post %{nil}
# The payload bundles its own copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires. Suppress all auto-generated provides; the package's own
# name provides are intrinsic and unaffected.
%global __provides_exclude ^.*$
# libffmpeg is shipped inside the upstream application payload.
%global __requires_exclude ^.*$
# QQ Music does not publish RPMs; this package repacks the official
# x86_64 .deb. Tencent signs download URLs, so Source0 points at the
# official download page's file_redirect.fcg CGI, which generates a
# fresh signed URL on every request
# (https://y.qq.com/download/download.html). scripts/check-updates.py
# rewrites both Version and Source0 automatically.
Name:           qqmusic
Version:        1.1.8
Release:        6%{?dist}
Summary:        Tencent QQ Music desktop client for Linux
License:        LicenseRef-Tencent-QQMusic-Software-License
URL:            https://y.qq.com/
Source0:        https://c.y.qq.com/cgi-bin/file_redirect.fcg?bid=dldir&file=ecosfile_plink%2Fmusic_clntupate%2Flinux%2Fother%2Fqqmusic_1.1.8_amd64.deb&sign=1-d1ca4d5c5a8369b26af88e881ba3ac544066a899dcaea29778b35c9f648e6fee-68cb7c1c

ExclusiveArch:  x86_64
BuildRequires:  binutils
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  xz

# Requires mirror the deb's Depends list, mapped to Fedora-native names:
# libgtk-3-0, libnotify4, libnss3, libxss1, libxtst6, xdg-utils,
# libatspi2.0-0, libuuid1, libappindicator3-1, libsecret-1-0.
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libappindicator-gtk3
Requires:       libnotify
Requires:       libsecret
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       nss
Requires:       xdg-utils

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: at-spi2-core
Requires: gtk3
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: libX11-xcb.so.1()(64bit)
Requires: libX11.so.6()(64bit)
Requires: libXScrnSaver
Requires: libXcomposite.so.1()(64bit)
Requires: libXcursor.so.1()(64bit)
Requires: libXdamage.so.1()(64bit)
Requires: libXext.so.6()(64bit)
Requires: libXfixes.so.3()(64bit)
Requires: libXi.so.6()(64bit)
Requires: libXrandr.so.2()(64bit)
Requires: libXrender.so.1()(64bit)
Requires: libXss.so.1()(64bit)
Requires: libXtst
Requires: libXtst.so.6()(64bit)
Requires: libappindicator-gtk3
Requires: libasound.so.2()(64bit)
Requires: libatk-1.0.so.0()(64bit)
Requires: libatk-bridge-2.0.so.0()(64bit)
Requires: libatspi.so.0()(64bit)
Requires: libc.so.6()(64bit)
Requires: libcairo.so.2()(64bit)
Requires: libcups.so.2()(64bit)
Requires: libdbus-1.so.3()(64bit)
Requires: libdl.so.2()(64bit)
Requires: libexpat.so.1()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libgdk-3.so.0()(64bit)
Requires: libgdk_pixbuf-2.0.so.0()(64bit)
Requires: libgio-2.0.so.0()(64bit)
Requires: libglib-2.0.so.0()(64bit)
Requires: libgobject-2.0.so.0()(64bit)
Requires: libgtk-3.so.0()(64bit)
Requires: libm.so.6()(64bit)
Requires: libnotify
Requires: libnspr4.so()(64bit)
Requires: libnss3.so()(64bit)
Requires: libnssutil3.so()(64bit)
Requires: libpango-1.0.so.0()(64bit)
Requires: libpangocairo-1.0.so.0()(64bit)
Requires: libpthread.so.0()(64bit)
Requires: librt.so.1()(64bit)
Requires: libsecret
Requires: libsmime3.so()(64bit)
Requires: libxcb.so.1()(64bit)
Requires: nss
Requires: rtld(GNU_HASH)
Requires: xdg-utils


%description
Tencent QQ Music (QQ音乐) desktop client for Linux, distributed by
Tencent. This package repacks the official upstream .deb without
rebuilding or modifying the application binaries.

%prep
echo "Source0 tracks Tencent's official QQ Music .deb via the signed redirect CGI."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
ar x %{SOURCE0} data.tar.xz
tar xJf data.tar.xz
rm -f data.tar.xz
chmod 0755 %{buildroot}/opt/qqmusic/qqmusic 2>/dev/null || :
# Upstream froze on Electron 11 (Chromium 80, 2021). Its seccomp sandbox
# policy predates glibc's clone3(): on modern kernels the browser process
# is killed by SIGSYS immediately at startup (verified via coredumpctl).
# The sandbox cannot be repaired in-place; --no-sandbox is the standard
# workaround for this frozen build (same as the AUR package).
sed -i 's|^Exec=/opt/qqmusic/qqmusic|Exec=/opt/qqmusic/qqmusic --no-sandbox|' \
    %{buildroot}%{_datadir}/applications/qqmusic.desktop
find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' \
    | awk '{ if ($0 ~ /[[:space:]]/) printf("\"%s\"\n", $0); else print }' \
    | sort > %{_builddir}/%{name}-filelist

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
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 1.1.8-6
- Launch with --no-sandbox: the bundled Chromium 80 seccomp policy predates
  glibc clone3() and kills the process with SIGSYS on current kernels
  (fixes instant crash on launch; coredump-verified root cause)

* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 1.1.8-4
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 1.1.8-3
- Filter the bundled libffmpeg soname from automatic runtime requirements

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.1.8-1
- Initial package: repack the official QQ Music .deb for COPR
