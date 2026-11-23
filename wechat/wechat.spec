%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# The payload bundles its own copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires (observed when installing fcitx5-wetypex). Suppress all
# auto-generated provides; the package's own name provides are intrinsic
# and unaffected.
%global __provides_exclude ^.*$
# Tencent ships these application-private libraries in the RPM payload.
%global __requires_exclude ^.*$
Name:           wechat
Version:        4.1.13.29
Release:        6%{?dist}

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: libEGL.so.1()(64bit)
Requires: libGL.so.1()(64bit)
Requires: libICE.so.6()(64bit)
Requires: libSM.so.6()(64bit)
Requires: libX11-xcb.so.1()(64bit)
Requires: libX11.so.6()(64bit)
Requires: libXcomposite.so.1()(64bit)
Requires: libXdamage.so.1()(64bit)
Requires: libXext.so.6()(64bit)
Requires: libXfixes.so.3()(64bit)
Requires: libXrandr.so.2()(64bit)
Requires: libasound.so.2()(64bit)
Requires: libatk-1.0.so.0()(64bit)
Requires: libatk-bridge-2.0.so.0()(64bit)
Requires: libatomic.so.1()(64bit)
Requires: libatspi.so.0()(64bit)
Requires: libc.so.6()(64bit)
Requires: libcairo.so.2()(64bit)
Requires: libcups.so.2()(64bit)
Requires: libdbus-1.so.3()(64bit)
Requires: libdl.so.2()(64bit)
Requires: libexpat.so.1()(64bit)
Requires: libfontconfig.so.1()(64bit)
Requires: libgbm.so.1()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libgio-2.0.so.0()(64bit)
Requires: libglib-2.0.so.0()(64bit)
Requires: libgobject-2.0.so.0()(64bit)
Requires: libjack.so.0()(64bit)
Requires: libm.so.6()(64bit)
Requires: libnspr4.so()(64bit)
Requires: libnss3.so()(64bit)
Requires: libnssutil3.so()(64bit)
Requires: libpango-1.0.so.0()(64bit)
Requires: libpthread.so.0()(64bit)
Requires: libpulse.so.0()(64bit)
Requires: librt.so.1()(64bit)
Requires: libstdc++.so.6()(64bit)
Requires: libudev.so.1()(64bit)
Requires: libvlc.so.5()(64bit)
Requires: libvlc_pulse.so.0()(64bit)
Requires: libvlccore.so.9()(64bit)
Requires: libxcb-keysyms.so.1()(64bit)
Requires: libxcb-shm.so.0()(64bit)
Requires: libxcb-xfixes.so.0()(64bit)
Requires: libxcb.so.1()(64bit)
Requires: libxkbcommon.so.0()(64bit)
Requires: libz.so.1()(64bit)
Requires: rtld(GNU_HASH)

Summary:        WeChat desktop client from Tencent
License:        LicenseRef-Tencent-Weixin-Software-and-Service-License
URL:            https://weixin.qq.com/
Source0:        https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Source0 is Tencent's version-independent download URL: its payload changes
# with every WeChat release, so the bytes are not hash-pinned here.
# scripts/check-updates.py sniffs the newest version directly from the RPM
# header (HTTP Range request) and bumps Version automatically.
%description
WeChat desktop client for Linux, distributed by Tencent.
This package repackages the official upstream RPM without rebuilding
or modifying the application binaries.

%prep
echo "Source0 tracks Tencent's rolling download; no hash pin applied."

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
* Sun Nov 23 2026 COPR Builder <copr@example.invalid> - 4.1.13.29-6
- Inject ELECTRON_OZONE_PLATFORM_HINT=x11 into desktop Exec lines:
  Electron under Wayland (niri) loses fcitx5 IME input
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 4.1.13.29-5
- Own every payload directory in the file list (except /usr/lib and /usr/lib64, which filesystem ships read-only 0555) so uninstall leaves no orphaned empty directories behind
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 4.1.13.29-3
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 4.1.13.29-2
- Filter application-private sonames bundled in the upstream RPM

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 4.1.13.29-1
- Update to upstream WeChat 4.1.13.29
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 4.1.13.26-2
- Drop the pinned SHA-256 so the rolling Tencent download can be tracked
- Repackage the official Tencent WeChat RPM for COPR
