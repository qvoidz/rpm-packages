#!/usr/bin/env bash
# Install/verify/remove each RPM from the enabled COPR repository.
# Run on a disposable Fedora 45 x86_64 system with qvoidz/rpm-packages enabled:
#   sudo bash scripts/verify-packages.sh
#   sudo bash scripts/verify-packages.sh FlClash linuxqq
#
# Existing packages are preserved (reinstalled for verification, never removed).
# Newly installed test packages are removed afterwards. Dependencies are NOT
# autoremove'd: this script must not clean unrelated software from the host.
set -uo pipefail

PACKAGES=(
  FlClash fcitx5-wetypex flyline wechat workbuddy linuxqq wemeet iptvnator
  waydroid-script nerd-fonts-cascadia-code lazyvim zed starship qqmusic
  wps-office dingtalk netease-cloud-music edge-repo vscode-repo
)

is_known_package() {
    local wanted=$1 item
    for item in "${PACKAGES[@]}"; do
        [[ "$item" == "$wanted" ]] && return 0
    done
    return 1
}

has_desktop_entry() {
    local pkg=$1 desktop
    desktop=$(rpm -ql "$pkg" 2>/dev/null |
        grep -E '^/usr/share/applications/[^/]+\.desktop$' | head -n 1 || :)
    [[ -n "$desktop" && -s "$desktop" ]]
}

check_installed() {
    local pkg=$1
    rpm -q "$pkg" >/dev/null 2>&1 || return 1

    case "$pkg" in
        FlClash)
            [[ -x /usr/bin/FlClash ]] || rpm -ql FlClash | grep -qE '^/usr/bin/FlClash$'
            ;;
        fcitx5-wetypex)
            command -v fcitx5-wetypex-setup >/dev/null 2>&1 ||
                rpm -ql fcitx5-wetypex | grep -q 'fcitx5-wetypex'
            ;;
        flyline)
            [[ -s /usr/lib64/flyline/libflyline.so &&
               -s /etc/profile.d/flyline.sh ]]
            ;;
        wechat|workbuddy|wemeet|iptvnator|qqmusic|dingtalk)
            has_desktop_entry "$pkg"
            ;;
        linuxqq)
            [[ -x /opt/QQ/qq ]] &&
            [[ -s /usr/share/applications/qq.desktop ]]
            ;;
        waydroid-script)
            [[ -x /usr/bin/waydroid-script &&
               -f /usr/share/waydroid-script/main.py ]]
            ;;
        nerd-fonts-cascadia-code)
            compgen -G '/usr/share/fonts/nerd-fonts-cascadia-code/*.ttf' >/dev/null
            ;;
        lazyvim)
            [[ -x /usr/bin/lazyvim &&
               -s /usr/share/lazyvim/init.lua ]]
            ;;
        zed)
            [[ -x /usr/bin/zed ]] &&
                { [[ -x /usr/lib64/zed.app/bin/zed ]] ||
                  [[ -x /usr/lib64/zed.app/libexec/zed-editor ]]; }
            ;;
        starship)
            [[ -x /usr/bin/starship ]]
            ;;
        wps-office)
            [[ -x /usr/bin/wps ]]
            ;;
        netease-cloud-music)
            [[ -s /usr/share/applications/netease-cloud-music.desktop &&
               -x /opt/netease/netease-cloud-music/netease-cloud-music.bash ]]
            ;;
        edge-repo)
            [[ -s /etc/yum.repos.d/microsoft-edge.repo ]] &&
                grep -q '^gpgcheck=1$' /etc/yum.repos.d/microsoft-edge.repo
            ;;
        vscode-repo)
            [[ -s /etc/yum.repos.d/vscode.repo ]] &&
                grep -q '^gpgcheck=1$' /etc/yum.repos.d/vscode.repo
            ;;
        *)
            echo "No installation assertion defined for $pkg" >&2
            return 1
            ;;
    esac
}

if [[ $EUID -ne 0 ]]; then
    echo "Run this script as root (sudo)." >&2
    exit 2
fi
if ! command -v dnf >/dev/null || ! command -v rpm >/dev/null; then
    echo "This script requires Fedora with dnf and rpm." >&2
    exit 2
fi

targets=("$@")
if [[ ${#targets[@]} -eq 0 ]]; then
    targets=("${PACKAGES[@]}")
fi

for pkg in "${targets[@]}"; do
    if ! is_known_package "$pkg"; then
        echo "Unknown package: $pkg" >&2
        echo "Valid packages: ${PACKAGES[*]}" >&2
        exit 2
    fi
done

declare -a results=()
overall=0

for pkg in "${targets[@]}"; do
    echo
    echo "================ $pkg ================"

    was_installed=0
    if rpm -q "$pkg" >/dev/null 2>&1; then
        was_installed=1
    fi

    ilog="/tmp/rpm-verify-$pkg-install.log"
    if [[ $was_installed -eq 1 ]]; then
        echo "Already installed; reinstalling the same repository package for verification."
        install_ok=0
        dnf reinstall -y "$pkg" >"$ilog" 2>&1 || install_ok=$?
    else
        install_ok=0
        dnf install -y "$pkg" >"$ilog" 2>&1 || install_ok=$?
    fi

    if [[ $install_ok -eq 0 ]] && check_installed "$pkg"; then
        # dnf check detects unsatisfied dependencies and package database issues.
        if dnf check >/tmp/rpm-verify-$pkg-deps.log 2>&1; then
            inst=PASS
            echo "Install, payload assertions and dependency check: PASS"
        else
            inst=FAIL
            overall=1
            echo "Dependency check failed:"
            tail -n 20 "/tmp/rpm-verify-$pkg-deps.log" | sed 's/^/  | /'
        fi
    else
        inst=FAIL
        overall=1
        echo "Install or payload assertion failed:"
        tail -n 30 "$ilog" | sed 's/^/  | /'
    fi

    if [[ $was_installed -eq 1 ]]; then
        rem=KEPT
        echo "Package existed before the test; preserving it."
    elif rpm -q "$pkg" >/dev/null 2>&1; then
        rlog="/tmp/rpm-verify-$pkg-remove.log"
        remove_rc=0
        dnf remove -y --setopt=clean_requirements_on_remove=False "$pkg" >"$rlog" 2>&1 || remove_rc=$?
        if [[ $remove_rc -eq 0 ]] && ! rpm -q "$pkg" >/dev/null 2>&1; then
            rem=PASS
            echo "Package removal: PASS (dependencies left untouched)"
        else
            rem=FAIL
            overall=1
            echo "Package removal failed:"
            tail -n 20 "$rlog" | sed 's/^/  | /'
        fi
    else
        rem=NOT_INSTALLED
        echo "Package was not installed; no removal needed."
    fi

    results+=("$pkg install=$inst remove=$rem")
done

echo
echo "================ Result summary ================"
printf '%s\n' "${results[@]}"
if [[ $overall -ne 0 ]]; then
    echo "One or more checks failed. See /tmp/rpm-verify-*.log"
    exit 1
fi
echo "All selected package checks passed."
