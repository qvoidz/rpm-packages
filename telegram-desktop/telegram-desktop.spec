%global debug_package %{nil}
# Repack the upstream portable build byte-for-byte: disable RPM build-side
# processing (brp-strip / brp-compress / check-rpaths), which would modify
# the payload or reject the bundled Qt/OpenAL stack.
%global __os_install_post %{nil}
# The payload bundles Qt 6, OpenAL, FFmpeg and friends inside the single
# Telegram binary. rpm's automatic generator turns such bundled libraries
# into soname Provides, shadowing the real Fedora providers and making dnf
# pull this package to satisfy unrelated soname requires (observed with
# fcitx5-wetypex). Suppress all auto-generated provides; the package's own
# name provides are intrinsic and unaffected.
%global __provides_exclude ^.*$
# Same story on the requirement side: everything the binary needs from the
# host is enumerated in the explicit Requires below (mechanically derived
# from `rpm -qpR` on a first-pass build + dnf sack classification on
# fedora:45, plus the dlopen'd runtime libraries the ELF scanner cannot
# see). Suppress auto-generated requires entirely.
%global __requires_exclude ^.*$
# Official portable build, repacked into an RPM. scripts/check-updates.py
# rewrites Version and Source0 from telegramdesktop/tdesktop
# releases/latest (tag v<version>, asset td-setup-linux-x64-<version>.tar.xz).
Name:           telegram-desktop
Version:        7.4.6
Release:        1%{?dist}
Summary:        Telegram Desktop messaging app (official portable build)
License:        LicenseRef-Telegram-Desktop-License
URL:            https://telegram.org/
Source0:        https://github.com/telegramdesktop/tdesktop/releases/download/v7.4.6/td-setup-linux-x64-7.4.6.tar.xz
Source1:        https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/Resources/art/icon512.png

ExclusiveArch:  x86_64

BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  xz

# Host dependencies. Direct NEEDED sonames (classified against fedora:45
# repodata): cairo/fontconfig/freetype/glib2/pango closures. Everything
# else the binary statically bundles (Qt 6, OpenAL, FFmpeg, openssl, ...)
# lives inside the payload and is found via ${ORIGIN} runpaths.
Requires:       cairo
Requires:       fontconfig
Requires:       freetype
Requires:       glib2
Requires:       pango
# dlopen'd at runtime (invisible to rpm's ELF scanner):
# - libgtk-3: GTK dialogs / portal integration / tray fallback
# - libasound.so.2 / libpulse.so.0: audio backends (pulse is recommended)
# - libwayland-client.so.0: Wayland windowing backend
# - libEGL.so.1 / libGLX.so.0: GL rendering (same rationale as FlClash's
#   mesa-libEGL declaration)
# - libdbus-1.so.3: D-Bus notifications / MPRIS
Requires:       gtk3
Requires:       alsa-lib
Requires:       pulseaudio-libs
Requires:       libwayland-client
Requires:       mesa-libEGL
Requires:       mesa-libGL
Requires:       dbus-libs
Requires:       hicolor-icon-theme
Requires:       desktop-file-utils

%description
Telegram Desktop is the official desktop client for the Telegram messaging
network. This package repacks the official upstream Linux portable build
(td-setup-linux-x64 tarball) without rebuilding or modifying any binary;
the payload bundles its own Qt 6 / OpenAL / FFmpeg stack. The bundled
Updater cannot write into the read-only system tree, so application
updates are delivered through this RPM (dnf upgrade), not in-app
self-updates.

%prep
%setup -q -c -T
tar -xJf %{SOURCE0}

%build
:

%install
install -Dm0755 Telegram/Telegram  %{buildroot}%{_libdir}/telegram-desktop/Telegram
install -Dm0755 Telegram/Updater   %{buildroot}%{_libdir}/telegram-desktop/Updater
# Relative symlink, the Fedora-preferred form.
install -d %{buildroot}%{_bindir}
ln -s ../%{_lib}/telegram-desktop/Telegram %{buildroot}%{_bindir}/telegram-desktop
install -Dm0644 %{SOURCE1} %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/telegram.png
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/org.telegram.desktop.desktop <<DESKTOP
[Desktop Entry]
Type=Application
Version=1.0
Name=Telegram Desktop
Comment=Official Telegram Desktop Client
Exec=telegram-desktop -- %u
Icon=telegram
Terminal=false
StartupWMClass=TelegramDesktop
Categories=Network;InstantMessaging;Chat;
MimeType=x-scheme-handler/tg;
DESKTOP

%check
test -x %{buildroot}%{_libdir}/telegram-desktop/Telegram
test -x %{buildroot}%{_bindir}/telegram-desktop
test -s %{buildroot}%{_datadir}/applications/org.telegram.desktop.desktop

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files
%{_libdir}/telegram-desktop/
%{_bindir}/telegram-desktop
%{_datadir}/icons/hicolor/512x512/apps/telegram.png
%{_datadir}/applications/org.telegram.desktop.desktop

%changelog
* Tue Nov 24 2026 COPR Builder <copr@example.invalid> - 7.4.6-1
- Update to upstream Telegram Desktop v7.4.6
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 7.4.4-1
- Initial package: repack the official td-setup-linux-x64 portable tarball
  (explicit-deps mode: auto requires/provides suppressed, host deps
  declared mechanically from dnf sack classification plus dlopen'd
  audio/wayland/GL/GTK runtime libraries)
