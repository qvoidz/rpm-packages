%global debug_package %{nil}
Name:           wechat
Version:        4.1.13.26
Release:        1%{?dist}
Summary:        WeChat desktop client from Tencent
License:        LicenseRef-Tencent-Weixin-Software-and-Service-License
URL:            https://weixin.qq.com/
Source0:        https://dldir1v6.qq.com/weixin/Universal/Linux/WeChatLinux_x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Keep the upstream binary artifact pinned even though Tencent uses a
# version-independent download URL.
%description
WeChat desktop client for Linux, distributed by Tencent.
This package repackages the official upstream RPM without rebuilding
or modifying the application binaries.

%prep
echo "%{SOURCE0}"
echo "919461e37f80abb277ec0d7acde67ea1e64aaaf2472b4b1d954f3f1f76a91d02  %{SOURCE0}" | sha256sum -c -

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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 4.1.13.26-1
- Repackage the official Tencent WeChat RPM for COPR
