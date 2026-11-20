#!/usr/bin/env bash
# 逐包实测：安装 → 验证 → 卸载 → 验证清理。
# 在 Fedora x86_64 实机上运行（已 dnf copr enable qvoidz/rpm-packages）：
#   sudo bash scripts/verify-packages.sh            # 测全部包
#   sudo bash scripts/verify-packages.sh linuxqq    # 只测指定包
#
# 失败时 dnf 的完整输出保存在 /tmp/rpm-verify-<包名>-{install,remove}.log，
# 屏幕上会直接打印末尾若干行，方便定位原因。
#
# 注意：全部包的总下载量约 3 GB（wemeet/微信/WorkBuddy/WPS/钉钉的 RPM 都很大；
# linuxqq/网易云安装时还会从腾讯/网易 CDN 额外下载官方载荷，需要国内网络）。
set -u

PACKAGES=(flclash fcitx5-wetypex flyline wechat workbuddy linuxqq wemeet iptvnator
          waydroid-script nerd-fonts-cascadia-code lazyvim zed starship qqmusic
          wps-office dingtalk netease-cloud-music edge-repo vscode-repo)

# 安装后：检查代表性文件是否就位
check_installed() {
    case "$1" in
        flclash)         rpm -ql flclash        | grep -qE 'bin/FlClash' ;;
        fcitx5-wetypex)  rpm -ql fcitx5-wetypex | grep -qE 'bin/|fcitx5' ;;
        flyline)         [ -f /usr/lib64/flyline/libflyline.so ] && [ -f /etc/profile.d/flyline.sh ] ;;
        wechat)          rpm -ql wechat         | grep -qE 'bin/' ;;
        workbuddy)       rpm -ql workbuddy      | grep -qE 'bin/' ;;
        linuxqq)         # 壳包：载荷不进 RPM 数据库，看 %post 的实际产物
                         [ -x /opt/QQ/qq ] && [ -s /var/lib/linuxqq/filelist ] \
                         && [ -f /usr/share/applications/qq.desktop ] ;;
        wemeet)          rpm -ql wemeet         | grep -qE 'bin/' ;;
        iptvnator)       rpm -ql iptvnator      | grep -qE 'bin/' ;;
        waydroid-script) [ -x /usr/bin/waydroid-script ] && [ -d /usr/share/waydroid-script ] ;;
        nerd-fonts-cascadia-code)
                         [ -d /usr/share/fonts/nerd-fonts-cascadia-code ] \
                         && ls /usr/share/fonts/nerd-fonts-cascadia-code/*.ttf >/dev/null 2>&1 ;;
        lazyvim)         [ -x /usr/bin/lazyvim ] ;;
        zed)             [ -e /usr/bin/zed ] ;;
        starship)        [ -x /usr/bin/starship ] ;;
        qqmusic)         [ -f /usr/share/applications/qqmusic.desktop ] ;;
        wps-office)      [ -x /usr/bin/wps ] ;;
        dingtalk)        [ -f /usr/share/applications/com.alibabainc.dingtalk.desktop ] ;;
        netease-cloud-music) # 壳包（网易 CDN 封机房，载荷安装期下载）
                         [ -s /var/lib/netease-cloud-music/filelist ] \
                         && [ -f /usr/share/applications/netease-cloud-music.desktop ] ;;
        edge-repo)       [ -f /etc/yum.repos.d/microsoft-edge.repo ] ;;
        vscode-repo)     [ -f /etc/yum.repos.d/vscode.repo ] ;;
    esac
}

# 卸载后：检查是否清理干净
check_removed() {
    case "$1" in
        linuxqq) # 壳包：载荷不进 RPM 数据库，靠 %postun 按清单删除
            [ ! -e /opt/QQ ] && [ ! -f /var/lib/linuxqq/filelist ] \
                && ! rpm -q linuxqq >/dev/null 2>&1 ;;
        netease-cloud-music)
            ! rpm -q netease-cloud-music >/dev/null 2>&1 \
                && [ ! -f /var/lib/netease-cloud-music/filelist ] ;;
        *) ! rpm -q "$1" >/dev/null 2>&1 ;;
    esac
}

targets=("$@")
[ ${#targets[@]} -eq 0 ] && targets=("${PACKAGES[@]}")

declare -a results
for pkg in "${targets[@]}"; do
    echo ""
    echo "================ $pkg ================"

    printf '[%s] 安装 ... ' "$pkg"
    ilog="/tmp/rpm-verify-$pkg-install.log"
    if dnf install -y "$pkg" >"$ilog" 2>&1 && check_installed "$pkg"; then
        inst=PASS
    else
        inst=FAIL
        echo
        echo "  --- 安装失败，dnf 输出末尾（完整日志: $ilog）---"
        tail -n 15 "$ilog" | sed 's/^/  | /'
        printf '[%s] 安装 ... FAIL\n' "$pkg"
    fi
    [ "$inst" = PASS ] && echo "$inst"

    printf '[%s] 卸载 ... ' "$pkg"
    rlog="/tmp/rpm-verify-$pkg-remove.log"
    if dnf remove -y "$pkg" >"$rlog" 2>&1 && check_removed "$pkg"; then
        rem=PASS
    else
        rem=FAIL
        echo
        echo "  --- 卸载失败，dnf 输出末尾（完整日志: $rlog）---"
        tail -n 15 "$rlog" | sed 's/^/  | /'
        printf '[%s] 卸载 ... FAIL\n' "$pkg"
    fi
    [ "$rem" = PASS ] && echo "$rem"

    # 清掉因依赖被带入、现已无用的包，让每个包的测试互不影响
    dnf autoremove -y >/dev/null 2>&1 || :

    results+=("$pkg install=$inst remove=$rem")
done

echo ""
echo "================ 结果汇总 ================"
printf '%s\n' "${results[@]}"
if printf '%s\n' "${results[@]}" | grep -q FAIL; then
    echo "存在失败项，请检查上面的日志。"
    exit 1
fi
echo "全部通过。"
