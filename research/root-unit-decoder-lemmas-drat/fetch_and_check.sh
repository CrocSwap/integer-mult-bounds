#!/usr/bin/env bash
# Fetch and check the DRAT certificates for the D5 T=3 caps-(4,4,4) UNSAT result of research/root-unit-decoder-lemmas (PR1590).
#   bash fetch_and_check.sh [workdir]            # quick: download, sha256 checks, CNF identity with the PR1590 pin (~1-2 min, ~430 MB download)
#   FULL=1 bash fetch_and_check.sh [workdir]     # also builds drat-trim (pinned commit) and checks the core-trimmed proof (~6-10 min, ~1 GB disk)
#   FULL=2 bash fetch_and_check.sh [workdir]     # also checks the original 1.71 GB proof (~20-25 min, ~2 GB disk)
# Needs: curl, shasum or sha256sum, zstd; for FULL: git, make, a C compiler.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; W="${1:-$(mktemp -d)}"; mkdir -p "$W"; cd "$W"
REL=https://github.com/DreamingOfClouds/integer-mult-bounds/releases/download/d5-t3-drat-v1
CNF_PIN=f5e75d3b1a484e02b3a832b6b5de6705cd47f3a22c2f92bdb7899875a7c17796   # = the D5 CNF digest pinned in research/root-unit-decoder-lemmas
FULL_DRAT_PIN=1b0e28b8b1d6abf36d6b66900594a4ba3fcbb8d3d4b1b329bd4e89aaca3cfaf3
DT_COMMIT=2e3b2dc0ecf938addbd779d42877b6ed69d9a985
sha(){ if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }
pass(){ echo "PASS $*"; }; fail(){ echo "FAIL $*"; exit 1; }
for f in d5_zr.cnf d5_core.drat.zst d5_full.drat.zst; do
  [ -s "$f" ] || { [ "$f" = d5_full.drat.zst ] && [ "${FULL:-0}" != 2 ] && continue; curl -fsSL -o "$f" "$REL/$f"; }
  want=$(awk -v f="$f" '$2==f{print $1}' "$HERE/SHA256SUMS"); [ "$(sha "$f")" = "$want" ] && pass "sha256 $f" || fail "sha256 $f"
done
[ "$(sha d5_zr.cnf)" = "$CNF_PIN" ] && pass "CNF equals the PR1590 pinned D5 CNF ($CNF_PIN)" || fail "CNF pin"
[ "${FULL:-0}" = 0 ] && { echo "quick checks done (set FULL=1 for the DRAT check)"; exit 0; }
[ -x drat-trim/drat-trim ] || { git clone -q https://github.com/marijnheule/drat-trim.git && git -C drat-trim checkout -q $DT_COMMIT && make -s -C drat-trim; }
zstd -q -d -f d5_core.drat.zst -o d5_core.drat
drat-trim/drat-trim d5_zr.cnf d5_core.drat -t 50000 > core.out || true; grep -q 's VERIFIED' core.out && pass "drat-trim core-trimmed proof: s VERIFIED" || fail "core proof"
if [ "${FULL:-0}" = 2 ]; then
  zstd -q -d -f d5_full.drat.zst -o d5_full.drat
  [ "$(sha d5_full.drat)" = "$FULL_DRAT_PIN" ] && pass "sha256 of original proof matches PR1590 README" || fail "full proof pin"
  drat-trim/drat-trim d5_zr.cnf d5_full.drat -t 50000 > full.out || true; grep -q 's VERIFIED' full.out && pass "drat-trim original proof: s VERIFIED" || fail "full proof"
fi
echo "all requested checks passed"
