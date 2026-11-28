%global debug_package %{nil}
%global __os_install_post %{nil}
# Codex ships a single static musl binary (static-pie, stripped); it has
# no runtime library dependencies at all, so no Requires are declared.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag rust-v<version>, asset
# codex-x86_64-unknown-linux-musl.tar.gz).
Name:           codex
Version:        0.172.0
Release:        1%{?dist}
Summary:        Codex CLI - OpenAI's coding agent for the terminal
License:        Apache-2.0
URL:            https://developers.openai.com/codex/
Source0:        https://github.com/openai/codex/releases/download/rust-v0.172.0/codex-x86_64-unknown-linux-musl.tar.gz

ExclusiveArch:  x86_64
BuildRequires:  coreutils
BuildRequires:  gzip
BuildRequires:  tar

%description
Codex is OpenAI's open source coding agent for the terminal: it reads,
edits and runs code in your repo, and can be driven interactively or
non-interactively. This package installs the official upstream x86_64
musl binary byte-for-byte, unmodified.

%prep
%setup -q -c

%build
:

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 codex-x86_64-unknown-linux-musl %{buildroot}%{_bindir}/codex

%check
test -x %{buildroot}%{_bindir}/codex

%files
%{_bindir}/codex

%changelog
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 0.172.0-1
- Initial package: official codex x86_64 musl binary
