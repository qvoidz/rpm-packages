%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# The bundle ships helper binaries and bundled copies of common system
# libraries; filter all auto-generated requirements so only the explicit
# host dependency list below applies.
%global __requires_exclude ^.*$
# Suppress auto-generated provides of bundled libraries so dnf never pulls
# this package to satisfy unrelated soname requires. The package's own name
# provides are intrinsic and unaffected.
%global __provides_exclude ^.*$
# ZCode is Z.ai's official open-source AI coding workbench (github.com/
# zai-org/ZCode). Linux installers are not published on GitHub Releases
# (macOS/Windows only there); the Linux RPM is hosted on the release CDN
# listed in the update manifest served at
# https://zcode.z.ai/api/v1/releases/electron/manifest?platform=linux-x64&channel=stable
# The URL embeds the version and changes with every release, so
# scripts/check-updates.py rewrites both Version and Source0 automatically.
Name:           zcode
Version:        3.18.2
Release:        1%{?dist}
Summary:        ZCode AI coding workbench desktop client from Z.ai
License:        Apache-2.0
URL:            https://zcode.z.ai/
Source0:        https://cdn-zcode.z.ai/zcode/electron/releases/3.18.2/linux-x64/ZCode-3.18.2-linux-x64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Keep the upstream binary artifact pinned even though the download URL is
# rolling. Requires mirror the upstream RPM's dependency list (Fedora-native
# package names).
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

# Explicit host dependencies (auto-generated from Fedora 45 repodata; the
# bundled private sonames libffmpeg.so and libvips-cpp.so.8.17.3 are filtered)
Requires:       ld-linux-x86-64.so.2()(64bit)
Requires:       libX11.so.6()(64bit)
Requires:       libXcomposite.so.1()(64bit)
Requires:       libXdamage.so.1()(64bit)
Requires:       libXext.so.6()(64bit)
Requires:       libXfixes.so.3()(64bit)
Requires:       libXrandr.so.2()(64bit)
Requires:       libasound.so.2()(64bit)
Requires:       libatk-1.0.so.0()(64bit)
Requires:       libatk-bridge-2.0.so.0()(64bit)
Requires:       libatspi.so.0()(64bit)
Requires:       libcairo.so.2()(64bit)
Requires:       libc.so.6()(64bit)
Requires:       libcups.so.2()(64bit)
Requires:       libdbus-1.so.3()(64bit)
Requires:       libdl.so.2()(64bit)
Requires:       libexpat.so.1()(64bit)
Requires:       libgbm.so.1()(64bit)
Requires:       libgcc_s.so.1()(64bit)
Requires:       libgio-2.0.so.0()(64bit)
Requires:       libglib-2.0.so.0()(64bit)
Requires:       libgobject-2.0.so.0()(64bit)
Requires:       libgtk-3.so.0()(64bit)
Requires:       libm.so.6()(64bit)
Requires:       libnspr4.so()(64bit)
Requires:       libnss3.so()(64bit)
Requires:       libnssutil3.so()(64bit)
Requires:       libpango-1.0.so.0()(64bit)
Requires:       libpthread.so.0()(64bit)
Requires:       libresolv.so.2()(64bit)
Requires:       librt.so.1()(64bit)
Requires:       libsmime3.so()(64bit)
Requires:       libstdc++.so.6()(64bit)
Requires:       libudev.so.1()(64bit)
Requires:       libutil.so.1()(64bit)
Requires:       libxcb.so.1()(64bit)
Requires:       libxkbcommon.so.0()(64bit)
Requires:       rtld(GNU_HASH)


%description
ZCode is Z.ai's official open-source AI coding workbench combining desktop,
browser, and terminal interfaces around a shared agent runtime (built for
the GLM model family). This package repackages the official upstream Linux
RPM without rebuilding or modifying the application binaries.

The desktop client's built-in updater manages its own upgrades; upgrade this
package from the repository instead.

%prep
echo "Source0 tracks Z.ai's official Linux RPM from the release manifest API."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
# Own the app-private directory tree explicitly (%dir): %files with files
# only leaves an 861-directory empty skeleton behind after uninstall.
find opt/ZCode -type d -printf '%%%%dir /%p\n' > %{_builddir}/%{name}-filelist
find . -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' >> %{_builddir}/%{name}-filelist
sort -o %{_builddir}/%{name}-filelist %{_builddir}/%{name}-filelist

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
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 3.18.2-1
- Repackage the official Z.ai ZCode Linux RPM (from the release manifest
  CDN channel) for COPR
