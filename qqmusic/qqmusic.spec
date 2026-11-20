%global debug_package %{nil}
%global __os_install_post %{nil}
# QQ Music does not publish RPMs; this package repacks the official
# x86_64 .deb. Tencent signs download URLs, so Source0 points at the
# official download page's file_redirect.fcg CGI, which generates a
# fresh signed URL on every request
# (https://y.qq.com/download/download.html). scripts/check-updates.py
# rewrites both Version and Source0 automatically.
Name:           qqmusic
Version:        1.1.8
Release:        1%{?dist}
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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.1.8-1
- Initial package: repack the official QQ Music .deb for COPR
