%global debug_package %{nil}
# FlClash validates the Core binary against a SHA256 embedded in Helper.
# Disable RPM post-install build processing (especially brp-strip), which
# would modify Core and make the application hang or fail at startup.
%global __os_install_post %{nil}
# The payload may bundle its own copies of common system libraries. rpm's
# automatic generator turns them into soname Provides, shadowing the real
# Fedora providers and making dnf pull this package to satisfy unrelated
# soname requires (observed when installing fcitx5-wetypex). Suppress all
# auto-generated provides; the package's own name provides are intrinsic
# and unaffected.
%global __provides_exclude ^.*$
# rpm's ELF scanner also turns the payload's bundled private libraries
# (libflutter_linux_gtk.so, the plugin libs, ...) into auto Requires that
# Fedora cannot satisfy (e.g. libdartjni's libjvm.so), which would break dnf
# resolution. Suppress them all; the explicit Requires below fully describe
# the real host dependencies (everything else lives inside gtk3's closure).
%global __requires_exclude ^.*$

Name:           FlClash
Version:        0.9.4
Release:        8%{?dist}
Summary:        A modern proxy client based on Clash
License:        GPL-3.0-or-later
URL:            https://github.com/chen08209/FlClash
Source0:        https://github.com/chen08209/FlClash/releases/download/v%{version}/FlClash-%{version}-linux-amd64.rpm

BuildRequires:  cpio
BuildRequires:  rpm
Requires:       gtk3
Requires:       libsecret
# Upstream 0.9.3 additionally pulled libayatana-appindicator-gtk3 (+ido and
# indicator, via its bundled libtray_plugin.so) and the whole Java stack
# (~240 MiB: java-25-openjdk-headless and friends, via libdartjni's NEEDED
# libjvm.so). Both are gone in 0.9.4: upstream dropped the tray plugin
# entirely (verified: no ayatana sonames, no dlopen strings in the 0.9.4
# payload) and libdartjni is an Android-only library never loaded on desktop.
# Suppressing those auto-requires is therefore safe and intentional.
# libflutter_linux_gtk.so renders through libepoxy, which dlopens libEGL at
# runtime instead of linking it, so no auto-require would catch it and EGL is
# NOT inside gtk3's dependency closure. Verified 2026-11-21 against the
# extracted upstream payload: every other NEEDED soname (gtk stack, X11,
# wayland, fontconfig, harfbuzz, epoxy, libstdc++/libgcc via cups-libs) is
# inside gtk3's closure; only EGL/GL is missing. mesa-libEGL pulls the GLVND
# dispatch layer plus the Mesa (software-capable) implementation. On any real
# desktop this is already installed; declaring it only guards minimal systems.
Requires:       mesa-libEGL
# Same-named as upstream's own RPM (Name: FlClash), so upstream releases and
# our rebuilds upgrade in place with no name dance (rpm vercmp: our
# 0.9.4-7 > upstream's 0.9.3+2026110401). The previous lowercase-named
# flclash package is gone from the target systems (confirmed 2026-11-21),
# so no migration Obsoletes is needed anymore.

%description
FlClash is a graphical proxy client based on Clash.

%prep
%setup -q -c -T

%build
:

%install
mkdir -p %{buildroot}
cd %{buildroot}
rpm2cpio %{SOURCE0} | cpio -idm --quiet --no-absolute-filenames
# Rewrite absolute symlinks in the payload to relative ones. Upstream ships
# /usr/bin/FlClash -> /usr/share/FlClash/FlClash, which rpmbuild flags as an
# "absolute symlink" warning; a relative link behaves identically and is the
# Fedora-preferred form. The helper strips the buildroot prefix from the link
# path before computing, so the result is relative in *system* space
# (realpath -m --relative-to would wrongly include the host buildroot prefix).
# The payload's .build-id links are already relative and pass through as-is.
sys_relpath() {
    local from=$1 to=$2
    local -a fa=() ta=() out=()
    local IFS=/
    read -ra fa <<< "${from#/}"
    read -ra ta <<< "${to#/}"
    local i=0
    while [ "$i" -lt "${#fa[@]}" ] && [ "$i" -lt "${#ta[@]}" ] \
          && [ "${fa[$i]}" = "${ta[$i]}" ]; do
        i=$((i+1))
    done
    local k
    for (( k=i; k<${#fa[@]}; k++ )); do out+=(..); done
    for (( k=i; k<${#ta[@]}; k++ )); do out+=("${ta[$k]}"); done
    if [ "${#out[@]}" -eq 0 ]; then echo .; else local IFS=/; echo "${out[*]}"; fi
}
find %{buildroot} -type l | while read -r link; do
    target=$(readlink "$link")
    case "$target" in
        /*)
            sys=${link#%{buildroot}}
            ln -snf "$(sys_relpath "${sys%/*}" "$target")" "$link"
            ;;
    esac
done
find %{buildroot} -mindepth 1 \( -type f -o -type l \) -printf '/%%P\n' | sort > %{_builddir}/%{name}-filelist

%post
update-desktop-database %{_datadir}/applications &> /dev/null || :

%postun
if [ "$1" = 0 ]; then
    systemctl disable --now flclash-helper.service >/dev/null 2>&1 || true
    rm -f /etc/systemd/system/flclash-helper.service
    systemctl daemon-reload >/dev/null 2>&1 || true
fi

%files -f %{_builddir}/%{name}-filelist

%changelog
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 0.9.4-8
- Rewrite the payload's one absolute symlink (/usr/bin/FlClash) to a relative
  link, silencing rpmbuild's "absolute symlink" warning; generic loop covers
  any absolute links future payloads may add
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 0.9.4-7
- Rename the package to FlClash, same as upstream's own RPM, so future
  upstream releases upgrade in place with no name migration; the lowercase
  flclash package has already been removed from the target systems
* Sat Nov 21 2026 COPR Builder <copr@example.invalid> - 0.9.4-6
- Declare mesa-libEGL: libepoxy dlopens libEGL at runtime and EGL is outside
  gtk3's closure; verified against the extracted upstream payload that all
  other host NEEDED sonames are covered by gtk3 + libsecret
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.9.4-5
- Suppress auto-generated requires of bundled private libraries; they used
  to be satisfied by the (now obsoleted) FlClash package's own provides
- Declare the real host dependencies explicitly (gtk3, libsecret)
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.9.4-4
- Obsolete/Provide FlClash: the old differently-named package owns the same
  /usr/share/FlClash paths and blocks installation with file conflicts
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - fix
- Filter auto-generated provides of bundled system libraries
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 0.9.4-2
- Preserve the upstream Core binary byte-for-byte; disable brp-strip processing
- Match upstream libsecret dependency and package scriptlets
