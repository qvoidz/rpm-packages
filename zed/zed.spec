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
Version:        1.29.2
Release:        2%{?dist}
Summary:        Zed - a high-performance, multiplayer code editor
License:        LicenseRef-Zed-License
URL:            https://zed.dev/
Source0:        https://github.com/zed-industries/zed/releases/download/v1.29.2/zed-linux-x86_64.tar.gz

ExclusiveArch:  x86_64
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  gzip

Requires:       alsa-lib
Requires:       hicolor-icon-theme

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

%check
# The public launcher is hard-wired to bin/zed; fail the build if upstream
# changes the bundle layout instead of shipping a broken /usr/bin/zed.
test -x %{buildroot}%{_libdir}/zed.app/bin/zed
test -x %{buildroot}%{_bindir}/zed

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files
%{_libdir}/zed.app
%{_bindir}/zed

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.29.2-1
- Initial package: repack the official zed-linux-x86_64 release tarball
