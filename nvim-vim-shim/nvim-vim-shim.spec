%global debug_package %{nil}
%global __os_install_post %{nil}

Name:           nvim-vim-shim
Version:        1.0
Release:        1%{?dist}
Summary:        Launch Neovim when the vim and vimdiff commands are used
License:        MIT
URL:            https://neovim.io/
BuildArch:      noarch

Requires:       neovim
# vim-enhanced owns /usr/bin/vim and /usr/bin/vimdiff as real files; the
# shim must not be co-installed with it (switch back with dnf remove/swap).
Conflicts:      vim-enhanced

%description
Muscle memory is hard to manage: scripts, sudo sessions, and editors
keep invoking `vim`, but Neovim is the editor you actually want. This
package installs two tiny shell shims, /usr/bin/vim and /usr/bin/vimdiff,
that exec Neovim (diff mode via `nvim -d`), so `vim` starts Neovim for
every user and with or without sudo.

The real Vim is deliberately not replaced or shadowed: remove this
package (or swap it) if you want vim-enhanced back.

%build
:

%install
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/vim <<'SHIM'
#!/bin/sh
# nvim-vim-shim: hand the vim invocation over to Neovim.
exec /usr/bin/nvim "$@"
SHIM
chmod 0755 %{buildroot}%{_bindir}/vim

cat > %{buildroot}%{_bindir}/vimdiff <<'SHIM'
#!/bin/sh
# nvim-vim-shim: vimdiff is Neovim's built-in diff mode (nvim -d).
exec /usr/bin/nvim -d "$@"
SHIM
chmod 0755 %{buildroot}%{_bindir}/vimdiff

%files
%{_bindir}/vim
%{_bindir}/vimdiff

%post
cat <<'EOF'

=====================================================================
 nvim-vim-shim installed: vim and vimdiff now launch Neovim.
 Verify with:  vim --version | head -1   (prints NVIM v...)

 Want real Vim back?
   sudo dnf remove nvim-vim-shim && sudo dnf install vim-enhanced
=====================================================================

EOF

%changelog
* Sun Nov 22 2026 COPR Builder <copr@example.invalid> - 1.0-1
- Initial package: /usr/bin/vim and /usr/bin/vimdiff shell shims
  that exec Neovim, Conflicts with vim-enhanced.
