#!/usr/bin/env bash
# Static validation for every RPM spec in this repository.
# This deliberately does not download sources or publish builds.
set -euo pipefail

command -v rpmspec >/dev/null || {
    echo "rpmspec is required (install rpm-build)." >&2
    exit 2
}
command -v python3 >/dev/null || {
    echo "python3 is required to validate the package updater." >&2
    exit 2
}

# Validate the automatic version updater as well as the RPM specs. Its
# self-tests cover RPM version ordering, macro-based changelog releases,
# and same-day Waydroid commit bumps without making network requests.
python3 -c 'import ast, pathlib; ast.parse(pathlib.Path("scripts/check-updates.py").read_text(encoding="utf-8"))'
python3 scripts/check-updates.py --selftest

mapfile -t specs < <(find . -mindepth 2 -maxdepth 2 -type f -name '*.spec' -print | sort)
if [[ ${#specs[@]} -eq 0 ]]; then
    echo "No spec files found." >&2
    exit 1
fi

failed=0
declare -A names=()

for spec in "${specs[@]}"; do
    echo "Checking $spec"

    if ! expanded=$(rpmspec -P "$spec" 2>&1); then
        echo "ERROR: rpmspec could not parse $spec"
        printf '%s\n' "$expanded"
        failed=1
        continue
    fi

    name=$(awk -F: '$1 == "Name" { sub(/^[[:space:]]*/, "", $2); print $2; exit }' "$spec")
    version=$(awk -F: '$1 == "Version" { sub(/^[[:space:]]*/, "", $2); print $2; exit }' "$spec")
    release=$(awk -F: '$1 == "Release" { sub(/^[[:space:]]*/, "", $2); print $2; exit }' "$spec")
    arch=$(awk -F: '/^(ExclusiveArch|BuildArch):/ { sub(/^[[:space:]]*/, "", $2); print $2; exit }' "$spec")
    if [[ -z "$name" || -z "$version" || -z "$release" || -z "$arch" ]]; then
        echo "ERROR: Name/Version/Release/architecture declaration is incomplete in $spec"
        failed=1
        continue
    fi

    if [[ -n ${names[$name]+x} ]]; then
        echo "ERROR: duplicate RPM Name '$name' in $spec and ${names[$name]}"
        failed=1
    else
        names[$name]=$spec
    fi

    if ! grep -q '^%files\b' "$spec"; then
        echo "ERROR: missing %files section in $spec"
        failed=1
    fi

    if ! grep -qE '^(ExclusiveArch|BuildArch):' "$spec"; then
        echo "ERROR: $spec must declare ExclusiveArch or BuildArch"
        failed=1
    fi

    if grep -qiE '^Source[0-9]*:.*\.zip([[:space:]]|$)' "$spec"; then
        if ! grep -q 'unzip' "$spec" || ! grep -qE '^%setup.*-T' "$spec"; then
            echo "ERROR: ZIP source in $spec must use %setup -T and unzip"
            failed=1
        fi
    fi

    if grep -q 'rpm2cpio' "$spec" &&
       { ! grep -q '^BuildRequires:[[:space:]]*rpm\b' "$spec" ||
         ! grep -q '^BuildRequires:[[:space:]]*cpio\b' "$spec"; }; then
        echo "ERROR: $spec uses rpm2cpio but must BuildRequire both rpm and cpio"
        failed=1
    fi

    if ! grep -qE '^(Source[0-9]*|NoSource):' "$spec" &&
       ! grep -q '^BuildArch:[[:space:]]*noarch' "$spec"; then
        echo "ERROR: $spec has neither a source nor a noarch-only definition"
        failed=1
    fi

    if grep -qE '^(PreReq|BuildRoot|Group):' "$spec"; then
        echo "WARNING: deprecated/unneeded RPM tag in $spec"
    fi

    printf '  -> %s %s-%s (%s)\n' "$name" "$version" "$release" "$arch"
done

echo
echo "Checked ${#specs[@]} spec files."
if [[ $failed -ne 0 ]]; then
    echo "Static RPM spec validation FAILED."
    exit 1
fi
echo "Static RPM spec validation PASSED."
