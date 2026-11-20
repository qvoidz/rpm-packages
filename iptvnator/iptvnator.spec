%global debug_package %{nil}
# Electron app: disable RPM build-side processing (brp-strip /
# brp-compress / check-rpaths) so the upstream binaries are repacked
# byte-for-byte (their "${ORIGIN}" runpaths would be rejected otherwise).
%global __os_install_post %{nil}
# The upstream RPM bundles a few helper libraries built for other
# architectures (aarch64) and with musl; rpm's dependency generator picks
# up their sonames (ld-linux-aarch64.so.1, libc.musl-*, libm.so.6
# GLIBC_2.17) as requirements, but no Fedora package provides them and the
# helpers are never loaded on the host, so filter them out.
%global __requires_exclude ^(ld-linux-aarch64|libc\\.musl|libm\\.so\\.6\\(GLIBC_2\\.17)

Name:           iptvnator
Version:        0.25.0
Release:        1%{?dist}
Summary:        Cross-platform IPTV (m3u playlist) player
License:        MIT
URL:            https://github.com/4gray/iptvnator
Source0:        https://github.com/4gray/iptvnator/releases/download/v%{version}/iptvnator-%{version}-linux-x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  rpm

%description
IPTV (m3u playlist) player by 4gray: watch TV via playlists, with EPG
support, favorites and multi-window layouts. This package repackages the
official upstream RPM without rebuilding or modifying the application
binaries.

%prep
echo "Source0 is the official upstream RPM published on GitHub releases."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.25.0-1
- Repackage the official upstream RPM for COPR
