#!/usr/bin/env bash
# 逐包实测：安装 → 验证 → 卸载 → 验证清理。
# 在 Fedora x86_64 实机上运行（已 dnf copr enable qvoidz/rpm-packages）：
#   sudo bash scripts/verify-packages.sh            # 测全部 9 个包
#   sudo bash scripts/verify-packages.sh linuxqq    # 只测指定包
#
# 注意：总下载量约 1 GB（微信/WorkBuddy/iptvnator/wemeet 的 RPM 都很大，
# linuxqq 安装时还会额外下载约 190 MB 官方载荷，需要能访问腾讯的网络）。
set -u

PACKAGES=(flclash fcitx5-wetypex flyline wechat workbuddy linuxqq wemeet iptvnator waydroid-script)

# 安装后：检查代表性文件是否就位
check_installed() {
    case "$1" in
        flclash)         rpm -ql flclash        | grep -qE 'bin/FlClash' ;;
        fcitx5-wetypex)  rpm -ql fcitx5-wetypex | grep -qE 'bin/|fcitx5' ;;
        flyline)         [ -f /usr/lib64/flyline/libflyline.so ] && [ -f /etc/profile.d/flyline.sh ] ;;
        wechat)          rpm -ql wechat         | grep -qE 'bin/' ;;
        workbuddy)       rpm -ql workbuddy      | grep -qE 'bin/' ;;
        linuxqq)         [ -x /opt/QQ/qq ] && [ -s /var/lib/linuxqq/filelist ] \
                         && [ -f /usr/share/applications/qq.desktop ] ;;
        wemeet)          rpm -ql wemeet         | grep -qE 'bin/' ;;
        iptvnator)       rpm -ql iptvnator      | grep -qE 'bin/' ;;
        waydroid-script) [ -x /usr/bin/waydroid-script ] && [ -d /usr/share/waydroid-script ] ;;
    esac
}

# 卸载后：检查是否清理干净
check_removed() {
    case "$1" in
        linuxqq) # 壳包：载荷不进 RPM 数据库，靠 %postun 按清单删除
            [ ! -e /opt/QQ ] && [ ! -f /var/lib/linuxqq/filelist ] \
                && ! rpm -q linuxqq >/dev/null 2>&1 ;;
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
    if dnf install -y "$pkg" >/dev/null 2>&1 && check_installed "$pkg"; then
        inst=PASS
    else
        inst=FAIL
    fi
    echo "$inst"

    printf '[%s] 卸载 ... ' "$pkg"
    if dnf remove -y "$pkg" >/dev/null 2>&1 && check_removed "$pkg"; then
        rem=PASS
    else
        rem=FAIL
    fi
    echo "$rem"

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
