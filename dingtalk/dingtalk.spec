%global debug_package %{nil}
%global __os_install_post %{nil}

# Bundled libraries with no Fedora provider (shipped in the payload):
# These legacy/private sonames are shipped inside the upstream .deb. Keep
# Fedora-provided host dependencies (GTK, X11, audio, etc.) auto-generated.
%global __requires_exclude ^.*$
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
Release:        8%{?dist}
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

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: gtk2
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: libEGL.so.1()(64bit)
Requires: libFcitx5Qt5DBusAddons.so.1()(64bit)
Requires: libGL.so.1()(64bit)
Requires: libGLU.so.1()(64bit)
Requires: libGLX.so.0()(64bit)
Requires: libGLdispatch.so.0()(64bit)
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
Requires: libQt5Multimedia.so.5()(64bit)
Requires: libQt5MultimediaWidgets.so.5()(64bit)
Requires: libQt5Network.so.5()(64bit)
Requires: libQt5OpenGL.so.5()(64bit)
Requires: libQt5PrintSupport.so.5()(64bit)
Requires: libQt5RemoteObjects.so.5()(64bit)
Requires: libQt5Sql.so.5()(64bit)
Requires: libQt5Svg.so.5()(64bit)
Requires: libQt5Test.so.5()(64bit)
Requires: libQt5Widgets.so.5()(64bit)
Requires: libQt5X11Extras.so.5()(64bit)
Requires: libQt5XcbQpa.so.5()(64bit)
Requires: libQt5Xml.so.5()(64bit)
Requires: libSM.so.6()(64bit)
Requires: libX11-xcb.so.1()(64bit)
Requires: libX11.so.6()(64bit)
Requires: libXau.so.6()(64bit)
Requires: libXcomposite.so.1()(64bit)
Requires: libXcursor.so.1()(64bit)
Requires: libXdamage.so.1()(64bit)
Requires: libXdmcp.so.6()(64bit)
Requires: libXext.so.6()(64bit)
Requires: libXfixes.so.3()(64bit)
Requires: libXi.so.6()(64bit)
Requires: libXinerama.so.1()(64bit)
Requires: libXmu.so.6()(64bit)
Requires: libXrandr.so.2()(64bit)
Requires: libXrender.so.1()(64bit)
Requires: libXt.so.6()(64bit)
Requires: libXtst.so.6()(64bit)
Requires: libapr-1.so.0()(64bit)
Requires: libaprutil-1.so.0()(64bit)
Requires: libasound.so.2()(64bit)
Requires: libatk-1.0.so.0()(64bit)
Requires: libatk-bridge-2.0.so.0()(64bit)
Requires: libatspi.so.0()(64bit)
Requires: libc.so.6()(64bit)
Requires: libcairo-gobject.so.2()(64bit)
Requires: libcairo.so.2()(64bit)
Requires: libcef.so()(64bit)
Requires: libcom_err.so.2()(64bit)
Requires: libcrypt.so.1()(64bit)
Requires: libcups.so.2()(64bit)
Requires: libcurl.so.4()(64bit)
Requires: libdbus-1.so.3()(64bit)
Requires: libdl.so.2()(64bit)
Requires: libdrm.so.2()(64bit)
Requires: libepoxy.so.0()(64bit)
Requires: libexpat.so.1()(64bit)
Requires: libfontconfig.so.1()(64bit)
Requires: libfreetype.so.6()(64bit)
Requires: libfribidi.so.0()(64bit)
Requires: libgbm.so.1()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libgcrypt.so.20()(64bit)
Requires: libgdk-3.so.0()(64bit)
Requires: libgdk-x11-2.0.so.0()(64bit)
Requires: libgdk_pixbuf-2.0.so.0()(64bit)
Requires: libgdkglext-x11-1.0.so.0()(64bit)
Requires: libgio-2.0.so.0()(64bit)
Requires: libglib-2.0.so.0()(64bit)
Requires: libgmodule-2.0.so.0()(64bit)
Requires: libgnutls.so.30()(64bit)
Requires: libgobject-2.0.so.0()(64bit)
Requires: libgraphite2.so.3()(64bit)
Requires: libgssapi_krb5.so.2()(64bit)
Requires: libgthread-2.0.so.0()(64bit)
Requires: libgtk-3.so.0()(64bit)
Requires: libgtk-x11-2.0.so.0()(64bit)
Requires: libgtkglext-x11-1.0.so.0()(64bit)
Requires: libharfbuzz.so.0()(64bit)
Requires: libidn2.so.0()(64bit)
Requires: libinput.so.10()(64bit)
Requires: libk5crypto.so.3()(64bit)
Requires: libkrb5.so.3()(64bit)
Requires: liblber-2.4.so.2()(64bit)
Requires: libm.so.6()(64bit)
Requires: libmtdev.so.1()(64bit)
Requires: libmvec.so.1()(64bit)
Requires: libnghttp2.so.14()(64bit)
Requires: libnspr4.so()(64bit)
Requires: libnss3.so()(64bit)
Requires: libnssutil3.so()(64bit)
Requires: libopus.so.0()(64bit)
Requires: libpango-1.0.so.0()(64bit)
Requires: libpangocairo-1.0.so.0()(64bit)
Requires: libpangoft2-1.0.so.0()(64bit)
Requires: libpng16.so.16()(64bit)
Requires: libpsl.so.5()(64bit)
Requires: libpthread.so.0()(64bit)
Requires: libpulse-mainloop-glib.so.0()(64bit)
Requires: libpulse.so.0()(64bit)
Requires: librt.so.1()(64bit)
Requires: librtmp.so.1()(64bit)
Requires: libsession.so()(64bit)
Requires: libsmime3.so()(64bit)
Requires: libssh2.so.1()(64bit)
Requires: libstdc++.so.6()(64bit)
Requires: libudev.so.1()(64bit)
Requires: libunistring.so.2()(64bit)
Requires: libuuid.so.1()(64bit)
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
Requires: libxcb-xfixes.so.0()(64bit)
Requires: libxcb-xinerama.so.0()(64bit)
Requires: libxcb-xinput.so.0()(64bit)
Requires: libxcb-xkb.so.1()(64bit)
Requires: libxcb.so.1()(64bit)
Requires: libxcrypt-compat
Requires: libxkbcommon-x11.so.0()(64bit)
Requires: libxkbcommon.so.0()(64bit)
Requires: libz.so.1()(64bit)
Requires: mesa-libGLU
Requires: rtld(GNU_HASH)


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
{
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | awk '{ if ($0 ~ /[[:space:]]/) print "%%dir \"" $0 "\""; else print "%%dir " $0 }'
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' \
    | awk '{ if ($0 ~ /[[:space:]]/) printf("\"%s\"\n", $0); else print }'
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
* Sun Nov 23 2026 COPR Builder <copr@example.invalid> - 8.3.1.261008001-8
- Inject ELECTRON_OZONE_PLATFORM_HINT=x11 into desktop Exec lines:
  Electron under Wayland (niri) loses fcitx5 IME input
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 8.3.1.261008001-7
- Own every payload directory in the file list (except /usr/lib and /usr/lib64, which filesystem ships read-only 0555) so uninstall leaves no orphaned empty directories behind
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 8.3.1.261008001-5
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 8.3.1.261008001-4
- Filter exact legacy and private sonames bundled in the upstream payload

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated requires of bundled libs
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 8.3.1.261008001-1
- Initial package: repack the official DingTalk .deb for COPR
