#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
cd "$root"
sha256sum -c SHA256SUMS
work="$(mktemp -d "${TMPDIR:-/tmp}/source-borrow-crossover-XXXXXX")"
mkdir -p "$work/inputs" "$work/deps" "$work/results" "$work/reference"
unzip -q native-inputs.zip -d "$work/inputs"
unzip -q native/native-deps.zip -d "$work/deps"
for name in source440-frame-admission source-entrances source-frame-admission bit-columns joint-banks source-boundary actual-signals native-pricing independent-pricing frozen-result all-active-primes; do
 echo "Compiling $name"
 "${CXX:-g++}" -O3 -std=c++20 -I"$work/deps/include" "native/$name.cpp" -o "$work/$name"
done
i="$work/inputs/combined"
r="$work/inputs/reference"
o="$work/results"
anchor="$r/packed-baseline.json"
"$work/source440-frame-admission" "$r" "$work/reference" witnesses/empty-bases.json "$anchor"
mkdir -p "$work/source440-reference"
"$work/source440-frame-admission" "$work/inputs/source440" "$work/source440-reference" witnesses/source440-candidate-bases.json "$anchor" replace-all "$work/reference/FRAME-ADMISSION.json"
sourceanchor="$root/witnesses/source469-packed-reference.json"
"$work/source-frame-admission" "$i" "$o" witnesses/candidate-bases.json "$sourceanchor" replace-all "$work/source440-reference/FRAME-ADMISSION.json"
cp "$o/merged-bases.json" "$i/current-bases.json"
"$work/all-active-primes" "$i" "$o/merged-bases.json" "$o/ALL-ACTIVE-PRIMES.json"
"$work/actual-signals" "$i" "$o/ACTUAL-SIGNALS.json"
"$work/source-entrances" "$i" "$o/SOURCE-ENTRANCES.json"
"$work/source-boundary" "$i" "$o/SOURCE-BOUNDARY.json"
"$work/bit-columns" "$i" "$o/ALL-COLUMNS.json"
"$work/joint-banks" "$i" "$o/BANKS.json"
"$work/native-pricing" price "$o/new-profile.json" witnesses/complex-profile.json "$o/ASSEMBLY.json" 4 "$i/public-complex-and-bridge.json"
"$work/independent-pricing" "$o/ASSEMBLY.json" "$o/INDEPENDENT-ARITHMETIC.json" "$o/BANKS.json" "$sourceanchor"
"$work/frozen-result" "$o/ASSEMBLY.json" certificate.json
sha256sum -c SHA256SUMS
printf 'PASS fresh offline replay; temporary outputs preserved: %s\n' "$work"