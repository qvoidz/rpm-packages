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
| [Linux QQ](https://im.qq.com/linuxqq/) | 官方 x86_64 RPM 原样重打包（签名 CDN，见下文说明） |
| [腾讯会议](https://meeting.tencent.com/) | 官方 x86_64 .deb 重打包为 RPM |
| [iptvnator](https://github.com/4gray/iptvnator) | 上游 GitHub release 提供的 Linux x86_64 RPM |
| [waydroid-script](https://github.com/casualsnek/waydroid_script) | Waydroid 装 GApps/Magisk/libhoudini 的 Python 工具 |
| [Nerd Fonts Cascadia Code](https://github.com/ryanoasis/nerd-fonts) | 上游 `CascadiaCode.zip` 字体，原样安装 |
| [LazyVim](https://www.lazyvim.org/) | 官方 starter 模板 + `lazyvim` 引导命令，版本跟踪 LazyVim release |
| [nvim-vim-shim](https://neovim.io/) | `vim`/`vimdiff` 命令直接启动 Neovim 的两个 shell shim，与 vim-enhanced 互斥 |
| [Zed](https://zed.dev/) | 官方 `zed.app` bundle 原样重打包 |
| [Starship](https://starship.rs/) | 官方静态 musl 二进制 |
| [QQ音乐](https://y.qq.com/) | 官方 x86_64 .deb 重打包为 RPM（签名跳转链） |
| [WPS Office](https://linux.wps.cn/) | 官方滚动 RPM 原样重打包，版本从 RPM 头部嗅探 |
| [钉钉](https://www.dingtalk.com/) | 官方 x86_64 .deb 重打包为 RPM |
| [网易云音乐](https://music.163.com/) | 官方 x86_64 .deb 重打包为 RPM（Referer 防盗链 CDN） |
| [Telegram Desktop](https://telegram.org/) | 官方 Linux portable tar.xz 原样重打包（GitHub releases/latest 跟踪） |
| [ZCode](https://zcode.z.ai/) | 智谱 Z.ai 官方 AI 编程工作台，Linux RPM 从发布清单 CDN 重打包 |
| edge-repo | 装上后即可 `dnf install microsoft-edge-stable` |
| vscode-repo | 装上后即可 `dnf install code` |

WeTypeX 的专有运行时不在其上游 RPM 内，需按上游说明单独安装并接受许可。

## 安装

```bash
sudo dnf copr enable qvoidz/rpm-packages
sudo dnf install wechat workbuddy flclash fcitx5-wetypex flyline linuxqq wemeet iptvnator waydroid-script \
    nerd-fonts-cascadia-code lazyvim zed starship qqmusic wps-office dingtalk netease-cloud-music \
    telegram-desktop zcode edge-repo vscode-repo nvim-vim-shim
sudo dnf upgrade   # 日常升级
```

## 复用上游 RPM 的原理

COPR 从 spec 构建软件包，本仓库每个目录放一个小的重打包 spec：

1. `Source0` 指向上游 RPM 的 URL（GitHub release 资产、微信的滚动下载地址、WorkBuddy 更新接口返回的地址等），COPR 的 `rpkg` SRPM 构建器自动下载；
2. `%install` 用 `rpm2cpio | cpio -idm` 原样解包并照搬文件清单；所有重打包 spec 都关闭 `debug_package` 和 `__os_install_post`，避免 brp-strip/compress/check-rpaths 修改或拒绝上游二进制中的 `${ORIGIN}` runpath；
3. `%post`/`%postun` 只刷新桌面/图标缓存。

### 需要镜像的载荷（Linux QQ / 网易云音乐）

2026 年 10 月起，腾讯给 `qqdl.gtimg.cn` 的 QQNT 路径加了实时 URL 签名：裸链一律 HTTP 403（与出口 IP、Referer 无关），官网下载是先调签名接口换临时链。网易 CDN 则校验 Referer（裸请求 403，带 `Referer: music.163.com` 即可，机房 IP 也能下）。COPR 的二进制构建 chroot 是完全断网的（用 nettest 探测包实测，连 Fedora 自家镜像都不通），只有 SRPM 阶段有网且只能裸 GET——拿不到这两家的载荷。

因此 [`mirror.yml`](.github/workflows/mirror.yml) 在 GitHub Actions runner 上：

1. 从 spec 读取裸链（镜像 spec 需要的版本，不追官方配置的“当前版”——腾讯回滚过版本，配置会摆动）；
2. QQ：调腾讯公开签名接口 `GetSign`（nixpkgs 同方案）换临时链下载；网易云：带 Referer 直接下载；
3. 校验后发布为 GitHub Release 资产（tag `linuxqq-<版本>` / `netease-cloud-music-<版本>`），spec 的 `Source0` 指向它，COPR 构建期正常拉取；
4. 下载用 16 分片并行 + 断点续传（qqdl 对海外单连接限速严重，单流 45 分钟都拖不完）。

`GITHUB_TOKEN` 推送的提交不会触发其他工作流的普通 `push` 事件，因此 `copr-auto-update` 会显式 dispatch `mirror.yml`，并校验对应 Release 资产确实存在后才触发 COPR。每天也会检查已配置版本的镜像资产；如果 CDN 暂时不可用，后续定时运行会重试，不会把缺失的载荷提交给 COPR 构建。

## 自动更新

[`.github/workflows/copr-auto-update.yml`](.github/workflows/copr-auto-update.yml) 每日运行 `scripts/check-updates.py` 检测上游版本：

| 软件包 | 版本探测方式 |
| --- | --- |
| FlClash / fcitx5-wetypex / flyline / iptvnator | GitHub API `releases/latest` |
| 微信 / WorkBuddy | 腾讯的下载/更新接口，HTTP Range 只取 RPM 头部（约 2 MB）嗅探版本 |
| linuxqq | 腾讯官方下载配置 `pcConfig.json`，从文件名解析版本 |
| wemeet | 腾讯会议下载接口 `query-download-info` |
| waydroid-script | 无 git tag，取默认分支最新 commit，版本号 = 提交日期（YYYYMMDD） |
| nerd-fonts-cascadia-code / zed / starship | GitHub API `releases/latest` |
| lazyvim | LazyVim/LazyVim `releases/latest`（starter 模板 commit 固定） |
| qqmusic | 官方下载页内嵌的签名跳转链（`file_redirect.fcg`），版本从文件名解析 |
| wps-office | 官方滚动 RPM 永不变 URL，HTTP Range 只取 RPM 头部（约 4 MB）嗅探版本 |
| dingtalk | 官方更新 JSON 的版本描述（灰度通道，可能略滞后于实际最新版） |
| netease-cloud-music | 官方下载页解析 .deb 文件名（上游 2019 年起冻结在 1.2.1） |
| telegram-desktop | Telegram 官方 GitHub `releases/latest`（tag `v<版本>`，资产 `td-setup-linux-x64-<版本>.tar.xz`） |
| zcode | 智谱 ZCode 更新清单 API（`api/v1/releases/electron/manifest?platform=linux-x64`，YAML 中的版本号 + RPM CDN 地址） |

发现新版本后，工作流自动完成：

1. 改写 spec（`Version`、`Release`、changelog）并以 `github-actions[bot]` 身份提交；
2. 对需要镜像的包显式启动 `mirror.yml`，并确认对应 Release 资产存在；
3. 向 COPR 的包 webhook 发送 POST，COPR 用刚推送的 spec 重建变更的包；
4. 用户侧 `sudo dnf upgrade` 即可获得更新。

另外，若 Linux QQ / 网易云音乐的最近一次 COPR 构建失败，工作流只会在没有正在运行的构建时重试，避免重复提交任务。

## COPR 配置说明

- COPR 项目 `qvoidz/rpm-packages` 为永久项目，仅启用 `fedora-45-x86_64` chroot；spec 中的 `ExclusiveArch: x86_64` 保证其他架构自动跳过。
- 每个包以 SCM 源注册进 COPR 并开启 webhook rebuild；工作流使用的 webhook 地址存于仓库 secret `COPR_WEBHOOK_BASE`。

## 信任模型

COPR 通过 HTTPS 提供软件包，上游 RPM 的字节保持原样，不用项目密钥重新签名。GitHub release 资产会校验文件名与 API 提供的摘要；腾讯系包通过 HTTPS 下载并校验 RPM 元数据与 x86_64 架构；QQ/网易云的载荷由 CI 经官方渠道（签名接口 / 带 Referer 的官方 CDN）镜像到 GitHub Releases，字节不改动，构建期还校验载荷的 RPM/deb 元数据与期望版本一致。

这是个人维护的非官方仓库，与上游项目无隶属关系。


## 验证与安装测试

每次修改 SPEC 或验证脚本时，GitHub Actions 会在 Fedora 45 环境中：

- 用 `rpmspec` 解析全部 SPEC，并检查 Name/Version/Release、架构声明、重复 RPM 名称和必要段落；
- 对自动更新脚本执行 Python 语法检查和回归自测（RPM 版本比较、宏 Release 的 changelog、Waydroid 同日提交更新）；
- 对所有 GitHub Actions 工作流执行 YAML 语法检查；
- 对 shell 脚本执行语法检查和 ShellCheck。

也可以在 GitHub Actions 手动运行 **Test COPR package installation** 工作流。默认测试全部 19 个包，也可以在 `packages` 输入框填写空格分隔的包名。该工作流使用干净的 Fedora 45 容器，从已经发布的 COPR 仓库安装，因此验证的是当前已发布版本；分支中尚未发布的 SPEC 仍需合并并构建后才能做真实安装测试。

在已启用本 COPR 的 Fedora 45 x86_64 测试机上，也可以逐包验证真实安装与卸载：

```bash
sudo bash scripts/verify-packages.sh
sudo bash scripts/verify-packages.sh FlClash linuxqq
```

安装测试会检查 RPM 数据库、关键文件/启动器、桌面入口和 `dnf check` 依赖状态。测试前已经安装的软件包会保留；测试新安装的软件包时，卸载阶段不会自动清理依赖，更不会运行 `dnf autoremove`。建议在一次性 Fedora 虚拟机中执行全量测试，因为部分桌面软件包下载量较大。
