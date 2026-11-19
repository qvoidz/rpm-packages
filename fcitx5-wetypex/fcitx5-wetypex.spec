Name:           fcitx5-wetypex
Version:        3.0.1.684
Release:        9%{?dist}
Summary:        WeTypeX input method adapter for Fcitx5
License:        GPL-3.0-or-later
URL:            https://github.com/panxuc/fcitx5-wetypex
Source0:        https://github.com/panxuc/fcitx5-wetypex/releases/download/v%{version}-9/fcitx5-wetypex-%{version}-9.x86_64.rpm

BuildRequires:  cpio
BuildRequires:  rpm

# Runtime requirements declared by the upstream Fedora RPM packaging.
Requires:       glibc
Requires:       openssl-libs
Requires:       ca-certificates
Requires:       json-c
Requires:       fcitx5
Requires:       fcitx5-qt-libfcitx5qt6widgets
Requires:       libime
Requires:       qt6-qtbase
Requires:       qt6-qtsvg
Requires:       qt6-qtwebengine
Requires:       layer-shell-qt
Requires:       bubblewrap
Requires:       util-linux
Requires:       python3
Requires:       python3-fonttools
Requires:       python3-pillow
Requires:       fontconfig
Requires:       libwayland-client
Requires:       pipewire-utils
Requires:       /usr/bin/ffmpeg
Requires:       /usr/bin/opencc
Requires:       wl-clipboard
Requires:       libnotify
Requires:       polkit

%description
WeTypeX adapter for Fcitx5. The proprietary WeTypeX runtime is not bundled;
install it separately using the upstream setup command and accept its license.

%prep
%setup -q -c -T

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
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    for d in /usr/share/icons/*; do
        [ -d "$d" ] && gtk-update-icon-cache -q "$d" 2>/dev/null || :
    done
fi
echo "WeTypeX runtime is separate. Run: fcitx5-wetypex-setup --download --accept-upstream-license"

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files -f %{_builddir}/%{name}-filelist
