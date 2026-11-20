%global debug_package %{nil}
# NetEase's download CDN (d1.music.126.net) rejects datacenter IPs, so no
# build machine can fetch the payload - the same situation as linuxqq.
# This is a shell package: %post downloads the official .deb on the user's
# machine at install time, extracts it in place (ar + tar, no rebuild) and
# records a file list in /var/lib/netease-cloud-music for clean upgrades
# (stale-file diff) and uninstall. The upstream client has been frozen at
# 1.2.1 since 2019; scripts/check-updates.py parses the versioned URL from
# the official download page and rewrites Version + netease_deb_url.
%global netease_deb_url https://d1.music.126.net/dmusic/netease-cloud-music_1.2.1_amd64_ubuntu_20190428.deb

Name:           netease-cloud-music
Version:        1.2.1
Release:        1%{?dist}
Summary:        NetEase Cloud Music (网易云音乐) desktop client for Linux
License:        LicenseRef-NetEase-CloudMusic-Software-License
URL:            https://music.163.com/

BuildArch:      noarch

# Tools used by the install-time downloader in %post.
Requires:       binutils
Requires:       curl
Requires:       tar
Requires:       xz

%description
NetEase Cloud Music (网易云音乐) desktop client for Linux, distributed
by NetEase. NetEase's CDN refuses datacenter IPs, so - like flatpak's
extra-data - the payload is downloaded on your machine during package
installation and extracted in place. The file list recorded in
/var/lib/netease-cloud-music/filelist guarantees clean upgrades and
uninstalls.

%pre
# Nothing to clean: on upgrade %post diffs the old and new file lists and
# removes only files dropped by the new upstream version, so a failed
# download never destroys a working installation.

%post
tmpdir=$(mktemp -d /var/tmp/netease-cloud-music-XXXXXX) || exit 1
trap 'rm -rf "$tmpdir"' EXIT

echo "netease-cloud-music: downloading %{netease_deb_url} ..."
curl -fsSL --retry 5 --retry-delay 3 -o "$tmpdir/ncm.deb" '%{netease_deb_url}' \
    || { echo "netease-cloud-music: download failed; check your network and run: dnf reinstall netease-cloud-music" >&2; exit 1; }
test -s "$tmpdir/ncm.deb" || { echo "netease-cloud-music: empty download" >&2; exit 1; }

# List of non-directory payload paths, relative to /.
list_payload() {
    (cd "$tmpdir" && ar p ncm.deb data.tar.xz \
        | tar tJf - | sed 's|^\./||' | grep -v '/$' | sort)
}

mkdir -p /var/lib/netease-cloud-music

# On upgrade, remove payload files that the new upstream version no longer
# ships (old file list minus new list), then extract over the old files.
if [ -f /var/lib/netease-cloud-music/filelist ]; then
    sort /var/lib/netease-cloud-music/filelist > "$tmpdir/old.list"
    list_payload > "$tmpdir/new.list" 2>/dev/null || cp "$tmpdir/old.list" "$tmpdir/new.list"
    comm -23 "$tmpdir/old.list" "$tmpdir/new.list" \
        | while IFS= read -r f; do
              [ -n "$f" ] && rm -f "/$f"
          done
fi

# Extract the deb's data archive directly into /.
cd "$tmpdir" && ar p ncm.deb data.tar.xz | tar xJ -C /

list_payload > /var/lib/netease-cloud-music/filelist.new \
    && mv /var/lib/netease-cloud-music/filelist.new /var/lib/netease-cloud-music/filelist

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lib/netease-cloud-music/filelist ]; then
        while IFS= read -r f; do
            [ -n "$f" ] && rm -f "/$f"
        done < /var/lib/netease-cloud-music/filelist
        rm -f /var/lib/netease-cloud-music/filelist
    fi
    rmdir /var/lib/netease-cloud-music 2>/dev/null || :
fi

%files
%ghost %dir /var/lib/netease-cloud-music
%ghost /var/lib/netease-cloud-music/filelist

%changelog
* Fri Nov 20 2026 COPR Builder <copr@example.invalid> - 1.2.1-1
- Initial package: install-time downloader for the official NetEase .deb
