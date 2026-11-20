1. The COPR project is `qvoidz/rpm-packages` (currently only `fedora-45-x86_64`). `ExclusiveArch: x86_64` in the specs makes other archs skip automatically.
2. Get your API token from <https://copr.fedorainfracloud.org/api/> (after `copr-cli login`).
3. Add three repository secrets: `COPR_LOGIN`, `COPR_TOKEN`, `COPR_USERNAME` (from that token page).
4. Run the `Update packages on COPR` workflow once manually (`workflow_dispatch`) to do the initial builds; after that it is fully automatic.