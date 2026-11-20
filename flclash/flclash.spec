%global debug_package %{nil}
# FlClash validates the Core binary against a SHA256 embedded in Helper.
# Disable RPM post-install build processing (especially brp-strip), which
# would modify Core and make the application hang or fail at startup.
%global __os_install_post %{nil}
# The payload may bundle its own copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires (observed when installing fcitx5-wetypex). Suppress all
# auto-generated provides; the package's own name provides are intrinsic
# and unaffected.
%global __provides_exclude ^.*$

Name:           flclash
Version:        0.9.4
Release:        3%{?dist}
Summary:        A modern proxy client based on Clash
License:        GPL-3.0-or-later
URL:            https://github.com/chen08209/FlClash
Source0:        https://github.com/chen08209/FlClash/releases/download/v%{version}/FlClash-%{version}-linux-amd64.rpm

BuildRequires:  cpio
BuildRequires:  rpm
Requires:       libsecret

%description
FlClash is a graphical proxy client based on Clash.

%prep
%setup -q -c -T

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' | sort > %{_builddir}/%{name}-filelist

%post
update-desktop-database %{_datadir}/applications &> /dev/null || :

%postun
if [ "$1" = 0 ]; then
    systemctl disable --now flclash-helper.service >/dev/null 2>&1 || true
    rm -f /etc/systemd/system/flclash-helper.service
    systemctl daemon-reload >/dev/null 2>&1 || true
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.9.4-2
- Preserve the upstream Core binary byte-for-byte; disable brp-strip processing
- Match upstream libsecret dependency and package scriptlets
