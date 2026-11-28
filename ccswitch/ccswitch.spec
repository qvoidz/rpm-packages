%global debug_package %{nil}
%global __os_install_post %{nil}
# CC-Switch publishes an official Linux RPM (Tauri app). Repack it
# byte-for-byte under the name ccswitch. The payload is one clean ELF
# binary linking only system libraries (gtk3 / webkit2gtk-4.1 /
# ayatana appindicator), so rpm's automatic dependency generation
# resolves the host sonames correctly and no filter is needed.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag v<version>, asset
# CC-Switch-v<version>-Linux-x86_64.rpm).
Name:           ccswitch
Version:        4.0.44
Release:        1%{?dist}
Summary:        CC Switch - desktop switcher for Claude Code / Codex providers
License:        MIT
URL:            https://github.com/farion1231/cc-switch
Source0:        https://github.com/farion1231/cc-switch/releases/download/v4.0.44/CC-Switch-v4.0.44-Linux-x86_64.rpm

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  coreutils
BuildRequires:  rpm

# The upstream payload owns no directories itself: the desktop file lives
# in /usr/share/applications (desktop-file-utils) and the icons in
# /usr/share/icons/hicolor (hicolor-icon-theme); keep those packages as
# the directory owners so uninstall leaves no orphaned skeletons.
Requires:       desktop-file-utils
Requires:       hicolor-icon-theme

%description
CC Switch is a desktop app for switching and managing API provider
configurations of AI coding CLIs: swap Claude Code and Codex between
providers at one click, with preset templates and config backup. This
package repackages the official upstream Linux x86_64 RPM without
rebuilding or modifying the application binary.

%prep
echo "Source0 tracks the official CC-Switch RPM from GitHub releases."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
{
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | awk '{ if ($0 ~ /[[:space:]]/) print "%%dir \"" $0 "\""; else print "%%dir " $0 }'
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' |
    awk '{ if ($0 ~ /[[:space:]]/) print "\"" $0 "\""; else print $0 }'
} | sort > %{_builddir}/%{name}-filelist

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
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -qf %{_datadir}/icons/hicolor 2>/dev/null || :
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 4.0.44-1
- Initial package: repack the official CC-Switch RPM as ccswitch
