%global debug_package %{nil}
# Ship the upstream binaries unmodified: disable RPM build-side processing
# (brp-strip etc.) which could modify or reject the upstream payload.
%global __os_install_post %{nil}
# The payload bundles its own copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires (observed when installing fcitx5-wetypex). Suppress all
# auto-generated provides; the package's own name provides are intrinsic
# and unaffected.
%global __provides_exclude ^.*$
# Tencent Meeting ships these private libraries in its .deb payload.
%global __requires_exclude ^(libwemeet_(framework|migration|module_api|platform|qt|util)|libxcast(_codec)?|libxnn(_core|_media)?|libyuv)\\.so(\\(|$)
# Tencent Meeting does not publish RPMs; this package repacks the official
# x86_64 .deb from the official download API
# https://meeting.tencent.com/web-service/query-download-info
# (the URL embeds the release md5 and changes with every release, so
# scripts/check-updates.py rewrites both Version and Source0 automatically).
Name:           wemeet
Version:        3.26.10.401
Release:        3%{?dist}
Summary:        Tencent Meeting desktop client for Linux
License:        LicenseRef-Tencent-Meeting-Software-License
URL:            https://meeting.tencent.com/
Source0:        https://updatecdn.meeting.qq.com/cos/72e0e0023e1d1e6d4123fba28821aea1/TencentMeeting_0300000000_3.26.10.401_x86_64_default.publish.officialwebsite.deb

ExclusiveArch:  x86_64
BuildRequires:  binutils
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  xz

# Requires mirror the deb's Depends list, mapped to Fedora-native names:
# libnss3, libx11-6, desktop-file-utils, libpulse0, libgcrypt20,
# libdbus-1-3, libsystemd0, libudev1.
Requires:       dbus-libs
Requires:       desktop-file-utils
Requires:       libgcrypt
Requires:       libX11
Requires:       nss
Requires:       pulseaudio-libs
Requires:       systemd-udev

%description
Tencent Meeting (腾讯会议) desktop client for Linux, distributed by Tencent.
This package repacks the official upstream .deb without rebuilding or
modifying the application binaries.

The deb's data archive does not preserve executable bits, so the launcher
binaries are chmod'ed in %install exactly like the deb's postinst does.

%prep
echo "Source0 tracks Tencent's official Meeting .deb from the download API."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
ar x %{SOURCE0} data.tar.xz
tar xJf data.tar.xz
rm -f data.tar.xz
chmod 0755 %{buildroot}/opt/wemeet/wemeetapp.sh 2>/dev/null || :
chmod 0755 %{buildroot}/opt/wemeet/bin/wemeetapp 2>/dev/null || :
find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' | sort > %{_builddir}/%{name}-filelist

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
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 3.26.10.401-3
- Filter application-private sonames bundled in the upstream .deb

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.26.10.401-1
- Initial package: repack the official Tencent Meeting .deb for COPR
