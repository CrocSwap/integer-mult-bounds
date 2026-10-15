#!/usr/bin/env bash
# Fresh standalone reproduction only; does not install tools or reuse old objects.
set -euo pipefail
cd "$(dirname "$0")"
lean_bin="${LEAN_BIN:-lean}"
version="$("$lean_bin" --version)"
[[ "$version" == "Lean (version 4.21.0,"* ]] || { printf 'Expected Lean 4.21.0, got %s\n' "$version" >&2; exit 2; }
sha256sum -c SOURCE_SHA256SUMS
out="${BUILD_DIR:-.build}"
[[ ! -e "$out" ]] || { printf 'Fresh output directory required: %s\n' "$out" >&2; exit 2; }
mkdir -p "$out"
out="$(cd "$out" && pwd)"
export LEAN_PATH="$out:$("$lean_bin" --print-prefix)/lib/lean"
export LEAN_NUM_THREADS=1
while IFS= read -r module; do
  printf 'Checking %s\n' "$module"
  # 40-second timeout, 3.5 GiB address-space cap, one configured Lean worker.
  (ulimit -v 3670016; timeout --kill-after=2s 40s "$lean_bin" -s65536 -j1 \
    -o "$out/$module.olean" "sources/$module.lean") \
    >"$out/$module.stdout" 2>"$out/$module.stderr"
  cat "$out/$module.stdout" "$out/$module.stderr"
  test -s "$out/$module.olean"
  if grep -q 'sorryAx' "$out/$module.stdout" "$out/$module.stderr"; then
    printf 'Rejected sorryAx in %s\n' "$module" >&2; exit 1
  fi
done < BUILD_ORDER.txt
printf 'All 127 source roots compiled. Inspect the complete saved axiom probes in %s.\n' "$out"
