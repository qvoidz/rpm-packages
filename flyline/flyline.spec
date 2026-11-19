%global debug_package %{nil}
# Ship the prebuilt loadable unmodified: disable RPM build-side processing
# (brp-strip etc.) which could damage the upstream artifact.
%global __os_install_post %{nil}
# Flyline upstream does not publish RPMs; this package wraps the official
# prebuilt bash loadable from the GitHub release tarball
# libflyline-v<version>-x86_64-unknown-linux-gnu.tar.gz (single file
# libflyline.so.<version>, MIT source / GPL-3.0+ binary when linked to bash).
Name:           flyline
Version:        1.11.0
Release:        1%{?dist}
Summary:        Modern readline replacement for bash, as a loadable builtin
License:        GPL-3.0-or-later
URL:            https://github.com/HalFrgrd/flyline
Source0:        https://github.com/HalFrgrd/flyline/releases/download/v%{version}/libflyline-v%{version}-x86_64-unknown-linux-gnu.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  coreutils
Requires:       bash >= 4.4

%description
Flyline replaces readline with a modern terminal UI: intellisense-style
suggestions, syntax highlighting, fuzzy history search, enhanced tab
completion and mouse support. It ships as a bash loadable builtin
(`enable -f ... flyline`) and runs in the same process as bash.

The package installs /usr/lib64/flyline/libflyline.so and
/etc/profile.d/flyline.sh, which loads flyline automatically in interactive
bash sessions. Set FLYLINE_DISABLE=1 in the environment to skip loading it.
To load it manually instead:

    enable flyline 2>/dev/null || enable -f /usr/lib64/flyline/libflyline.so flyline

%prep
# -c creates the build dir; do NOT pass -T (it would skip unpacking Source0).
%setup -q -c

%build
:

%install
install -D -m 0755 libflyline.so.* %{buildroot}%{_libdir}/flyline/libflyline.so
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cat > %{buildroot}%{_sysconfdir}/profile.d/flyline.sh <<'EOF'
# Flyline - enhanced Bash experience (loaded from the flyline RPM).
# Export FLYLINE_DISABLE=1 to skip loading it.
if [ -n "${BASH_VERSION:-}" ] && [ "${FLYLINE_DISABLE:-0}" != 1 ] && [ -r /usr/lib64/flyline/libflyline.so ]; then
    case $- in
        *i*) enable flyline 2>/dev/null || enable -f /usr/lib64/flyline/libflyline.so flyline 2>/dev/null ;;
    esac
fi
EOF

%files
%{_libdir}/flyline/libflyline.so
%config(noreplace) %{_sysconfdir}/profile.d/flyline.sh

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.11.0-1
- Initial package: wrap the upstream prebuilt bash loadable from the release tarball
