%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which would modify the payload.
%global __os_install_post %{nil}
# The payload bundles its own copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires. Suppress all auto-generated provides; the package's own
# name provides are intrinsic and unaffected.
%global __provides_exclude ^.*$
# The Ubuntu 19.04 payload carries these legacy ABI libraries privately;
# do not turn them into Fedora package dependencies. Keep the explicit
# host compatibility requirements (libxcrypt and libnsl) below.
%global __requires_exclude ^.*$
# Bare asset URL, rewritten automatically by scripts/check-updates.py from
# the official download page (the upstream client has been frozen at 1.2.1
# since 2019). NetEase's CDN (d1.music.126.net) 403s bare requests and, like
# QQ, cannot be fetched by a build machine, so
# .github/workflows/mirror.yml downloads it with Referer on an Actions
# runner and publishes it as a GitHub Release asset; this spec fetches the
# mirrored asset as plain Source0 during the SRPM build (COPR's binary
# chroots are fully offline; only the SRPM stage has network access).
%global netease_deb_url https://d1.music.126.net/dmusic/netease-cloud-music_1.2.1_amd64_ubuntu_20190428.deb

Name:           netease-cloud-music
Version:        1.2.1
Release:        7%{?dist}
Summary:        NetEase Cloud Music (网易云音乐) desktop client for Linux
License:        LicenseRef-NetEase-CloudMusic-Software-License
URL:            https://music.163.com/

%global ncm_mirror https://github.com/qvoidz/rpm-packages/releases/download/netease-cloud-music-%{version}
Source0:        %{ncm_mirror}/%(basename %{netease_deb_url})

ExclusiveArch:  x86_64

