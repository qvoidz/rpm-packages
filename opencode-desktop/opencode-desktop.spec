%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# The Electron payload bundles helper binaries for other architectures and
# bundled private libraries (libEGL, libGLESv2, ...). Suppress all
# auto-generated provides/requires and declare the host dependency set
# explicitly below; bundled private sonames resolve via ${ORIGIN} runpath.
%global __provides_exclude ^.*$
%global __requires_exclude ^.*$
# Source0 is the official opencode desktop Electron RPM from the same
# GitHub release as the opencode CLI (tag v<version>); the upstream RPM's
# own package name is "opencode", which collides with the CLI package, so
# this spec repacks it under the name opencode-desktop.
Name:           opencode-desktop
Version:        1.19.6
Release:        1%{?dist}
Summary:        opencode desktop client (Electron) for Linux
License:        MIT
URL:            https://opencode.ai/
Source0:        https://github.com/sst/opencode/releases/download/v1.19.6/opencode-desktop-linux-x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Explicit host dependencies (Electron runtime; mirrors the upstream RPM's
# dependency list mapped to Fedora-native packages).
Requires:       (libXtst or libXtst6)
Requires:       (libuuid or libuuid1)
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       mesa-libgbm
Requires:       nss
Requires:       xdg-utils

%description
opencode desktop client: the Electron GUI companion to the opencode AI
coding agent, distributed by SST. This package repackages the official
upstream Linux x86_64 RPM without rebuilding or modifying the application
binaries.

%prep
echo "Source0 tracks the official opencode desktop RPM from GitHub releases."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
{
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | awk '{ if ($0 ~ /[[:space:]]/) print "%%dir \"" $0 "\""; else print "%%dir " $0 }'
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' |
    awk '{ if ($0 ~ /[[:space:]]/) print "\"" $0 "\""; else print $0 }'
} | sort > %{_builddir}/%{name}-filelist

# Electron apps under Wayland compositors (niri) can lose fcitx5 IME input;
# pin the X11 ozone platform for every desktop entry this payload ships.
for f in %{buildroot}%{_datadir}/applications/*.desktop; do
    [ -f "$f" ] || continue
    sed -i -e 's|^Exec=\(.*\)|Exec=env ELECTRON_OZONE_PLATFORM_HINT=x11 \1|' "$f" || :
done

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
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 1.19.6-1
- Initial package: repack the official opencode desktop Electron RPM
  (renamed opencode-desktop to coexist with the opencode CLI package)
