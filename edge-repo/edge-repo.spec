%global debug_package %{nil}
Name:           edge-repo
Version:        1.0
Release:        1%{?dist}
Summary:        Yum/DNF repository definition for Microsoft Edge browser
License:        MIT
URL:            https://packages.microsoft.com/yumrepos/edge/
BuildArch:      noarch

%description
Installs the official Microsoft Edge yum repository definition into
/etc/yum.repos.d/, so that `sudo dnf install microsoft-edge-stable`
works directly. The packages themselves come from Microsoft's
repository and are signed with Microsoft's GPG key.

%install
mkdir -p %{buildroot}%{_sysconfdir}/yum.repos.d
cat > %{buildroot}%{_sysconfdir}/yum.repos.d/microsoft-edge.repo <<'EOF'
[microsoft-edge]
name=Microsoft Edge
baseurl=https://packages.microsoft.com/yumrepos/edge/
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF

%files
%config(noreplace) %{_sysconfdir}/yum.repos.d/microsoft-edge.repo

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.0-1
- Initial package: official Microsoft Edge yum repo definition
