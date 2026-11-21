%global debug_package %{nil}
%global __os_install_post %{nil}
# The zed.app payload bundles its own copies of common system libraries
# (libstdc++, ...). rpm's automatic generator turns them into soname
# Provides, shadowing the real Fedora providers: dnf may pull this package
# just to satisfy e.g. libstdc++.so.6 (observed when installing
# fcitx5-wetypex). Suppress all auto-generated provides; the package's own
# name provides are intrinsic and unaffected.
%global __provides_exclude ^.*$
# Zed ships a zed.app bundle in its release tarball; this package installs
# it under /usr/lib/zed.app unmodified and exposes /usr/bin/zed.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag v<version>, asset zed-linux-x86_64.tar.gz).
Name:           zed
Version:        1.29.3
Release:        2%{?dist}
Summary:        Zed - a high-performance, multiplayer code editor
License:        LicenseRef-Zed-License
URL:            https://zed.dev/
Source0:        https://github.com/zed-industries/zed/releases/download/v1.29.3/zed-linux-x86_64.tar.gz

ExclusiveArch:  x86_64
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  gzip

Requires:       alsa-lib
Requires:       hicolor-icon-theme
Requires:       desktop-file-utils

%description
Zed is a high-performance code editor written in Rust, with built-in
collaboration, LSP support and an integrated terminal. This package
repacks the official upstream zed-linux-x86_64.tar.gz release without
rebuilding or modifying any binary.

%prep
%setup -q -c

%build
:

%install
mkdir -p %{buildroot}%{_libdir}
cp -a zed.app %{buildroot}%{_libdir}/zed.app
mkdir -p %{buildroot}%{_bindir}
ln -s %{_libdir}/zed.app/bin/zed %{buildroot}%{_bindir}/zed
# Desktop integration: ship upstream's own .desktop file and hicolor icons.
# Exec=zed %U matches the /usr/bin/zed symlink; Icon=zed matches the pngs
# installed below. desktop-file-utils / hicolor-icon-theme own the parent
# directories, so uninstall leaves no orphaned directory skeletons.
mkdir -p %{buildroot}%{_datadir}/applications
install -m 0644 zed.app/share/applications/dev.zed.Zed.desktop \
    %{buildroot}%{_datadir}/applications/
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps \
         %{buildroot}%{_datadir}/icons/hicolor/1024x1024/apps
install -m 0644 zed.app/share/icons/hicolor/512x512/apps/zed.png \
    %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/
install -m 0644 zed.app/share/icons/hicolor/1024x1024/apps/zed.png \
    %{buildroot}%{_datadir}/icons/hicolor/1024x1024/apps/

%check
# The public launcher is hard-wired to bin/zed; fail the build if upstream
# changes the bundle layout instead of shipping a broken /usr/bin/zed.
test -x %{buildroot}%{_libdir}/zed.app/bin/zed
test -L %{buildroot}%{_bindir}/zed
# The desktop integration ships upstream files verbatim; fail if upstream
# renames or moves them.
test -f %{buildroot}%{_datadir}/applications/dev.zed.Zed.desktop
test -f %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/zed.png
test -f %{buildroot}%{_datadir}/icons/hicolor/1024x1024/apps/zed.png

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
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -qf %{_datadir}/icons/hicolor 2>/dev/null || :
fi

%files
%{_libdir}/zed.app
%{_bindir}/zed
%{_datadir}/applications/dev.zed.Zed.desktop
%{_datadir}/icons/hicolor/512x512/apps/zed.png
%{_datadir}/icons/hicolor/1024x1024/apps/zed.png

%changelog
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 1.29.3-2
- Ship upstream desktop file and hicolor icons so Zed appears in
  application launchers (Exec=zed %U matches the /usr/bin/zed symlink;
  desktop-file-utils and hicolor-icon-theme own the parent dirs).
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 1.29.3-1
- Update to upstream Zed v1.29.3
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 1.29.2-3
- Check the /usr/bin/zed symlink itself; its absolute target is outside buildroot

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.29.2-1
- Initial package: repack the official zed-linux-x86_64 release tarball
