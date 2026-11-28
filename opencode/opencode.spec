%global debug_package %{nil}
%global __os_install_post %{nil}
# opencode ships a single dynamically linked executable (libc only) in its
# release tarball; rpm's automatic dependency generation resolves the host
# sonames correctly, so no filter is needed.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag v<version>, asset opencode-linux-x64.tar.gz).
Name:           opencode
Version:        1.19.6
Release:        1%{?dist}
Summary:        The AI coding agent built for the terminal
License:        MIT
URL:            https://opencode.ai/
Source0:        https://github.com/sst/opencode/releases/download/v1.19.6/opencode-linux-x64.tar.gz

ExclusiveArch:  x86_64
BuildRequires:  coreutils
BuildRequires:  gzip
BuildRequires:  tar

%description
opencode is an open source AI coding agent built for the terminal by SST.
It supports 75+ LLM providers, an LSP-aware agent loop and a client/server
split for remote use. This package installs the official upstream Linux
x64 binary byte-for-byte, unmodified.

%prep
%setup -q -c

%build
:

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 opencode %{buildroot}%{_bindir}/opencode

%check
test -x %{buildroot}%{_bindir}/opencode

%files
%{_bindir}/opencode

%changelog
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 1.19.6-1
- Initial package: official opencode-linux-x64 release binary
