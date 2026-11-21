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
%global __requires_exclude ^.*$
# Tencent Meeting does not publish RPMs; this package repacks the official
# x86_64 .deb from the official download API
# https://meeting.tencent.com/web-service/query-download-info
# (the URL embeds the release md5 and changes with every release, so
# scripts/check-updates.py rewrites both Version and Source0 automatically).
Name:           wemeet
Version:        3.26.10.401
Release:        6%{?dist}
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

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: dbus-libs
Requires: desktop-file-utils
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: libEGL.so.1()(64bit)
Requires: libGL.so.1()(64bit)
Requires: libICE.so.6()(64bit)
Requires: libQt5Concurrent.so.5()(64bit)
Requires: libQt5Core.so.5()(64bit)
Requires: libQt5DBus.so.5()(64bit)
Requires: libQt5Designer.so.5()(64bit)
Requires: libQt5DesignerComponents.so.5()(64bit)
Requires: libQt5EglFSDeviceIntegration.so.5()(64bit)
Requires: libQt5EglFsKmsSupport.so.5()(64bit)
Requires: libQt5Gui.so.5()(64bit)
Requires: libQt5Help.so.5()(64bit)
Requires: libQt5Location.so.5()(64bit)
Requires: libQt5Network.so.5()(64bit)
Requires: libQt5NetworkAuth.so.5()(64bit)
Requires: libQt5OpenGL.so.5()(64bit)
Requires: libQt5Pdf.so.5()(64bit)
Requires: libQt5PdfWidgets.so.5()(64bit)
Requires: libQt5Positioning.so.5()(64bit)
Requires: libQt5PositioningQuick.so.5()(64bit)
Requires: libQt5PrintSupport.so.5()(64bit)
Requires: libQt5Qml.so.5()(64bit)
Requires: libQt5QmlModels.so.5()(64bit)
Requires: libQt5QmlWorkerScript.so.5()(64bit)
Requires: libQt5Quick.so.5()(64bit)
Requires: libQt5QuickControls2.so.5()(64bit)
Requires: libQt5QuickParticles.so.5()(64bit)
Requires: libQt5QuickShapes.so.5()(64bit)
Requires: libQt5QuickTemplates2.so.5()(64bit)
Requires: libQt5QuickTest.so.5()(64bit)
Requires: libQt5QuickWidgets.so.5()(64bit)
Requires: libQt5RemoteObjects.so.5()(64bit)
Requires: libQt5Script.so.5()(64bit)
Requires: libQt5ScriptTools.so.5()(64bit)
Requires: libQt5Scxml.so.5()(64bit)
Requires: libQt5Sql.so.5()(64bit)
Requires: libQt5Svg.so.5()(64bit)
Requires: libQt5Test.so.5()(64bit)
Requires: libQt5TextToSpeech.so.5()(64bit)
Requires: libQt5WaylandClient.so.5()(64bit)
Requires: libQt5WaylandCompositor.so.5()(64bit)
Requires: libQt5WebChannel.so.5()(64bit)
Requires: libQt5WebEngine.so.5()(64bit)
Requires: libQt5WebEngineCore.so.5()(64bit)
Requires: libQt5WebEngineWidgets.so.5()(64bit)
Requires: libQt5WebSockets.so.5()(64bit)
Requires: libQt5WebView.so.5()(64bit)
Requires: libQt5Widgets.so.5()(64bit)
Requires: libQt5X11Extras.so.5()(64bit)
Requires: libQt5XcbQpa.so.5()(64bit)
Requires: libQt5Xml.so.5()(64bit)
Requires: libQt5XmlPatterns.so.5()(64bit)
Requires: libSM.so.6()(64bit)
Requires: libX11
Requires: libX11-xcb.so.1()(64bit)
Requires: libX11.so.6()(64bit)
Requires: libXau.so.6()(64bit)
Requires: libXcomposite.so.1()(64bit)
Requires: libXdamage.so.1()(64bit)
Requires: libXdmcp.so.6()(64bit)
Requires: libXext.so.6()(64bit)
Requires: libXfixes.so.3()(64bit)
Requires: libXinerama.so.1()(64bit)
Requires: libXrandr.so.2()(64bit)
Requires: libXrender.so.1()(64bit)
Requires: libXtst.so.6()(64bit)
Requires: libasound.so.2()(64bit)
Requires: libbsd.so.0()(64bit)
Requires: libc.so.6()(64bit)
Requires: libdbus-1.so.3()(64bit)
Requires: libdl.so.2()(64bit)
Requires: libdrm.so.2()(64bit)
Requires: libexpat.so.1()(64bit)
Requires: libfontconfig.so.1()(64bit)
Requires: libfreetype.so.6()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libgcrypt
Requires: libglib-2.0.so.0()(64bit)
Requires: libgthread-2.0.so.0()(64bit)
Requires: libharfbuzz.so.0()(64bit)
Requires: libm.so.6()(64bit)
Requires: libnsl.so.1()(64bit)
Requires: libnspr4.so()(64bit)
Requires: libnss3.so()(64bit)
Requires: libnssutil3.so()(64bit)
Requires: libogg.so.0()(64bit)
Requires: libplc4.so()(64bit)
Requires: libplds4.so()(64bit)
Requires: libpthread.so.0()(64bit)
Requires: libpulse.so.0()(64bit)
Requires: libresolv.so.2()(64bit)
Requires: librt.so.1()(64bit)
Requires: libsmime3.so()(64bit)
Requires: libstdc++.so.6()(64bit)
Requires: libudev.so.1()(64bit)
Requires: libvorbis.so.0()(64bit)
Requires: libvorbisenc.so.2()(64bit)
Requires: libwayland-client.so.0()(64bit)
Requires: libwayland-cursor.so.0()(64bit)
Requires: libwayland-egl.so.1()(64bit)
Requires: libwayland-server.so.0()(64bit)
Requires: libxcb-glx.so.0()(64bit)
Requires: libxcb-icccm.so.4()(64bit)
Requires: libxcb-image.so.0()(64bit)
Requires: libxcb-keysyms.so.1()(64bit)
Requires: libxcb-randr.so.0()(64bit)
Requires: libxcb-render-util.so.0()(64bit)
Requires: libxcb-render.so.0()(64bit)
Requires: libxcb-shape.so.0()(64bit)
Requires: libxcb-shm.so.0()(64bit)
Requires: libxcb-sync.so.1()(64bit)
Requires: libxcb-util.so.1()(64bit)
Requires: libxcb-xfixes.so.0()(64bit)
Requires: libxcb-xinerama.so.0()(64bit)
Requires: libxcb-xkb.so.1()(64bit)
Requires: libxcb.so.1()(64bit)
Requires: libxkbcommon-x11.so.0()(64bit)
Requires: libxkbcommon.so.0()(64bit)
Requires: libz.so.1()(64bit)
Requires: nss
Requires: pulseaudio-libs
Requires: rtld(GNU_HASH)
Requires: systemd-udev


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
{
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | awk '{ if ($0 ~ /[[:space:]]/) print "%%dir \"" $0 "\""; else print "%%dir " $0 }'
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n'
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
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 3.26.10.401-6
- Own every payload directory in the file list (except /usr/lib and /usr/lib64, which filesystem ships read-only 0555) so uninstall leaves no orphaned empty directories behind
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 3.26.10.401-4
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 3.26.10.401-3
- Filter application-private sonames bundled in the upstream .deb

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.26.10.401-1
- Initial package: repack the official Tencent Meeting .deb for COPR
