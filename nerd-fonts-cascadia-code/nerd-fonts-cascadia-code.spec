%global debug_package %{nil}
%global __os_install_post %{nil}
# Pre-patched Cascadia Code Nerd Font from ryanoasis/nerd-fonts releases.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag v<version>, asset CascadiaCode.zip).
Name:           nerd-fonts-cascadia-code
Version:        3.5.1
Release:        1%{?dist}
Summary:        Cascadia Code Nerd Font - developer font with extra glyphs
License:        OFL-1.1 AND MIT
URL:            https://github.com/ryanoasis/nerd-fonts
Source0:        https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/CascadiaCode.zip

BuildArch:      noarch
BuildRequires:  coreutils
BuildRequires:  unzip

%description
Nerd Fonts patched variant of Microsoft's Cascadia Code monospaced font,
including hundreds of extra glyphs (icons, powerline symbols, font
ligatures). The TTF files are shipped unmodified from the upstream
CascadiaCode.zip release asset.

%prep
mkdir -p CascadiaCode
cd CascadiaCode
unzip -q %{SOURCE0}

%build
:

%install
mkdir -p %{buildroot}%{_datadir}/fonts/%{name}
find . -name '*.ttf' -exec install -m 0644 '{}' \
    %{buildroot}%{_datadir}/fonts/%{name}/ ';'

%post
if command -v fc-cache >/dev/null 2>&1; then
    fc-cache -f %{_datadir}/fonts/%{name} >/dev/null || :
fi

%postun
if command -v fc-cache >/dev/null 2>&1; then
    fc-cache -f >/dev/null || :
fi

%files
%{_datadir}/fonts/%{name}

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 3.5.1-1
- Initial package: Nerd Fonts patched Cascadia Code 3.5.1
