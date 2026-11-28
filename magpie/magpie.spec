%global debug_package %{nil}
%global __os_install_post %{nil}
# Magpie publishes two raw ELF binaries per release: the desktop app
# (Tauri, dynamically linked against the system's gtk3 / webkit2gtk-4.1)
# and the CLI (static Go). rpm's automatic dependency generation resolves
# the desktop binary's host sonames correctly, so no filter is needed.
# scripts/check-updates.py rewrites Version and both Source URLs from
# releases/latest of yetone/magpie-releases (tag v<version>, assets
# magpie-linux-amd64 and magpie-cli-linux-amd64; both are required).
Name:           magpie
Version:        0.1.4989
Release:        1%{?dist}
Summary:        Magpie - one local gateway for every AI coding agent
License:        MIT
URL:            https://usemagpie.ai/
Source0:        https://github.com/yetone/magpie-releases/releases/download/v0.1.4989/magpie-linux-amd64
Source1:        https://github.com/yetone/magpie-releases/releases/download/v0.1.4989/magpie-cli-linux-amd64

ExclusiveArch:  x86_64
BuildRequires:  coreutils

# desktop-file-utils owns the applications directory the desktop file
# lands in, so uninstall leaves no orphaned directories.
Requires:       desktop-file-utils

%description
Magpie runs a local gateway (127.0.0.1:3425, OpenAI / Anthropic / Gemini
protocol compatible) that lets every AI coding agent - Claude Code,
Codex, Gemini CLI, opencode, pi, Goose and more - share the same model
providers, subscriptions and accounts, with routing, failover, usage
accounting and local secret redaction. This package ships the official
upstream desktop binary as /usr/bin/magpie and the headless CLI as
/usr/bin/magpie-cli, byte-for-byte unmodified.

%prep
echo "Source0/Source1 are the official magpie desktop and CLI binaries."

%build
:

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/magpie
install -m 0755 %{SOURCE1} %{buildroot}%{_bindir}/magpie-cli
# Upstream publishes no Linux desktop file; ship a minimal one so the
# gateway app can be started from the application menu.
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/magpie.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Magpie
GenericName=AI Agent Gateway
Comment=One gateway for every AI coding agent
Exec=/usr/bin/magpie
Terminal=false
Categories=Development;
StartupNotify=false
EOF

%check
test -x %{buildroot}%{_bindir}/magpie
test -x %{buildroot}%{_bindir}/magpie-cli
test -f %{buildroot}%{_datadir}/applications/magpie.desktop

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%files
%{_bindir}/magpie
%{_bindir}/magpie-cli
%{_datadir}/applications/magpie.desktop

%changelog
* Sat Nov 28 2026 COPR Builder <copr@example.invalid> - 0.1.4989-1
- Initial package: official desktop and CLI binaries plus a minimal
  desktop entry (upstream publishes no Linux .desktop file)
