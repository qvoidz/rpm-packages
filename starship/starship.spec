%global debug_package %{nil}
%global __os_install_post %{nil}
# Starship's static musl binary from GitHub releases.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag v<version>, asset
# starship-x86_64-unknown-linux-musl.tar.gz).
Name:           starship
Version:        1.27.0
Release:        1%{?dist}
Summary:        The minimal, blazing-fast, and infinitely customizable prompt
License:        MIT
URL:            https://starship.rs/
Source0:        https://github.com/starship/starship/releases/download/v1.27.0/starship-x86_64-unknown-linux-musl.tar.gz

ExclusiveArch:  x86_64
BuildRequires:  coreutils
BuildRequires:  tar
BuildRequires:  gzip

Requires:       fontconfig

%description
Starship is a cross-shell prompt: fast, customizable and written in
Rust. The binary shipped here is the official static musl build from
GitHub releases, byte-for-byte unmodified. After installing, follow
https://starship.rs to hook it into your shell (one line of init code).

%prep
%setup -q -c

%build
:

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 starship %{buildroot}%{_bindir}/starship

%files
%{_bindir}/starship

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.27.0-1
- Initial package: official static musl build
