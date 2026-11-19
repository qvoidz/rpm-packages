%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
Name:           wechat
Version:        4.1.13.26
Release:        2%{?dist}
Summary:        WeChat desktop client from Tencent
License:        LicenseRef-Tencent-Weixin-Software-and-Service-License
URL:            https://weixin.qq.com/
Source0:        https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Source0 is Tencent's version-independent download URL: its payload changes
# with every WeChat release, so the bytes are not hash-pinned here.
# scripts/check-updates.py sniffs the newest version directly from the RPM
# header (HTTP Range request) and bumps Version automatically.
%description
WeChat desktop client for Linux, distributed by Tencent.
This package repackages the official upstream RPM without rebuilding
or modifying the application binaries.

%prep
echo "Source0 tracks Tencent's rolling download; no hash pin applied."

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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 4.1.13.26-2
- Drop the pinned SHA-256 so the rolling Tencent download can be tracked
- Repackage the official Tencent WeChat RPM for COPR
