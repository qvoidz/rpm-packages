%global debug_package %{nil}
%global __os_install_post %{nil}
# pi ships a release tarball containing the pi/ directory: the main
# executable, bundled assets, themes, export templates and extension
# examples. rpm's automatic dependency generation resolves the host
# sonames correctly (glibc / libstdc++ only), so no filter is needed.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag v<version>, asset pi-linux-x64.tar.gz).
Name:           pi
Version:        1.7.0
Release:        1%{?dist}
Summary:        pi - a coding agent for the terminal
License:        MIT
URL:            https://pi.dev/
Source0:        https://github.com/earendil-works/pi/releases/download/v1.7.0/pi-linux-x64.tar.gz

ExclusiveArch:  x86_64
BuildRequires:  coreutils
BuildRequires:  gzip
BuildRequires:  tar

%description
pi is a minimalist coding agent for the terminal by Mario Zechner
(earendil-works): one binary, a TUI, provider-agnostic model support and
a TypeScript extension SDK. This package installs the official upstream
pi-linux-x64 release unmodified under %{_libdir}/pi and exposes
/usr/bin/pi.

%prep
%setup -q -c

%build
:

%install
mkdir -p %{buildroot}%{_libdir}
cp -a pi %{buildroot}%{_libdir}/pi
mkdir -p %{buildroot}%{_bindir}
ln -s %{_libdir}/pi/pi %{buildroot}%{_bindir}/pi

%check
# Fail the build if upstream changes the bundle layout instead of
# shipping a broken /usr/bin/pi.
test -x %{buildroot}%{_libdir}/pi/pi
test -L %{buildroot}%{_bindir}/pi

%files
%{_libdir}/pi
%{_bindir}/pi

%changelog
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 1.7.0-1
- Initial package: official pi-linux-x64 release tarball
