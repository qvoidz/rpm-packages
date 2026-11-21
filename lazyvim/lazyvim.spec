%global debug_package %{nil}
# The starter template tracks upstream main (no tags of its own); the
# package Version follows the LazyVim/LazyVim release tag and
# %%global starter_commit pins the LazyVim/starter archive, both rewritten
# automatically by scripts/check-updates.py.
%global starter_commit 803bc181d7c0d6d5eeba9274d9be49b287294d99
Name:           lazyvim
Version:        16.0.2
Release:        2%{?dist}
Summary:        LazyVim - Neovim config distribution with the official starter template
License:        Apache-2.0
URL:            https://www.lazyvim.org/
Source0:        https://github.com/LazyVim/starter/archive/%{starter_commit}/starter-%{starter_commit}.tar.gz

BuildArch:      noarch
BuildRequires:  coreutils

Requires:       neovim
Requires:       git
Recommends:     ripgrep
Recommends:     fd-find
Recommends:     gcc

%description
LazyVim is a Neovim setup powered by lazy.nvim, shipped here as the
official LazyVim/starter template. Running the provided `lazyvim`
command bootstraps a user config the first time (copying the template
to ~/.config/nvim) and then simply launches Neovim. Plugins are
downloaded and managed by Neovim itself at first start, exactly like a
manual LazyVim installation.

%prep
%setup -q -n starter-%{starter_commit}

%build
:

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a init.lua lua stylua.toml .neoconf.json %{buildroot}%{_datadir}/%{name}/
install -m 0644 LICENSE %{buildroot}%{_datadir}/%{name}/LICENSE

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'WRAPPER'
#!/bin/sh
# LazyVim starter bootstrap: seed the user config on first run, then
# hand over to Neovim.
cfg="$HOME/.config/nvim"
if [ ! -e "$cfg/init.lua" ]; then
    mkdir -p "$HOME/.config"
    cp -a /usr/share/lazyvim/. "$cfg/"
    echo "lazyvim: starter template installed to $cfg"
fi
exec nvim "$@"
WRAPPER
chmod 0755 %{buildroot}%{_bindir}/%{name}

%post
cat <<'EOF'

=====================================================================
 LazyVim 已安装。终端里运行 lazyvim 命令即可启动：

     lazyvim

 首次运行会把官方 starter 模板铺到 ~/.config/nvim（你已有自己的
 Neovim 配置则原样保留、不覆盖），插件由 Neovim 首次启动时自动下载。
 想直接敲 nvim 也进 LazyVim，可在 ~/.bashrc 里加一行：

     alias nvim=lazyvim
=====================================================================

EOF

%files
%{_datadir}/%{name}
%{_bindir}/%{name}

%changelog
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 16.0.2-2
- Print usage instructions from the %%post scriptlet: run the lazyvim
  command, first run seeds ~/.config/nvim, and an optional
  alias nvim=lazyvim one-liner.
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 16.0.2-1
- Initial package: official starter template pinned at 803bc181
