# waydroid_script tracks upstream master (no git tags): Version is the
# commit date (YYYYMMDD) and %global commit pins the exact source archive;
# scripts/check-updates.py rewrites both automatically.
%global commit 4a50dabd97fcb632a608b1421105258862a5b994

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

BuildArch:      noarch
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

%files
%{_bindir}/%{name}
%{_datadir}/%{name}

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 20261114-1
- Initial package: master 4a50dabd, vendor InquirerPy 0.3.4 + pfzy 0.3.4 wheels
