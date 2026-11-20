## Diagnostic only: probes network egress from the COPR binary build
## chroot. Added to settle whether fetch failures in %prep are the
## builder's firewall or the spec's fault. Removed after use.
%global debug_package %{nil
Name:           nettest
Version:        1
Release:        1%{?dist
Summary:        COPR chroot network probe (diagnostic, never install)
License:        MIT
ExclusiveArch:  x86_64
BuildRequires:  curl
BuildRequires:  glibc-common
%description
Diagnostic package: probes network access from the build chroot.
%prep
echo "PROBE1 getent hosts mirrors.fedoraproject.org:"
getent ahostsv4 mirrors.fedoraproject.org | head -2 || echo "PROBE1 FAIL (no resolver)"
echo "PROBE2 curl https://mirrors.fedoraproject.org (DNS+TLS):"
curl -sS -o /dev/null -w 'PROBE2 http=%{http_code}\n' --max-time 10 'https://mirrors.fedoraproject.org/' || echo "PROBE2 FAIL"
echo "PROBE3 curl https://1.1.1.1 (IP literal, no DNS):"
curl -sS -o /dev/null -w 'PROBE3 http=%{http_code}\n' --max-time 10 'https://1.1.1.1/' || echo "PROBE3 FAIL"
echo "PROBE4 curl https://qqdl.gtimg.cn bare QQ rpm:"
curl -sS -o /dev/null -w 'PROBE4 http=%{http_code}\n' --max-time 10 -r 0-255 'https://qqdl.gtimg.cn/qqfile/QQNTV2/9.9.37/release/816b3c79/QQ_3.2.35_261103_x86_64_01.rpm' || echo "PROBE4 FAIL"
echo "PROBE done"
%build
:
%install
mkdir -p %{buildroot}%{_bindir
printf '#!/bin/sh\ntrue\n' > %{buildroot}%{_bindir}/nettest
chmod +x %{buildroot}%{_bindir}/nettest
%files
%{_bindir}/nettest
