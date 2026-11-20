%global debug_package %{nil}
%global __os_install_post %{nil}

# Bundled libraries with no Fedora provider (shipped in the payload):
# These legacy/private sonames are shipped inside the upstream .deb. Keep
# Fedora-provided host dependencies (GTK, X11, audio, etc.) auto-generated.
%global __requires_exclude ^(liblber|libldap|libpangox|libahencrypt_sdk|libaliumidsdk|libavcodec\.so\.61|libavformat\.so\.61|libavutil\.so\.59|libcalendar_sdk|libcef|libcrypto\.so\.1\.1|libdt_resource_loader|libdtfbase|libdtnest(_module)?|libexiv2\.so\.14|libffmpeg|libgaea|libhttp_server|libicudata\.so\.63|libicui18n\.so\.63|libicuuc\.so\.63|libmeeting_sdk|libprgbase|libsession|libsodium\.so\.23|libssl\.so\.1\.1|libswresample\.so\.5|libswscale\.so\.8|libsync|libutforpc|libxcb-util\.so\.0)
# The payload also bundles its own copies of common system libraries
# (libm, libGLX, libstdc++, ...). rpm's automatic generator turns them
# into soname Provides, shadowing the real Fedora providers: dnf may pull
# this multi-GB package just to satisfy e.g. libGLX.so.0 (observed when
# installing fcitx5-wetypex). Suppress all auto-generated provides; the
# package's own name provides are intrinsic and unaffected.
%global __provides_exclude ^.*$
# DingTalk does not publish RPMs; this package repacks the official
# x86_64 .deb. The Release directory has no version-independent URL and
# the update JSON lags behind actual releases, so scripts/check-updates.py
# derives the latest version from the update JSON's description
# ("版本：X-Release.Y" -> com.alibabainc.dingtalk_X.Y_amd64.deb) and
# verifies the constructed URL before rewriting Version and Source0.
Name:           dingtalk
Version:        8.3.1.261008001
Release:        4%{?dist}
Summary:        DingTalk (钉钉) desktop client for Linux
License:        LicenseRef-Alibaba-DingTalk-Software-License
URL:            https://www.dingtalk.com/
Source0:        https://dtapp-pub.dingtalk.com/dingtalk-desktop/xc_dingtalk_update/linux_deb/Release/com.alibabainc.dingtalk_8.3.1.261008001_amd64.deb

ExclusiveArch:  x86_64
BuildRequires:  binutils
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  xz

Requires:       gtk2
Requires:       libxcrypt-compat
Requires:       mesa-libGLU

%description
DingTalk (钉钉) desktop client for Linux, distributed by Alibaba. This
package repacks the official upstream .deb without rebuilding or
modifying the application binaries.

%prep
echo "Source0 tracks DingTalk's official Release .deb."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
ar x %{SOURCE0} data.tar.xz
tar xJf data.tar.xz
rm -f data.tar.xz
chmod 0755 %{buildroot}/opt/dingtalk/com.alibabainc.dingtalk 2>/dev/null || :
chmod 0755 %{buildroot}/opt/dingtalk/dingtalk 2>/dev/null || :
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
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 8.3.1.261008001-4
- Filter exact legacy and private sonames bundled in the upstream payload

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated requires of bundled libs
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 8.3.1.261008001-1
- Initial package: repack the official DingTalk .deb for COPR
