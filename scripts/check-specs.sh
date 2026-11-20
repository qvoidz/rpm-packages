#!/usr/bin/env bash
# Static validation for every RPM spec in this repository.
# This deliberately does not download sources or publish builds.
set -euo pipefail

command -v rpmspec >/dev/null || {
    echo "rpmspec is required (install rpm-build)." >&2
    exit 2
}

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

    query=$(rpmspec -q --srpm --qf '%{NAME}|%{VERSION}|%{RELEASE}|%{ARCH}\n' "$spec" 2>&1) || {
        echo "ERROR: RPM metadata query failed for $spec"
        printf '%s\n' "$query"
        failed=1
        continue
    }

    IFS='|' read -r name version release arch <<< "$query"
    if [[ -z "$name" || -z "$version" || -z "$release" ]]; then
        echo "ERROR: Name/Version/Release is incomplete in $spec"
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
