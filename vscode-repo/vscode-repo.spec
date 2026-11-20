%global debug_package %{nil}
Name:           vscode-repo
Version:        1.0
Release:        1%{?dist}
Summary:        Yum/DNF repository definition for Visual Studio Code
License:        MIT
URL:            https://packages.microsoft.com/yumrepos/vscode/
BuildArch:      noarch

%description
Installs the official Visual Studio Code yum repository definition into
/etc/yum.repos.d/, so that `sudo dnf install code` works directly. The
packages themselves come from Microsoft's repository and are signed
with Microsoft's GPG key.

%install
mkdir -p %{buildroot}%{_sysconfdir}/yum.repos.d
cat > %{buildroot}%{_sysconfdir}/yum.repos.d/vscode.repo <<'EOF'
[vscode]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF

%files
%config(noreplace) %{_sysconfdir}/yum.repos.d/vscode.repo

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.0-1
- Initial package: official Visual Studio Code yum repo definition
