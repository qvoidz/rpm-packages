%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# The app bundle ships helper binaries for other architectures and OSes
# (aarch64 / armhf / loongarch / riscv64, musl, FreeBSD). rpm's dependency
# generator scans them too and emits soname requirements (e.g.
# ld-linux-aarch64.so.1, libc.musl-*, libc.so.7) that no Fedora package
# provides; the helpers only ever run inside the app's own sandbox, so
# filter those false requirements out.
%global __requires_exclude ^(ld-linux-(aarch64|armhf|loongarch|riscv64)|libc\\.(musl|so\\.7)|libcxxrt|libc\\+\\+abi|libc\\+\\+\\.so\\.9|libm\\.so\\.(5|10\\.1)|libm\\.so\\.6\\(GLIBC_2\\.17|libpthread\\.so\\.(26\\.1|0\\(GLIBC_2\\.17\\))|libgcc_s\\.so\\.1\\(GCC_3\\.5\\)|libstdc\\+\\+\\.so\\.6\\(CXXABI_ARM|libutil\\.so\\.1\\(GLIBC_2\\.17\\))
# The payload also bundles x86-64 copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires (observed when installing fcitx5-wetypex). Suppress all
# auto-generated provides; the package's own name provides are intrinsic
# and unaffected.
%global __provides_exclude ^.*$
# Source0 is Tencent's official WorkBuddy Linux RPM, discovered through the
# update API https://copilot.tencent.com/v2/update?platform=workbuddy-linux-x64-rpm
# The URL embeds a build hash and changes with every release, so
# scripts/check-updates.py rewrites both Version and Source0 automatically.
Name:           workbuddy
Version:        5.6.2.40046327
Release:        2%{?dist}
Summary:        WorkBuddy AI coding assistant desktop client from Tencent
License:        LicenseRef-Tencent-WorkBuddy-Software-License
URL:            https://www.workbuddy.cn/
Source0:        https://download.codebuddy.cn/workbuddy/saas/linux-x64-rpm/WorkBuddy-linux-x64-rpm-5.6.2.40046327-c7b525f3.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# Keep the upstream binary artifact pinned even though the download URL is
# rolling. Requires mirror the upstream RPM's dependency list (Fedora-native
# package names).
Requires:       (libXtst or libXtst6)
Requires:       (libuuid or libuuid1)
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       mesa-libgbm
Requires:       nss
Requires:       xdg-utils

%description
WorkBuddy AI coding assistant desktop client for Linux, distributed by
Tencent. This package repackages the official upstream RPM without rebuilding
or modifying the application binaries.

The application's built-in updater points back to the official website, which
lists no Linux download; upgrade this package from the repository instead.

%prep
echo "Source0 tracks Tencent's official Linux RPM from the update API."

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
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 5.6.2.40046327-1
- Repackage the official Tencent WorkBuddy Linux RPM (from the update API channel) for COPR
