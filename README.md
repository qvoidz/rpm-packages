# qvoidz RPM 软件包

面向 Fedora x86_64 的 COPR 软件源。核心思路是**原样复用上游 RPM**：载荷用 `rpm2cpio | cpio` 逐字节解包后重新打包，不重新构建、不修改任何二进制。GitHub Actions 每日跟踪上游版本，自动改写 spec 并触发 COPR 构建。

## 软件包

| 软件包 | 说明 |
| --- | --- |
| [微信 WeChat](https://weixin.qq.com/) | 腾讯官方 Linux RPM（无 GitHub release） |
| [WorkBuddy](https://www.workbuddy.cn/) | 腾讯官方 Linux RPM，通过更新接口发现新版本 |
| [FlClash](https://github.com/chen08209/FlClash) | 上游 Linux x86_64 RPM |
| [Fcitx5 WeTypeX](https://github.com/panxuc/fcitx5-wetypex) | 上游 x86_64 RPM |
| [Flyline](https://github.com/HalFrgrd/flyline) | 上游 release 压缩包内的预编译 bash loadable |
| [Linux QQ](https://im.qq.com/linuxqq/) | 安装器壳包（见下文说明） |
| [腾讯会议](https://meeting.tencent.com/) | 官方 x86_64 .deb 重打包为 RPM |
| [iptvnator](https://github.com/4gray/iptvnator) | 上游 GitHub release 提供的 Linux x86_64 RPM |
| [waydroid-script](https://github.com/casualsnek/waydroid_script) | Waydroid 装 GApps/Magisk/libhoudini 的 Python 工具 |

WeTypeX 的专有运行时不在其上游 RPM 内，需按上游说明单独安装并接受许可。

## 安装

```bash
sudo dnf copr enable qvoidz/rpm-packages
sudo dnf install wechat workbuddy flclash fcitx5-wetypex flyline linuxqq wemeet iptvnator waydroid-script
sudo dnf upgrade   # 日常升级
```

## 复用上游 RPM 的原理

COPR 从 spec 构建软件包，本仓库每个目录放一个小的重打包 spec：

1. `Source0` 指向上游 RPM 的 URL（GitHub release 资产、微信的滚动下载地址、WorkBuddy 更新接口返回的地址等），COPR 的 `rpkg` SRPM 构建器自动下载；
2. `%install` 用 `rpm2cpio | cpio -idm` 原样解包并照搬文件清单；所有重打包 spec 都关闭 `debug_package` 和 `__os_install_post`，避免 brp-strip/compress/check-rpaths 修改或拒绝上游二进制中的 `${ORIGIN}` runpath；
3. `%post`/`%postun` 只刷新桌面/图标缓存。

### Linux QQ 的特别处理

腾讯的下载 CDN 拒绝所有机房 IP，任何构建机都拿不到安装包（COPR builder、GitHub runner、Cloudflare Workers 均实测被拒）。因此 linuxqq 是一个壳包：RPM 本体只有几 KB，`%post` 在**用户安装时**从腾讯官方地址下载载荷并解包（类似 flatpak 的 `extra-data` 机制），文件清单记录在 `/var/lib/linuxqq/filelist`，升级时对新旧清单做差集清理上游移除的文件，卸载时按清单删除。

## 自动更新

[`.github/workflows/copr-auto-update.yml`](.github/workflows/copr-auto-update.yml) 每日运行 `scripts/check-updates.py` 检测上游版本：

| 软件包 | 版本探测方式 |
| --- | --- |
| FlClash / fcitx5-wetypex / flyline / iptvnator | GitHub API `releases/latest` |
| 微信 / WorkBuddy | 腾讯的下载/更新接口，HTTP Range 只取 RPM 头部（约 2 MB）嗅探版本 |
| linuxqq | 腾讯官方下载配置 `pcConfig.json`，从文件名解析版本 |
| wemeet | 腾讯会议下载接口 `query-download-info` |
| waydroid-script | 无 git tag，取默认分支最新 commit，版本号 = 提交日期（YYYYMMDD） |

发现新版本后，工作流自动完成：

1. 改写 spec（`Version`、`Release`、changelog）并以 `github-actions[bot]` 身份提交；
2. 向 COPR 的包 webhook 发送 POST，COPR 用刚推送的 spec 重建变更的包；
3. 用户侧 `sudo dnf upgrade` 即可获得更新。

触发机制没有有效期：COPR 的 webhook secret 不过期，GitHub Actions 由仓库自带的 `GITHUB_TOKEN` 驱动。整个更新链路无需人工维护。

## COPR 配置说明

- COPR 项目 `qvoidz/rpm-packages` 为永久项目，仅启用 `fedora-45-x86_64` chroot；spec 中的 `ExclusiveArch: x86_64` 保证其他架构自动跳过。
- 每个包以 SCM 源注册进 COPR 并开启 webhook rebuild；工作流使用的 webhook 地址存于仓库 secret `COPR_WEBHOOK_BASE`。

## 信任模型

COPR 通过 HTTPS 提供软件包，上游 RPM 的字节保持原样，不用项目密钥重新签名。GitHub release 资产会校验文件名与 API 提供的摘要；腾讯系包通过 HTTPS 下载并校验 RPM 元数据与 x86_64 架构；linuxqq 的载荷在安装期通过 HTTPS 从腾讯官方地址下载，信任级别等同于手动从官网下载。

这是个人维护的非官方仓库，与上游项目无隶属关系。
