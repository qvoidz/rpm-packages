Name:           flclash
Version:        0.9.4
Release:        1%{?dist}
Summary:        A modern proxy client based on Clash
License:        GPL-3.0-or-later
URL:            https://github.com/chen08209/FlClash
Source0:        https://github.com/chen08209/FlClash/releases/download/v%{version}/FlClash-dev-%{version}-linux-amd64.rpm

BuildRequires:  cpio
BuildRequires:  rpm

Requires:       glibc
Requires:       gtk3
Requires:       libX11
Requires:       libXcursor
Requires:       libXrandr
Requires:       libXinerama
Requires:       libXi
Requires:       libXrender
Requires:       mesa-libEGL
Requires:       mesa-libGL
Requires:       nss
Requires:       alsa-lib

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
find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%P\n' | sort > %{_builddir}/%{name}-filelist

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    for d in /usr/share/icons/*; do
        [ -d "$d" ] && gtk-update-icon-cache -q "$d" 2>/dev/null || :
    done
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files -f %{_builddir}/%{name}-filelist
