# waydroid_script tracks upstream master (no git tags): Version is the
# commit date (YYYYMMDD) and the pinned commit hash variable below is
# rewritten automatically by scripts/check-updates.py.
# NOTE: the comment above must not contain rpm macro syntax verbatim.
%global commit 4a50dabd97fcb632a608b1421105258862a5b994

# The bundle carries Android ARM ELF helpers under bin/ (resetprop etc.),
# so this cannot be noarch; disable build-side binary processing so
# brp-strip does not touch the foreign-arch ELFs (and disable the debug
# package, whose source list would be empty without brp-strip).
%global __os_install_post %{nil}
%global debug_package %{nil}
# rpm's dependency generator also scans the Android ARM ELF helpers under
# bin/ and emits their bionic sonames (libc.so, libm.so, libdl.so,
# liblog.so) as requirements; no Fedora package provides them (they only
# exist inside the Android container), so filter them out.
%global __requires_exclude ^lib(c|m|dl|log)\\.so(\\(\\)\\(64bit\\))?$

# InquirerPy and pfzy are not packaged in Fedora; they are vendored from
# pinned PyPI wheels into the package directory and put on PYTHONPATH by
# the launcher. prompt-toolkit (their dependency) comes from Fedora.
Name:           waydroid-script
Version:        20261114
Release:        1%{?dist}
Summary:        Script to install GApps / Magisk / libhoudini and more into Waydroid
License:        GPL-3.0-or-later AND MIT
URL:            https://github.com/casualsnek/waydroid_script
Source0:        https://github.com/casualsnek/waydroid_script/archive/%{commit}/waydroid_script-%{commit}.tar.gz
Source1:        https://files.pythonhosted.org/packages/ce/ff/3b59672c47c6284e8005b42e84ceba13864aa0f39f067c973d1af02f5d91/InquirerPy-0.3.4-py3-none-any.whl
Source2:        https://files.pythonhosted.org/packages/8c/d7/8ff98376b1acc4503253b685ea09981697385ce344d4e3935c2af49e044d/pfzy-0.3.4-py3-none-any.whl

ExclusiveArch:  x86_64
BuildRequires:  python3
Requires:       waydroid
Requires:       python3-requests
Requires:       python3-tqdm
Requires:       python3-prompt-toolkit

%description
waydroid_script automates Waydroid tweaks that are otherwise manual:
installing OpenGApps / MindTheGapps / MicroG, Magisk, libhoudini /
libndk (x86_64 on ARM translation), Widevine DRM, smart dock, hiding the
status bar, and registering a certified Android ID.

Run it with: sudo waydroid-script

%prep
%setup -q -n waydroid_script-%{commit}

%build
:

%install
pkgdir=%{buildroot}%{_datadir}/%{name}
mkdir -p "$pkgdir" %{buildroot}%{_bindir}
cp -a main.py requirements.txt assets bin stuff tools "$pkgdir"/
python3 -m zipfile -e %{SOURCE1} "$pkgdir"/vendor/
python3 -m zipfile -e %{SOURCE2} "$pkgdir"/vendor/
cat > %{buildroot}%{_bindir}/%{name} <<'LAUNCHER'
#!/bin/sh
# Run waydroid_script from its own directory with the vendored PyPI deps.
export PYTHONPATH="/usr/share/waydroid-script/vendor${PYTHONPATH:+:$PYTHONPATH}"
exec /usr/bin/python3 /usr/share/waydroid-script/main.py "$@"
LAUNCHER
chmod 755 %{buildroot}%{_bindir}/%{name}

%check
test -x %{buildroot}%{_bindir}/%{name}
test -s %{buildroot}%{_datadir}/%{name}/main.py
test -s %{buildroot}%{_datadir}/%{name}/vendor/InquirerPy/__init__.py
test -s %{buildroot}%{_datadir}/%{name}/vendor/pfzy/__init__.py

%files
%{_bindir}/%{name}
%{_datadir}/%{name}

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 20261114-1
- Initial package: master 4a50dabd, vendor InquirerPy 0.3.4 + pfzy 0.3.4 wheels