# The upstream .deb was built for Ubuntu 19.04 and links these two legacy
# libc interfaces that Fedora ships in separate packages.
Requires:       libxcrypt
Requires:       libnsl

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: libEGL.so.1()(64bit)
Requires: libGL.so.1()(64bit)
Requires: libGLESv2.so.2()(64bit)
Requires: libGLdispatch.so.0()(64bit)
Requires: libICE.so.6()(64bit)
Requires: libQt5Core.so.5()(64bit)
Requires: libQt5DBus.so.5()(64bit)
Requires: libQt5EglFSDeviceIntegration.so.5()(64bit)
Requires: libQt5Gui.so.5()(64bit)
Requires: libQt5Network.so.5()(64bit)
Requires: libQt5Qml.so.5()(64bit)
Requires: libQt5Svg.so.5()(64bit)
Requires: libQt5WebChannel.so.5()(64bit)
Requires: libQt5Widgets.so.5()(64bit)
Requires: libQt5X11Extras.so.5()(64bit)
Requires: libQt5XcbQpa.so.5()(64bit)
Requires: libQt5Xml.so.5()(64bit)
Requires: libSDL-1.2.so.0()(64bit)
Requires: libSDL_image-1.2.so.0()(64bit)
Requires: libSM.so.6()(64bit)
Requires: libUsageEnvironment.so.3()(64bit)
Requires: libX11-xcb.so.1()(64bit)
Requires: libX11.so.6()(64bit)
Requires: libXcomposite.so.1()(64bit)
Requires: libXcursor.so.1()(64bit)
Requires: libXdamage.so.1()(64bit)
Requires: libXext.so.6()(64bit)
Requires: libXfixes.so.3()(64bit)
Requires: libXi.so.6()(64bit)
Requires: libXinerama.so.1()(64bit)
Requires: libXpm.so.4()(64bit)
Requires: libXrandr.so.2()(64bit)
Requires: libXrender.so.1()(64bit)
Requires: libXss.so.1()(64bit)
Requires: libXtst.so.6()(64bit)
Requires: libaa.so.1()(64bit)
Requires: libacl.so.1()(64bit)
Requires: libarchive.so.13()(64bit)
Requires: libaribb24.so.0()(64bit)
Requires: libasn1.so.8()(64bit)
Requires: libasound.so.2()(64bit)
Requires: libass.so.9()(64bit)
Requires: libasyncns.so.0()(64bit)
Requires: libatk-1.0.so.0()(64bit)
Requires: libatk-bridge-2.0.so.0()(64bit)
Requires: libatspi.so.0()(64bit)
Requires: libattr.so.1()(64bit)
Requires: libavahi-client.so.3()(64bit)
Requires: libavahi-common.so.3()(64bit)
Requires: libavc1394.so.0()(64bit)
Requires: libblkid.so.1()(64bit)
Requires: libbsd.so.0()(64bit)
Requires: libc.so.6()(64bit)
Requires: libcaca.so.0()(64bit)
Requires: libcairo-gobject.so.2()(64bit)
Requires: libcairo.so.2()(64bit)
Requires: libcap.so.2()(64bit)
Requires: libcddb.so.2()(64bit)
Requires: libcef.so()(64bit)
Requires: libchromaprint.so.1()(64bit)
Requires: libcom_err.so.2()(64bit)
Requires: libcrypt.so.1()(64bit)
Requires: libcups.so.2()(64bit)
Requires: libdbus-1.so.3()(64bit)
Requires: libdbus-glib-1.so.2()(64bit)
Requires: libdca.so.0()(64bit)
Requires: libdcerpc-binding.so.0()(64bit)
Requires: libdl.so.2()(64bit)
Requires: libdrm.so.2()(64bit)
Requires: libdvbpsi.so.10()(64bit)
Requires: libdvdnav.so.4()(64bit)
Requires: libepoxy.so.0()(64bit)
Requires: libevdev.so.2()(64bit)
Requires: libexpat.so.1()(64bit)
Requires: libfaad.so.2()(64bit)
Requires: libfontconfig.so.1()(64bit)
Requires: libfreetype.so.6()(64bit)
Requires: libfribidi.so.0()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libgconf-2.so.4()(64bit)
Requires: libgcrypt.so.20()(64bit)
Requires: libgdk-3.so.0()(64bit)
Requires: libgdk-x11-2.0.so.0()(64bit)
Requires: libgdk_pixbuf-2.0.so.0()(64bit)
Requires: libgio-2.0.so.0()(64bit)
Requires: libglib-2.0.so.0()(64bit)
Requires: libgme.so.0()(64bit)
Requires: libgmodule-2.0.so.0()(64bit)
Requires: libgmp.so.10()(64bit)
Requires: libgnutls.so.30()(64bit)
Requires: libgobject-2.0.so.0()(64bit)
Requires: libgomp.so.1()(64bit)
Requires: libgpg-error.so.0()(64bit)
Requires: libgpm.so.2()(64bit)
Requires: libgsm.so.1()(64bit)
Requires: libgssapi.so.3()(64bit)
Requires: libgssapi_krb5.so.2()(64bit)
Requires: libgtk-3.so.0()(64bit)
Requires: libgtk-x11-2.0.so.0()(64bit)
Requires: libgudev-1.0.so.0()(64bit)
Requires: libharfbuzz.so.0()(64bit)
Requires: libhcrypto.so.4()(64bit)
Requires: libheimbase.so.1()(64bit)
Requires: libheimntlm.so.0()(64bit)
Requires: libhx509.so.5()(64bit)
Requires: libidn2.so.0()(64bit)
Requires: libinput.so.10()(64bit)
Requires: libjansson.so.4()(64bit)
Requires: libk5crypto.so.3()(64bit)
Requires: libkate.so.1()(64bit)
Requires: libkeyutils.so.1()(64bit)
Requires: libkrb5.so.26()(64bit)
Requires: libkrb5.so.3()(64bit)
Requires: libkrb5support.so.0()(64bit)
Requires: liblber-2.4.so.2()(64bit)
Requires: libldap_r-2.4.so.2()(64bit)
Requires: liblirc_client.so.0()(64bit)
Requires: liblz4.so.1()(64bit)
Requires: liblzma.so.5()(64bit)
Requires: liblzo2.so.2()(64bit)
Requires: libm.so.6()(64bit)
Requires: libmad.so.0()(64bit)
Requires: libmp3lame.so.0()(64bit)
Requires: libmpcdec.so.6()(64bit)
Requires: libmpeg2.so.0()(64bit)
Requires: libmpg123.so.0()(64bit)
Requires: libmtdev.so.1()(64bit)
Requires: libmtp.so.9()(64bit)
Requires: libncurses.so.5()(64bit)
Requires: libncursesw.so.5()(64bit)
Requires: libndr-krb5pac.so.0()(64bit)
Requires: libndr-nbt.so.0()(64bit)
Requires: libndr-standard.so.0()(64bit)
Requires: libnotify.so.4()(64bit)
Requires: libnsl
Requires: libnsl.so.1()(64bit)
Requires: libnspr4.so()(64bit)
Requires: libnss3.so()(64bit)
Requires: libnssutil3.so()(64bit)
Requires: libnuma.so.1()(64bit)
Requires: libogg.so.0()(64bit)
Requires: libopenjp2.so.7()(64bit)
Requires: libopenmpt.so.0()(64bit)
Requires: libopus.so.0()(64bit)
Requires: libp11-kit.so.0()(64bit)
Requires: libpango-1.0.so.0()(64bit)
Requires: libpangocairo-1.0.so.0()(64bit)
Requires: libpangoft2-1.0.so.0()(64bit)
Requires: libpixman-1.so.0()(64bit)
Requires: libplc4.so()(64bit)
Requires: libplds4.so()(64bit)
Requires: libpng16.so.16()(64bit)
Requires: libpthread.so.0()(64bit)
Requires: libpulse-simple.so.0()(64bit)
Requires: libpulse.so.0()(64bit)
Requires: libraw1394.so.11()(64bit)
Requires: libresolv.so.2()(64bit)
Requires: libroken.so.18()(64bit)
Requires: librom1394.so.0()(64bit)
Requires: librsvg-2.so.2()(64bit)
Requires: librt.so.1()(64bit)
Requires: libsamba-errors.so.1()(64bit)
Requires: libsamba-hostconfig.so.0()(64bit)
Requires: libsamba-util.so.0()(64bit)
Requires: libsamdb.so.0()(64bit)
Requires: libsamplerate.so.0()(64bit)
Requires: libsecret-1.so.0()(64bit)
Requires: libselinux.so.1()(64bit)
Requires: libshout.so.3()(64bit)
Requires: libslang.so.2()(64bit)
Requires: libsmbclient.so.0()(64bit)
Requires: libsmbconf.so.0()(64bit)
Requires: libsmime3.so()(64bit)
Requires: libsnappy.so.1()(64bit)
Requires: libsndfile.so.1()(64bit)
Requires: libsoxr.so.0()(64bit)
Requires: libspeex.so.1()(64bit)
Requires: libspeexdsp.so.1()(64bit)
Requires: libsqlite3.so.0()(64bit)
Requires: libssh2.so.1()(64bit)
Requires: libstdc++.so.6()(64bit)
Requires: libsystemd.so.0()(64bit)
Requires: libtalloc.so.2()(64bit)
Requires: libtasn1.so.6()(64bit)
Requires: libtdb.so.1()(64bit)
Requires: libtevent-util.so.0()(64bit)
Requires: libtevent.so.0()(64bit)
Requires: libthai.so.0()(64bit)
Requires: libtheora.so.0()(64bit)
Requires: libtheoradec.so.1()(64bit)
Requires: libtheoraenc.so.1()(64bit)
Requires: libtinfo.so.5()(64bit)
Requires: libtwolame.so.0()(64bit)
Requires: libudev.so.1()(64bit)
Requires: libunistring.so.2()(64bit)
Requires: libusb-1.0.so.0()(64bit)
Requires: libuuid.so.1()(64bit)
Requires: libva-drm.so.2()(64bit)
Requires: libva-wayland.so.2()(64bit)
Requires: libva-x11.so.2()(64bit)
Requires: libva.so.2()(64bit)
Requires: libvdpau.so.1()(64bit)
Requires: libvlc.so.5()(64bit)
Requires: libvlc_pulse.so.0()(64bit)
Requires: libvlc_vdpau.so.0()(64bit)
Requires: libvlc_xcb_events.so.0()(64bit)
Requires: libvlccore.so.9()(64bit)
Requires: libvorbis.so.0()(64bit)
Requires: libvorbisenc.so.2()(64bit)
Requires: libvorbisfile.so.3()(64bit)
Requires: libvulkan.so.1()(64bit)
Requires: libwavpack.so.1()(64bit)
Requires: libwayland-client.so.0()(64bit)
Requires: libwayland-cursor.so.0()(64bit)
Requires: libwayland-egl.so.1()(64bit)
Requires: libwbclient.so.0()(64bit)
Requires: libwebpmux.so.3()(64bit)
Requires: libwind.so.0()(64bit)
Requires: libwrap.so.0()(64bit)
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
Requires: libxcb-xv.so.0()(64bit)
Requires: libxcb.so.1()(64bit)
Requires: libxcrypt
Requires: libxkbcommon-x11.so.0()(64bit)
Requires: libxkbcommon.so.0()(64bit)
Requires: libxml2.so.2()(64bit)
Requires: libxvidcore.so.4()(64bit)
Requires: libz.so.1()(64bit)
Requires: libzvbi.so.0()(64bit)
Requires: rtld(GNU_HASH)


