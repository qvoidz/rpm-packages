%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# The payload bundles its own copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires (observed when installing fcitx5-wetypex). Suppress all
# auto-generated provides; the package's own name provides are intrinsic
# and unaffected.
%global __provides_exclude ^.*$
# Same story on the requirement side: rpm's ELF scanner turns the payload's
# NEEDED entries (openssl 1.1 sonames, bundled libbugly/libcrbase/
# liblinux_compat.so) into auto Requires that Fedora cannot satisfy, even
# though every one of those libraries ships inside the payload and is found
# via "${ORIGIN}" runpaths. Suppress them all; the explicit Fedora-native
# Requires below fully describe the real host dependencies.
%global __requires_exclude ^.*$
# Bare asset URL, bumped automatically by scripts/check-updates.py from
# Tencent's download config (cdn-go.cn/.../rainbow/pcConfig.json). Tencent's
# CDN (qqdl.gtimg.cn) rejects datacenter IPs, and since Oct 2026 every QQNT
# path additionally requires a real-time signature: bare links get HTTP 403
# regardless of network or Referer. .github/workflows/mirror.yml therefore
# signs the URL via Tencent's public API and mirrors the payload to GitHub
# Releases, from where this spec fetches it as a plain Source0 during the
# SRPM build (COPR's binary chroots are fully offline; only the SRPM stage
# has network access, and it can only do bare GETs).
%global qq_rpm_url https://qqdl.gtimg.cn/qqfile/QQNTV2/9.9.37/release/816b3c79/QQ_3.2.35_261103_x86_64_01.rpm

Name:           linuxqq
Version:        3.2.35
Release:        11%{?dist}
Summary:        QQ desktop client from Tencent (NTQQ)
License:        LicenseRef-Tencent-QQ-Software-License
URL:            https://im.qq.com/linuxqq/

%global qq_mirror https://github.com/qvoidz/rpm-packages/releases/download/linuxqq-%{version}
Source0:        %{qq_mirror}/%(basename %{qq_rpm_url})

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
QQ (NTQQ) desktop client for Linux, distributed by Tencent.
This package repackages the official upstream RPM without rebuilding
or modifying the application binaries. The payload is fetched at BUILD
time: Tencent's CDN requires per-request URL signing, so a GitHub
Actions workflow mirrors the official RPM to this repository's
Releases, and the build repacks it from Source0.

%prep
# Sanity check: the mirrored payload must be the official linuxqq RPM of
# the expected version.
payload=$(rpm -qp --qf '%{NAME}-%{VERSION}' '%{SOURCE0}')
echo "linuxqq: payload RPM is $payload"
case "$payload" in
    # upstream appends its internal build number: 3.2.35_54395
    linuxqq-%{version}|linuxqq-%{version}_*) : ;;
    *) echo "linuxqq: unexpected payload '$payload'" >&2; exit 1 ;;
esac

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio '%{SOURCE0}' | cpio -idm --quiet --no-absolute-filenames
# Own: every file/symlink and every payload directory, so uninstall leaves
# no orphaned empty dirs. Only /usr/lib and /usr/lib64 themselves are
# deliberately left unowned: filesystem ships them read-only 0555 and
# claiming them with a mismatched mode conflicts. Their subdirectories
# (e.g. /usr/lib/.build-id from the upstream RPM) are owned normally.
{ find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n'
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | sed 's|^|%%dir |'
  rpm -qp --dump '%{SOURCE0}' | awk '$5 ~ /^04/ {print $1}'
} | sort -u | sed -e 's|.*|"&"|' -e 's|^"%dir \(.*\)"$|%dir \1|' > %{_builddir}/%{name}-filelist

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
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 3.2.35-11
- Own every payload directory in the file list (except /usr/lib and /usr/lib64, which filesystem ships read-only 0555) so uninstall leaves no orphaned empty directories behind
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-10
- Suppress auto-generated requires of bundled libraries (openssl 1.1 sonames,
  libbugly/libcrbase/liblinux_compat.so); they all ship in the payload and
  resolve via "${ORIGIN}" runpaths, but made dnf fail transaction resolution
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-8
- Fetch the payload from a GitHub Releases mirror: .github/workflows/
  mirror.yml signs Tencent's bare URL and publishes the official RPM as
  a release asset, so Source0 works in COPR's offline build chroots
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-7
- Resolve build hosts via DoH fallback: COPR chroots can lack a resolver
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-6
- Own only the /opt payload tree plus upstream-owned dirs; leave /usr
  directories unowned to avoid conflicts with the filesystem package
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-4
- Restore upstream directory modes to avoid ownership conflicts (filesystem)
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-3
- Own the payload directories too, so uninstall leaves no empty tree
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-2
- Convert to a build-time repack: bare qqdl links are 403'd since Oct 2026
  (real-time URL signing), so %prep signs via Tencent's public GetSign API
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.2.35-1
- Installer shell package: download the official Tencent RPM at install time
  (Tencent's CDN blocks build machines), like flatpak's extra-data
