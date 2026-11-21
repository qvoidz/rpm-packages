%global debug_package %{nil}
%global __os_install_post %{nil}
# Starship's static musl binary from GitHub releases.
# scripts/check-updates.py rewrites Version and Source0 from
# releases/latest (tag v<version>, asset
# starship-x86_64-unknown-linux-musl.tar.gz).
Name:           starship
Version:        1.27.0
Release:        2%{?dist}
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

%post
cat <<'EOF'

=====================================================================
 starship 已安装（提示符工具，装完不会自动生效）。启用只需一步：

     echo 'eval "$(starship init bash)"' >> ~/.bashrc

 然后重开终端，提示符立即变成 starship。
 zsh 用户改用 ~/.zshrc + starship init zsh；配置见 https://starship.rs
=====================================================================

EOF

%files
%{_bindir}/starship

%changelog
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 1.27.0-2
- Print enablement instructions from the %%post scriptlet (one
  eval line into ~/.bashrc) instead of leaving users to find the
  upstream quickstart on their own.
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.27.0-1
- Initial package: official static musl build
