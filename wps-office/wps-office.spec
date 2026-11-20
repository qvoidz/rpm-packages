%global debug_package %{nil}
%global __os_install_post %{nil}
# WPS Office publishes a version-independent rolling RPM
# (https://wdl1.pcfg.cache.wpscdn.com/wpsdl/wpsoffice/download/linux/
# wps-office.rpm, always the latest release). Source0 never changes;
# scripts/check-updates.py sniffs the RPM header (HTTP Range, ~4 MB)
# for the upstream version and rewrites Version when it advances.
Name:           wps-office
Version:        12.1.2.29182.AK.preread.sw
Release:        1%{?dist}
Summary:        WPS Office - Kingsoft office suite for Linux
License:        LicenseRef-Kingsoft-WPS-Office-License
URL:            https://linux.wps.cn/
Source0:        https://wdl1.pcfg.cache.wpscdn.com/wpsdl/wpsoffice/download/linux/wps-office.rpm

ExclusiveArch:  x86_64
BuildRequires:  coreutils

# Requires mirror the upstream RPM header's dependency list.
Requires:       cups-libs
Requires:       fontconfig
Requires:       glib2
Requires:       libGLU
Requires:       libICE
Requires:       libSM
Requires:       libX11
Requires:       libXext
Requires:       libXrender
Requires:       libxcb
Requires:       python3

%description
WPS Office (金山办公) suite for Linux, distributed by Kingsoft. This
package repacks the official upstream RPM without rebuilding or
modifying the application binaries.

%prep
echo "Source0 tracks WPS Office's official rolling RPM."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
# Wrap entries containing spaces in double quotes (supported by rpm >= 4.20
# file lists); WPS ships template documents like "labor contract.dotm".
find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' \
    | awk '{ if ($0 ~ /[[:space:]]/) printf("\"%s\"\n", $0); else print }' \
    | sort > %{_builddir}/%{name}-filelist

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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 12.1.2.29182.AK.preread.sw-1
- Initial package: repack the official WPS Office RPM for COPR
