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
# rpm's ELF scanner also turns the payload's bundled private libraries
# (libflutter_linux_gtk.so, the plugin libs, ...) into auto Requires that
# Fedora cannot satisfy. With the old FlClash package (which provided those
# sonames) obsoleted away in the same transaction, they would break dnf
# resolution. Suppress them all; the explicit Requires below fully describe
# the real host dependencies (everything else lives inside gtk3's closure).
%global __requires_exclude ^.*$

Name:           flclash
Version:        0.9.4
Release:        5%{?dist}
Summary:        A modern proxy client based on Clash
License:        GPL-3.0-or-later
URL:            https://github.com/chen08209/FlClash
Source0:        https://github.com/chen08209/FlClash/releases/download/v%{version}/FlClash-%{version}-linux-amd64.rpm

BuildRequires:  cpio
BuildRequires:  rpm
Requires:       gtk3
Requires:       libsecret
# This package replaced an earlier, differently-named build of upstream's
# own RPM (Name: FlClash, capital F). Both ship identical file paths under
# /usr/share/FlClash, so without an Obsoletes dnf fails the transaction with
# file conflicts. Obsoletes makes dnf erase FlClash in the same transaction.
Obsoletes:      FlClash < 1.0
Provides:       FlClash = %{version}-%{release}

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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.9.4-5
- Suppress auto-generated requires of bundled private libraries; they used
  to be satisfied by the (now obsoleted) FlClash package's own provides
- Declare the real host dependencies explicitly (gtk3, libsecret)
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.9.4-4
- Obsolete/Provide FlClash: the old differently-named package owns the same
  /usr/share/FlClash paths and blocks installation with file conflicts
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.9.4-2
- Preserve the upstream Core binary byte-for-byte; disable brp-strip processing
- Match upstream libsecret dependency and package scriptlets
