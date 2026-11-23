%global debug_package %{nil}
# Upstream release tags look like v<version>-<upstream_rel>, e.g. v3.0.1.684-9.
# scripts/check-updates.py keeps both globals in sync with the latest tag.
%global upstream_rel 10
# Payload bundles its own copies of libkqueue etc.; keep auto-Provides from
# exposing them as soname provides (would shadow the real Fedora packages).
%global __provides_exclude ^.*$
# libkqueue is bundled in the upstream RPM; it is not a Fedora runtime dependency.
%global __requires_exclude ^.*$
ExclusiveArch:  x86_64

Name:           fcitx5-wetypex
Version:        3.0.1.684
# Repack counter (.2) forces an upgrade over the -9 COPR build for the same
# upstream release; check-updates.py drops it on the next upstream tag bump.
Release:        %{upstream_rel}%{?dist}
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

# Explicit host dependencies (auto-generated from Fedora 45 repodata; bundled private sonames excluded)
Requires: bubblewrap
Requires: ca-certificates
Requires: fcitx5
Requires: fcitx5-qt-libfcitx5qt6widgets
Requires: fontconfig
Requires: glibc
Requires: json-c
Requires: layer-shell-qt
Requires: ld-linux-x86-64.so.2()(64bit)
Requires: libFcitx5Config.so.6()(64bit)
Requires: libFcitx5Core.so.7()(64bit)
Requires: libFcitx5Qt6WidgetsAddons.so.2()(64bit)
Requires: libFcitx5Utils.so.2()(64bit)
Requires: libGLX.so.0()(64bit)
Requires: libIMECore.so.0()(64bit)
Requires: libIMEPinyin.so.0()(64bit)
Requires: libLayerShellQtInterface.so.6()(64bit)
Requires: libOpenGL.so.0()(64bit)
Requires: libQt6Core.so.6()(64bit)
Requires: libQt6DBus.so.6()(64bit)
Requires: libQt6Gui.so.6()(64bit)
Requires: libQt6Network.so.6()(64bit)
Requires: libQt6OpenGL.so.6()(64bit)
Requires: libQt6Positioning.so.6()(64bit)
Requires: libQt6PrintSupport.so.6()(64bit)
Requires: libQt6Qml.so.6()(64bit)
Requires: libQt6QmlMeta.so.6()(64bit)
Requires: libQt6QmlModels.so.6()(64bit)
Requires: libQt6QmlWorkerScript.so.6()(64bit)
Requires: libQt6Quick.so.6()(64bit)
Requires: libQt6Svg.so.6()(64bit)
Requires: libQt6WebChannel.so.6()(64bit)
Requires: libQt6WebEngineCore.so.6()(64bit)
Requires: libQt6WebEngineWidgets.so.6()(64bit)
Requires: libQt6Widgets.so.6()(64bit)
Requires: libc++.so.1()(64bit)
Requires: libc++abi.so.1()(64bit)
Requires: libc.so.6()(64bit)
Requires: libcrypto.so.3()(64bit)
Requires: libfontconfig.so.1()(64bit)
Requires: libfreetype.so.6()(64bit)
Requires: libgcc_s.so.1()(64bit)
Requires: libime
Requires: libjson-c.so.5()(64bit)
Requires: libm.so.6()(64bit)
Requires: libnotify
Requires: libssl.so.3()(64bit)
Requires: libstdc++.so.6()(64bit)
Requires: libwayland-client
Requires: libwayland-client.so.0()(64bit)
Requires: openssl-libs
Requires: pipewire-utils
Requires: polkit
Requires: python3
Requires: python3-fonttools
Requires: python3-pillow
Requires: qt6-qtbase
Requires: qt6-qtsvg
Requires: qt6-qtwebengine
Requires: rtld(GNU_HASH)
Requires: util-linux
Requires: wl-clipboard


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
{
  find %{buildroot} -mindepth 1 -type d \
    ! -path '%{buildroot}/usr/bin' ! -path '%{buildroot}/usr/sbin' \
    ! -path '%{buildroot}/usr/lib' ! -path '%{buildroot}/usr/lib64' \
    -printf '/%%P\n' | awk '{ if ($0 ~ /[[:space:]]/) print "%%dir \"" $0 "\""; else print "%%dir " $0 }'
  find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n'
} | sort > %{_builddir}/%{name}-filelist

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
* Mon Nov 23 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-10
- Update to upstream v3.0.1.684-10
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-
- Own every payload directory in the file list (except /usr/lib and /usr/lib64, which filesystem ships read-only 0555) so uninstall leaves no orphaned empty directories behind
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-upstream_rel.4
- Filter all bundled sonames that no Fedora package provides; keep every
  provider-backed host dependency (regression-tested against Fedora 45 repodata)
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-9.3
- Filter the bundled libkqueue soname from automatic runtime requirements

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-9.2
- Restore upstream %post setup instructions and cache refresh behavior
- Filter auto-Provides so bundled libkqueue.so does not shadow the Fedora package

* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.0.1.684-9
- Repackage upstream WeTypeX RPM for COPR
