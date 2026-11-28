%global debug_package %{nil}
%global __os_install_post %{nil}
# Anthropic ships Claude Code as a native single executable (a Node.js
# single-executable-application bundle, dynamically linked against glibc
# only) from its versioned GCS release channel. rpm's automatic dependency
# generation resolves the host sonames correctly, so no filter is needed.
# The URL layout is <channel>/<version>/linux-x64/claude; the "stable"
# pointer file
# https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/stable
# names the version the official native installer ships, and
# scripts/check-updates.py rewrites both Version and Source0 from it.
Name:           claude-code
Version:        2.1.326
Release:        1%{?dist}
Summary:        Claude Code - Anthropic's agentic coding tool for the terminal
License:        LicenseRef-Anthropic-Claude-Code-Commercial-Terms
URL:            https://code.claude.com/
Source0:        https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/2.1.326/linux-x64/claude

ExclusiveArch:  x86_64
BuildRequires:  coreutils

%description
Claude Code is Anthropic's agentic coding tool that lives in the terminal:
it reads your codebase, edits files, runs commands and drives multi-step
engineering work. This package installs the official native Linux x64
build from Anthropic's release channel byte-for-byte, unmodified. It
bundles its own runtime, so no Node.js installation is required.

%prep
echo "Source0 tracks the native Claude Code binary from Anthropic's GCS release channel."

%build
:

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 %{_sourcedir}/claude %{buildroot}%{_bindir}/claude

%check
test -x %{buildroot}%{_bindir}/claude

%files
%{_bindir}/claude

%changelog
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 2.1.326-1
- Initial package: native Claude Code binary from the stable channel
