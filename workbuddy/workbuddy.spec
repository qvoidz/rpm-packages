%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# The app bundle ships helper binaries for other architectures and OSes
# (aarch64 / armhf / loongarch / riscv64, musl, FreeBSD). rpm's dependency
# generator scans them too and emits soname requirements (e.g.
# ld-linux-aarch64.so.1, libc.musl-*, libc.so.7) that no Fedora package
# provides; the helpers only ever run inside the app's own sandbox, so
# filter those false requirements out.
%global __requires_exclude ^.*$
# The payload also bundles x86-64 copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires (observed when installing fcitx5-wetypex). Suppress all
# auto-generated provides; the package's own name provides are intrinsic
# and unaffected.
%global __provides_exclude ^.*$
# Source0 is Tencent's official WorkBuddy Linux RPM, discovered through the
# update API https://copilot.tencent.com/v2/update?platform=workbuddy-linux-x64-rpm
# The URL embeds a build hash and changes with every release, so
# scripts/check-updates.py rewrites both Version and Source0 automatically.
Name:           workbuddy
Version:        5.6.2.40046327
Release:        7%{?dist}
Summary:        WorkBuddy AI coding assistant desktop client from Tencent
License:        LicenseRef-Tencent-WorkBuddy-Software-License
URL:            https://www.workbuddy.cn/
Source0:        https://download.codebuddy.cn/workbuddy/saas/linux-x64-rpm/WorkBuddy-linux-x64-rpm-5.6.2.40046327-c7b525f3.rpm

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

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: (libXtst or libXtst6)
Requires: (libuuid or libuuid1)
Requires: alsa-lib
Requires: at-spi2-core
Requires: gtk3
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: ld-linux.so.2
Requires: ld-linux.so.2(GLIBC_2.3)
Requires: libGL.so.1()(64bit)
Requires: libX11.so.6()(64bit)
Requires: libXScrnSaver
Requires: libXcomposite.so.1()(64bit)
Requires: libXdamage.so.1()(64bit)
Requires: libXext.so.6()(64bit)
Requires: libXfixes.so.3()(64bit)
Requires: libXrandr.so.2()(64bit)
Requires: libasound.so.2()(64bit)
Requires: libatk-1.0.so.0()(64bit)
Requires: libatk-bridge-2.0.so.0()(64bit)
Requires: libatspi.so.0()(64bit)
Requires: libc++.so.1()(64bit)
Requires: libc.so.6()(64bit)
Requires: libcairo.so.2()(64bit)
Requires: libcups.so.2()(64bit)
Requires: libdbus-1.so.3()(64bit)
Requires: libdl.so.2()(64bit)
Requires: libexpat.so.1()(64bit)
Requires: libgbm.so.1()(64bit)
Requires: libgcc_s.so.1()(64bit)
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
Requires: libpthread.so.0()(64bit)
Requires: libpython3.13.so.1.0()(64bit)
Requires: librt.so.1()(64bit)
Requires: libsmime3.so()(64bit)
Requires: libstdc++.so.6()(64bit)
Requires: libtcl9.0.so()(64bit)
Requires: libtcl9tk9.0.so()(64bit)
Requires: libudev.so.1()(64bit)
Requires: libutil.so.1()(64bit)
Requires: libxcb.so.1()(64bit)
Requires: libxkbcommon.so.0()(64bit)
Requires: mesa-libgbm
Requires: nss
Requires: rtld(GNU_HASH)
Requires: xdg-utils


%description
WorkBuddy AI coding assistant desktop client for Linux, distributed by
Tencent. This package repackages the official upstream RPM without rebuilding
or modifying the application binaries.

The application's built-in updater points back to the official website, which
lists no Linux download; upgrade this package from the repository instead.

%prep
echo "Source0 tracks Tencent's official Linux RPM from the update API."

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
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n'
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
* Sun Nov 23 2026 COPR Builder <copr@example.invalid> - 5.6.2.40046327-7
- Inject ELECTRON_OZONE_PLATFORM_HINT=x11 into desktop Exec lines:
  Electron under Wayland (niri) loses fcitx5 IME input
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 5.6.2.40046327-6
- Own every payload directory in the file list (except /usr/lib and /usr/lib64, which filesystem ships read-only 0555) so uninstall leaves no orphaned empty directories behind
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 5.6.2.40046327-4
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 5.6.2.40046327-3
- Filter the bundled libffmpeg soname from automatic runtime requirements

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 5.6.2.40046327-1
- Repackage the official Tencent WorkBuddy Linux RPM (from the update API channel) for COPR