BuildRequires:  binutils
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  xz

%description
NetEase Cloud Music (网易云音乐) desktop client for Linux, distributed
by NetEase. This package repackages the official upstream .deb without
rebuilding or modifying the application binaries. NetEase's CDN refuses
datacenter IPs, so a GitHub Actions workflow mirrors the .deb to this
repository's Releases, and the build repacks it from Source0.

%prep
# Sanity check: the mirrored payload must be a readable .deb carrying a
# data archive.
ar t '%{SOURCE0}' | grep -qx data.tar.xz \
    || { echo "netease-cloud-music: unexpected payload" >&2; exit 1; }

%build
:

%install
mkdir -p %{buildroot}
ar p '%{SOURCE0}' data.tar.xz | tar xJ -C %{buildroot} --no-same-owner
# Own: every file/symlink plus the private /opt/netease tree; everything
# else (usr/bin, usr/share/...) stays unowned so the base packages keep
# their directories.
{ find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n'
  find %{buildroot}/opt -mindepth 1 -type d -printf '/opt/%%P\n' 2>/dev/null
} | sort -u | sed 's|.*|"&"|' > %{_builddir}/%{name}-filelist

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -qf %{_datadir}/icons/hicolor 2>/dev/null || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 1.2.1-6
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 1.2.1-5
- Filter legacy Ubuntu payload sonames unavailable on Fedora 45

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.2.1-3
- Fetch the payload from a GitHub Releases mirror: the Actions runner
  can download NetEase's Referer-gated .deb, so the build repacks it
  from Source0 and the payload joins the RPM database
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Send Referer/UA when fetching the payload: the CDN 403s bare requests
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.2.1-1
- Initial package: install-time downloader for the official NetEase .deb
