%global debug_package %{nil}
# Upstream release tags look like v<version>-<upstream_rel>, e.g. v3.0.1.684-9.
# scripts/check-updates.py keeps both globals in sync with the latest tag.
%global upstream_rel 9
# Payload bundles its own copies of libkqueue etc.; keep auto-Provides from
# exposing them as soname provides (would shadow the real Fedora packages).
%global __provides_exclude ^.*$
# libkqueue is bundled in the upstream RPM; it is not a Fedora runtime dependency.
%global __requires_exclude ^libkqueue\\.so\\.0(\\(|$)
ExclusiveArch:  x86_64

Name:           fcitx5-wetypex
Version:        3.0.1.684
# Repack counter (.2) forces an upgrade over the -9 COPR build for the same
# upstream release; check-updates.py drops it on the next upstream tag bump.
Release:        %{upstream_rel}.3%{?dist}
Summary:        WeTypeX input method adapter for Fcitx5
License:        GPL-3.0-or-later
URL:            https://github.com/panxuc/fcitx5-wetypex
Source0:        https://github.com/panxuc/fcitx5-wetypex/releases/download/v%{version}-%{upstream_rel}/fcitx5-wetypex-%{version}-%{upstream_rel}.x86_64.rpm

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

%check
test -x %{buildroot}%{_bindir}/fcitx5-wetypex-setup
find %{buildroot}%{_libdir}/fcitx5 -type f -name '*.so*' -print -quit | grep -q .

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications >/dev/null 2>&1 || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t /usr/share/icons/hicolor >/dev/null 2>&1 || :
fi
cat <<'EOF'

WeTypeX 已安装。请以日常使用输入法的用户身份完成设置：

  1. 准备官方运行时（先阅读并接受上游软件许可）：
     fcitx5-wetypex-setup --download --accept-upstream-license

  2. 检查核心和本地传输：
     fcitx5-wetypex-setup --check --transport

  3. 重启 Fcitx5，让它加载新插件：
     KDE Plasma Wayland：在系统设置的“虚拟键盘”中先选择“无”，再选择 Fcitx 5；
                         也可注销并重新登录。
     X11 或独立启动的 Fcitx5：fcitx5 -r -d

  4. 打开 fcitx5-configtool，将 WeTypeX 加入输入法列表。

离线安装、旧版迁移和其他桌面环境：
https://github.com/panxuc/fcitx5-wetypex/blob/main/docs/installation.md
EOF

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-9.3
- Filter the bundled libkqueue soname from automatic runtime requirements

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-9.2
- Restore upstream %post setup instructions and cache refresh behavior
- Filter auto-Provides so bundled libkqueue.so does not shadow the Fedora package

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-9
- Repackage upstream WeTypeX RPM for COPR
