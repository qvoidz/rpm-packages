# qvoidz RPM 软件包

面向 Fedora x86_64 的 COPR 软件源，核心思路是**原样复用上游 RPM**：载荷用 `rpm2cpio | cpio` 逐字节解包后重新打包，绝不重新构建。GitHub Actions 工作流每日跟踪上游版本、自动改写 spec 并触发 COPR 构建，用户侧只需要普通的 `dnf upgrade`。

## 软件包

- [微信 WeChat](https://weixin.qq.com/) — 腾讯官方 Linux RPM（无 GitHub release）
- [WorkBuddy](https://www.workbuddy.cn/) — 腾讯官方 Linux RPM，通过更新接口 `copilot.tencent.com/v2/update?platform=workbuddy-linux-x64-rpm` 发现（无 GitHub release）
- [FlClash](https://github.com/chen08209/FlClash) — 上游 Linux x86_64 RPM
- [Fcitx5 WeTypeX](https://github.com/panxuc/fcitx5-wetypex) — 上游 x86_64 RPM
- [Flyline](https://github.com/HalFrgrd/flyline) — 包装上游 release 压缩包内的预编译 bash loadable（无上游 RPM，由 COPR 构建）
- [Linux QQ](https://im.qq.com/linuxqq/) — 安装器壳包：腾讯 CDN 拒绝机房 IP，构建机拿不到安装包。RPM 本体只有几 KB，**在你安装时**由 `%post` 从腾讯官方地址下载载荷（flatpak `extra-data` 的 RPM 模拟），并用文件清单保证升级/卸载干净
- [腾讯会议](https://meeting.tencent.com/) — 将官方 x86_64 .deb 重打包为 RPM（无上游 RPM，由 COPR 构建）
- [iptvnator](https://github.com/4gray/iptvnator) — 上游 GitHub release 提供的 Linux x86_64 RPM
- [waydroid-script](https://github.com/casualsnek/waydroid_script) — Waydroid 一键装 GApps/Magisk/libhoudini 等的 Python 工具（无 tag，跟踪 master；InquirerPy/pfzy 从固定 PyPI wheel 内置，运行 `sudo waydroid-script`）

WeTypeX 的专有运行时不在其上游 RPM 内，需按上游说明单独安装并接受许可。

## "复用上游 RPM"的原理

COPR 从 spec 构建软件包，所以每个目录放的是一个小的重打包 spec：

1. `Source0` 指向上游 RPM 的 URL（GitHub release 资产、微信的版本无关下载地址、WorkBuddy 更新接口返回的地址等）。COPR 的 `rpkg` SRPM 构建器会自动下载 URL 源。
2. `%install` 原样解包（`rpm2cpio %{SOURCE0} | cpio -idm`）并照搬文件清单，不改动任何二进制——这也是所有重打包 spec 都关闭 `debug_package` 和 `__os_install_post` 的原因（brp-strip/compress/check-rpaths 会修改或拒绝上游二进制里的 `${ORIGIN}` runpath）。
3. `%post`/`%postun` 只刷新桌面/图标缓存。

linuxqq 是唯一的例外：没有 Source0，载荷在安装期下载（见上文）。

## 自动更新

[`copr-auto-update` 工作流](.github/workflows/copr-auto-update.yml) 每日运行 `scripts/check-updates.py`：

| 软件包 | 版本探测方式 |
| --- | --- |
| FlClash | GitHub API `releases/latest`（tag `v<版本>`） |
| fcitx5-wetypex | GitHub API `releases/latest`（tag `v<版本>-<rel>`，两个字段同步更新） |
| flyline | GitHub API `releases/latest`（tag `v<版本>`） |
| 微信 | HTTP `Range` 请求只取腾讯滚动下载地址的 RPM 头部（约 2 MB），用 `rpm -qp` 嗅探版本 |
| WorkBuddy | 腾讯更新接口（JSON：版本 + RPM 下载地址）；同样嗅探 RPM 头部做校验，改写 `Version` 和 `Source0` |
| linuxqq | 腾讯官方桌面版下载配置（`pcConfig.json`），从文件名解析版本；只改写 `Version` 和 `%global qq_rpm_url` 两行——载荷由包的 `%post` 在用户机器上安装期下载 |
| wemeet | 腾讯会议下载接口（`query-download-info`：版本 + .deb 地址，都会改写） |
| iptvnator | GitHub API `releases/latest`（tag `v<版本>`） |
| waydroid-script | 无 tag，取默认分支最新 commit：版本 = 提交日期（YYYYMMDD），commit hash 改写进 `%global commit` |

发现上游新版本后，工作流会：

1. 改写 spec（`Version`、`Release`、changelog），以 `github-actions[bot]` 身份提交；
2. 只对变更的包调用 `copr-cli buildscm`，让 COPR 重建并发布；
3. 用户随后 `sudo dnf upgrade` 即可升级。

仓库另有一个独立的 [GitHub Pages DNF 镜像](.github/workflows/publish-dnf-repo.yml)（`scripts/sync-dnf-repo.py`）；只用 COPR 的话可以删掉。

## Fedora 安装（COPR）

完成下文的一次性配置后：

```bash
sudo dnf copr enable qvoidz/rpm-packages
sudo dnf install wechat workbuddy flclash fcitx5-wetypex flyline linuxqq wemeet iptvnator waydroid-script
sudo dnf upgrade   # 之后就正常升级
```

备选方式（不用 COPR 的静态镜像）：

```bash
sudo curl -fsSL https://raw.githubusercontent.com/qvoidz/rpm-packages/main/qvoidz.repo -o /etc/yum.repos.d/qvoidz.repo
sudo dnf makecache
sudo dnf install wechat workbuddy flclash fcitx5-wetypex
```

## COPR 一次性配置

1. COPR 项目为 `qvoidz/rpm-packages`（目前只有 `fedora-45-x86_64`）。spec 里的 `ExclusiveArch: x86_64` 会让其他架构自动跳过。
2. 在 <https://copr.fedorainfracloud.org/api/> 获取 API token。
3. 在 GitHub 仓库添加三个 secret：`COPR_LOGIN`、`COPR_TOKEN`、`COPR_USERNAME`（都来自那个 token 页面）。
4. 手动跑一次 `Update packages on COPR` 工作流（`workflow_dispatch`）完成首次构建，之后就全自动了。

注意：COPR 的 API token 有有效期，过期后工作流里的构建步骤会失败——重新访问上面的 token 页面生成新 token 并更新 secrets 即可。没配 secrets 时工作流仍会改写并提交 spec，只是不触发构建（日志里会有警告）。

## 信任模型

COPR 通过 HTTPS 提供软件包。上游 RPM 的字节保持原样，不用项目密钥重新签名。FlClash、WeTypeX、flyline 的资产还会校验 GitHub release 资产名（以及 API 提供的摘要）；微信和 WorkBuddy 通过 HTTPS 从腾讯下载并校验 RPM 元数据与 x86_64 架构（WorkBuddy 接口的 `sha256hash` 字段实测与实际文件不符，不使用）。linuxqq 的载荷在安装期通过 HTTPS 从腾讯官方地址下载，信任级别等同于手动从 im.qq.com 下载。这是个人维护的非官方仓库，与上游项目无隶属关系。
