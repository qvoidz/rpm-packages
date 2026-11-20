%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which would modify the payload.
%global __os_install_post %{nil}
# Bare asset URL, rewritten automatically by scripts/check-updates.py from
# the official download page (the upstream client has been frozen at 1.2.1
# since 2019). NetEase's CDN (d1.music.126.net) 403s bare requests and, like
# QQ, cannot be fetched by a build machine, so
# .github/workflows/mirror.yml downloads it with Referer on an Actions
# runner and publishes it as a GitHub Release asset; this spec fetches the
# mirrored asset as plain Source0 during the SRPM build (COPR's binary
# chroots are fully offline; only the SRPM stage has network access).
%global netease_deb_url https://d1.music.126.net/dmusic/netease-cloud-music_1.2.1_amd64_ubuntu_20190428.deb

Name:           netease-cloud-music
Version:        1.2.1
Release:        3%{?dist}
Summary:        NetEase Cloud Music (网易云音乐) desktop client for Linux
License:        LicenseRef-NetEase-CloudMusic-Software-License
URL:            https://music.163.com/

%global ncm_mirror https://github.com/qvoidz/rpm-packages/releases/download/netease-cloud-music-%{version}
Source0:        %{ncm_mirror}/%(basename %{netease_deb_url})

ExclusiveArch:  x86_64

# The upstream .deb was built for Ubuntu 19.04 and links these two legacy
# libc interfaces that Fedora ships in separate packages.
Requires:       libxcrypt
Requires:       libnsl

BuildRequires:  binutils
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  xz

%description
NetEase Cloud Music (网易云音乐) desktop client for Linux, distributed
by NetEase. This package repackages the official upstream .deb without
rebuilding or modifying the application binaries. NetEase's CDN refuses
datacenter IPs, so a GitHub Actions workflow mirrors the .deb to this
repository's Releases, and the build repacks it from Source0.

%prep
# Sanity check: the mirrored payload must be a readable .deb carrying a
# data archive.
ar t '%{SOURCE0}' | grep -qx data.tar.xz \
    || { echo "netease-cloud-music: unexpected payload" >&2; exit 1; }

%build
:

%install
mkdir -p %{buildroot}
ar p '%{SOURCE0}' data.tar.xz | tar xJ -C %{buildroot} --no-same-owner
# Own: every file/symlink plus the private /opt/netease tree; everything
# else (usr/bin, usr/share/...) stays unowned so the base packages keep
# their directories.
{ find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n'
  find %{buildroot}/opt -mindepth 1 -type d -printf '/opt/%%P\n' 2>/dev/null
} | sort -u | sed 's|.*|"&"|' > %{_builddir}/%{name}-filelist

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -qf %{_datadir}/icons/hicolor 2>/dev/null || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.2.1-3
- Fetch the payload from a GitHub Releases mirror: the Actions runner
  can download NetEase's Referer-gated .deb, so the build repacks it
  from Source0 and the payload joins the RPM database
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Send Referer/UA when fetching the payload: the CDN 403s bare requests
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.2.1-1
- Initial package: install-time downloader for the official NetEase .deb
