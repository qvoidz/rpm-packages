%global debug_package %{nil}
%global __os_install_post %{nil}

# Bundled libraries with no Fedora provider (shipped in the payload):
%global __requires_exclude ^.*$
# The payload also bundles its own copies of common system libraries
# (libstdc++, libgcc_s, libc++abi, ...). rpm's automatic generator turns
# them into soname Provides, shadowing the real Fedora providers: dnf may
# pull this multi-GB package just to satisfy e.g. libstdc++.so.6 (observed
# when installing fcitx5-wetypex). Suppress all auto-generated provides;
# the package's own name provides are intrinsic and unaffected.
%global __provides_exclude ^.*$
# WPS Office publishes a version-independent rolling RPM
# (https://wdl1.pcfg.cache.wpscdn.com/wpsdl/wpsoffice/download/linux/
# wps-office.rpm, always the latest release). Source0 never changes;
# scripts/check-updates.py sniffs the RPM header (HTTP Range, ~4 MB)
# for the upstream version and rewrites Version when it advances.
Name:           wps-office
Version:        12.1.2.29182.AK.preread.sw
Release:        7%{?dist}
Summary:        WPS Office - Kingsoft office suite for Linux
License:        LicenseRef-Kingsoft-WPS-Office-License
URL:            https://linux.wps.cn/
Source0:        https://wdl1.pcfg.cache.wpscdn.com/wpsdl/wpsoffice/download/linux/wps-office.rpm

ExclusiveArch:  x86_64
BuildRequires:  coreutils
BuildRequires:  cpio
BuildRequires:  rpm

# Requires mirror the upstream RPM header's dependency list.
Requires:       cups-libs
Requires:       fontconfig
Requires:       glib2
Requires:       libGLU
Requires:       libICE
Requires:       libSM
Requires:       libX11
Requires:       libXext
Requires:       libXrender
Requires:       libxcb
Requires:       python3

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: cups-libs
Requires: fontconfig
Requires: glib2
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: libEGL.so.1()(64bit)
Requires: libGL.so.1()(64bit)
Requires: libGLU
Requires: libICE
Requires: libICE.so.6()(64bit)
Requires: libQt5Core.so.5()(64bit)
Requires: libQt5Gui.so.5()(64bit)
Requires: libQt5Widgets.so.5()(64bit)
Requires: libQtCore.so.4()(64bit)
Requires: libSDL2-2.0.so.0()(64bit)
Requires: libSM
Requires: libSM.so.6()(64bit)
Requires: libX11
Requires: libX11-xcb.so.1()(64bit)
Requires: libX11.so.6()(64bit)
Requires: libXcomposite.so.1()(64bit)
Requires: libXdamage.so.1()(64bit)
Requires: libXext
Requires: libXext.so.6()(64bit)
Requires: libXfixes.so.3()(64bit)
Requires: libXrandr.so.2()(64bit)
Requires: libXrender
Requires: libXrender.so.1()(64bit)
Requires: libXtst.so.6()(64bit)
Requires: libXv.so.1()(64bit)
Requires: libanl.so.1()(64bit)
Requires: libasound.so.2()(64bit)
Requires: libatk-1.0.so.0()(64bit)
Requires: libatk-bridge-2.0.so.0()(64bit)
Requires: libatspi.so.0()(64bit)
Requires: libc++abi.so.1()(64bit)
Requires: libc.so.6()(64bit)
Requires: libcairo-gobject.so.2()(64bit)
Requires: libcairo.so.2()(64bit)
Requires: libcef.so()(64bit)
Requires: libcups.so.2()(64bit)
Requires: libcurl.so.4()(64bit)
Requires: libdbus-1.so.3()(64bit)
Requires: libdl.so.2()(64bit)
Requires: libdrm.so.2()(64bit)
Requires: libexpat.so.1()(64bit)
Requires: libfontconfig.so.1()(64bit)
Requires: libfreetype.so.6()(64bit)
Requires: libgbm.so.1()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libgdk-3.so.0()(64bit)
Requires: libgdk_pixbuf-2.0.so.0()(64bit)
Requires: libgio-2.0.so.0()(64bit)
Requires: libglib-2.0.so.0()(64bit)
Requires: libgobject-2.0.so.0()(64bit)
Requires: libgthread-2.0.so.0()(64bit)
Requires: libgtk-3.so.0()(64bit)
Requires: libltdl.so.7()(64bit)
Requires: liblzma.so.5()(64bit)
Requires: libm.so.6()(64bit)
Requires: libnspr4.so()(64bit)
Requires: libnss3.so()(64bit)
Requires: libnssutil3.so()(64bit)
Requires: libodbc.so.2()(64bit)
Requires: libodbccr.so.2()(64bit)
Requires: libodbcinst.so.2()(64bit)
Requires: libpaho-mqtt3as.so.1()(64bit)
Requires: libpango-1.0.so.0()(64bit)
Requires: libpangocairo-1.0.so.0()(64bit)
Requires: libplc4.so()(64bit)
Requires: libplds4.so()(64bit)
Requires: libpthread.so.0()(64bit)
Requires: libqrencode.so.4()(64bit)
Requires: librt.so.1()(64bit)
Requires: libsmime3.so()(64bit)
Requires: libsqlite3.so.0()(64bit)
Requires: libstdc++.so.6()(64bit)
Requires: libsystemd.so.0()(64bit)
Requires: libtbb.so.12()(64bit)
Requires: libtcmalloc_minimal.so.4()(64bit)
Requires: libusb-1.0.so.0()(64bit)
Requires: libuuid.so.1()(64bit)
Requires: libva-drm.so.2()(64bit)
Requires: libva-x11.so.2()(64bit)
Requires: libva.so.2()(64bit)
Requires: libwayland-client.so.0()(64bit)
Requires: libxcb
Requires: libxcb-glx.so.0()(64bit)
Requires: libxcb-shape.so.0()(64bit)
Requires: libxcb-shm.so.0()(64bit)
Requires: libxcb-xfixes.so.0()(64bit)
Requires: libxcb.so.1()(64bit)
Requires: libxkbcommon-x11.so.0()(64bit)
Requires: libxkbcommon.so.0()(64bit)
Requires: libz.so.1()(64bit)
Requires: python3
Requires: rtld(GNU_HASH)


%description
WPS Office (金山办公) suite for Linux, distributed by Kingsoft. This
package repacks the official upstream RPM without rebuilding or
modifying the application binaries.

%prep
echo "Source0 tracks WPS Office's official rolling RPM."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
# Wrap entries containing spaces in double quotes (supported by rpm >= 4.20
# file lists); WPS ships template documents like "labor contract.dotm".
{
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | awk '{ if ($0 ~ /[[:space:]]/) print "%%dir \"" $0 "\""; else print "%%dir " $0 }'
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' \
    | awk '{ if ($0 ~ /[[:space:]]/) printf("\"%s\"\n", $0); else print }'
} | sort > %{_builddir}/%{name}-filelist

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
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 12.1.2.29182.AK.preread.sw-7
- Own every payload directory in the file list (except /usr/lib and /usr/lib64, which filesystem ships read-only 0555) so uninstall leaves no orphaned empty directories behind
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 12.1.2.29182.AK.preread.sw-5
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 12.1.2.29182.AK.preread.sw-4
- Filter WPS-private sonames bundled in the upstream RPM

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated requires of bundled libs
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 12.1.2.29182.AK.preread.sw-1
- Initial package: repack the official WPS Office RPM for COPR
