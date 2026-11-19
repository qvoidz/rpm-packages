# fcitx5-wetypex

Upstream: https://github.com/panxuc/fcitx5-wetypex

## Current upstream release checked

- Release: `v3.0.1.684-9`
- x86_64 RPM: `fcitx5-wetypex-3.0.1.684-9.x86_64.rpm`
- Upstream SHA-256: `5bff24c123941f7ca807a196f960e556d1e4eb3b69cc78667ed34dff1c814efe`
- Release page: https://github.com/panxuc/fcitx5-wetypex/releases/tag/v3.0.1.684-9

The upstream project already publishes a Fedora-compatible RPM. Before creating a COPR rebuild/repackaging recipe, inspect the RPM file list, Requires, scriptlets, and upstream license/redistribution terms.

Important: WeTypeX's open-source adapter does not include the proprietary WeChat input runtime. The runtime is downloaded and installed per-user by its setup command after the user accepts the upstream license. Do not bundle that runtime in this package.
