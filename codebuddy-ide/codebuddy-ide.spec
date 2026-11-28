%global debug_package %{nil}
# Repack upstream binaries byte-for-byte: disable RPM build-side processing
# (brp-strip / brp-compress / check-rpaths), which rejects the upstream
# binaries' "${ORIGIN}" runpaths and would modify the payload.
%global __os_install_post %{nil}
# The VSCode-fork payload bundles private libraries (libEGL, libGLESv2,
# libffmpeg, ...). Suppress all auto-generated provides/requires and
# declare the host dependency set explicitly below; bundled private
# sonames resolve via ${ORIGIN} runpath.
%global __provides_exclude ^.*$
%global __requires_exclude ^.*$
# Source0 is the official CodeBuddy IDE (international brand of Tencent's
# WorkBuddy; domestic channel) Linux x64 .deb, discovered through the
# update API
# https://copilot.tencent.com/v2/update?platform=ide-linux-x64&version=1.0.0&x-machine-id=default
# The URL embeds a build hash and changes with every release, so
# scripts/check-updates.py rewrites both Version and Source0 automatically.
Name:           codebuddy-ide
Version:        4.12.0.37847260
Release:        1%{?dist}
Summary:        CodeBuddy IDE - Tencent's AI-powered IDE for Linux
License:        LicenseRef-Tencent-CodeBuddy-IDE-Software-License
URL:            https://www.codebuddy.ai/
Source0:        https://download.codebuddy.cn/aiide/linux-x64/CodeBuddy-linux-x64-4.12.0.37847260-b4c35ed0-cn.deb

ExclusiveArch:  x86_64
BuildRequires:  binutils
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  xz

# Requires mirror the deb's Chromium/Electron dependency list, mapped to
# Fedora-native packages; the soname list below was generated mechanically
# from the payload and verified against Fedora 45 repodata.
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libdrm
Requires:       libsecret
Requires:       libxkbfile
Requires:       libxkbcommon
Requires:       libnotify
Requires:       mesa-libgbm
Requires:       nss
Requires:       xdg-utils

%description
CodeBuddy IDE is Tencent's AI-powered code editor (the international
brand of WorkBuddy): a VSCode fork with agent mode, design-to-code
integration and one-stop build/deploy. This package repacks the official
upstream x86_64 .deb (domestic channel, downloaded from the official
update API) without rebuilding or modifying the application binaries.
The application installs under /usr/share/buddycn with /usr/bin/buddycn.

%prep
echo "Source0 tracks Tencent's official CodeBuddy IDE .deb from the update API."

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
ar x %{SOURCE0} data.tar.xz
tar xJf data.tar.xz
rm -f data.tar.xz
{
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | awk '{ if ($0 ~ /[[:space:]]/) print "%%dir \"" $0 "\""; else print "%%dir " $0 }'
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' |
    awk '{ if ($0 ~ /[[:space:]]/) print "\"" $0 "\""; else print $0 }'
} | sort > %{_builddir}/%{name}-filelist

# Electron apps under Wayland compositors (niri) can lose fcitx5 IME input;
# pin the X11 ozone platform for every desktop entry this payload ships.
for f in %{buildroot}%{_datadir}/applications/*.desktop; do
    [ -f "$f" ] || continue
    sed -i -e 's|^Exec=\(.*\)|Exec=env ELECTRON_OZONE_PLATFORM_HINT=x11 \1|' "$f" || :
done

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi
if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database %{_datadir}/mime &>/dev/null || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi
if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database %{_datadir}/mime &>/dev/null || :
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 4.12.0.37847260-1
- Initial package: repack the official CodeBuddy IDE .deb (domestic channel)
