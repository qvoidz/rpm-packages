%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# Tencent's CDN (qqdl.gtimg.cn) rejects datacenter IPs, so COPR cannot fetch
# the source directly. scripts/mirror-linuxqq.py downloads it from a machine
# with China network access and publishes it as a GitHub release asset
# (tag linuxqq-<version>) of this repository; Source0 points there.
Name:           linuxqq
Version:        3.2.35
Release:        1%{?dist}
Summary:        QQ desktop client from Tencent (NTQQ)
License:        LicenseRef-Tencent-QQ-Software-License
URL:            https://im.qq.com/linuxqq/
Source0:        https://github.com/qvoidz/rpm-packages/releases/download/linuxqq-3.2.35/QQ_3.2.35_261103_x86_64_01.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Requires mirror the upstream RPM's dependency list (Fedora-native names).
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libnotify
Requires:       libuuid
Requires:       nss
Requires:       xdg-utils

%description
QQ (NTQQ) desktop client for Linux, distributed by Tencent. This package
repackages the official upstream RPM without rebuilding or modifying the
application binaries.

%prep
echo "Source0 tracks Tencent's official Linux QQ RPM from the download config."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' | sort > %{_builddir}/%{name}-filelist

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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-1
- Repackage the official Tencent Linux QQ RPM (from the official download config) for COPR
