# Reproduce the marked fixed-width increment

Commands only; this document was prepared without installation, downloading or replay. Use existing Lean4.21.0 and complete Mathlib308445d7985027f538e281e18df29ca16ede2ba3 objects and pinned package caches. Set the four path variables to caller-owned locations. Public prerequisites are fetched only into a fresh caller scratch directory; this package vendors none of them. No installer or cache downloader is invoked.

```sh
set -euo pipefail
unset LEAN_OPTS
export LEAN_SYSROOT=/absolute/path/to/existing/lean-4.21.0-linux
export MATHLIB_ROOT=/absolute/path/to/existing/mathlib4
export PACKAGE_ROOT=/absolute/path/to/research/lean-marked-fixed-increment
export SCRATCH_PARENT=/absolute/path/to/caller/scratch
LEAN="$LEAN_SYSROOT/bin/lean"
test -x "$LEAN"
test -d "$SCRATCH_PARENT"
"$LEAN" --version | grep -F 'version 4.21.0,'
test "$(git -C "$MATHLIB_ROOT" rev-parse HEAD)" = \
  308445d7985027f538e281e18df29ca16ede2ba3
test "$(cat "$MATHLIB_ROOT/lean-toolchain")" = leanprover/lean4:v4.21.0
test -z "$(git -C "$MATHLIB_ROOT" status --porcelain --untracked-files=no)"

WORK="$(mktemp -d "$SCRATCH_PARENT/marked-increment-replay.XXXXXXXX")"
mkdir "$WORK/public-source" "$WORK/build" "$WORK/logs"
test "$(df -Pk "$WORK" | awk 'END {print $4}')" -ge 8388608
printf '%s\n' "$WORK" > "$WORK/WORKSPACE_PATH.txt"

# Fetch both immutable public fork commits into caller scratch only.
git init -q "$WORK/public-xor-git"
git -C "$WORK/public-xor-git" fetch --no-tags --depth=1 \
  https://github.com/jamesyc/integer-mult-bounds.git 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645
test "$(git -C "$WORK/public-xor-git" rev-parse FETCH_HEAD)" = 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645
git init -q "$WORK/public-padding-git"
git -C "$WORK/public-padding-git" fetch --no-tags --depth=1 \
  https://github.com/jamesyc/integer-mult-bounds.git 65ab016b4a464e3f5e2dd26c1bb0ae477e1ebce8
test "$(git -C "$WORK/public-padding-git" rev-parse FETCH_HEAD)" = 65ab016b4a464e3f5e2dd26c1bb0ae477e1ebce8
git -C "$WORK/public-xor-git" show \
  "3f1b0641d5866f9d0b6cdd8e46db416fed6c5645:research/lean-paired-bit-xor-machines/PairedBitXorScan.lean" > "$WORK/public-source/PairedBitXorScan.lean"
git -C "$WORK/public-xor-git" show \
  "3f1b0641d5866f9d0b6cdd8e46db416fed6c5645:research/lean-paired-bit-xor-machines/MarkedBitXorScan.lean" > "$WORK/public-source/MarkedBitXorScan.lean"
git -C "$WORK/public-padding-git" show \
  "65ab016b4a464e3f5e2dd26c1bb0ae477e1ebce8:research/lean-counted-bit-addition-padding/SequentialBitAddition.lean" > "$WORK/public-source/SequentialBitAddition.lean"
git -C "$WORK/public-padding-git" show \
  "65ab016b4a464e3f5e2dd26c1bb0ae477e1ebce8:research/lean-counted-bit-addition-padding/MarkedZeroPadding.lean" > "$WORK/public-source/MarkedZeroPadding.lean"

git init -q "$WORK/public-counter-git"
git -C "$WORK/public-counter-git" fetch --no-tags --depth=1 \
  https://github.com/rfu08/integer-mult-bounds.git 2d970ab3ca0271cfb2b609dc9aae1b7073b7774d
test "$(git -C "$WORK/public-counter-git" rev-parse FETCH_HEAD)" = 2d970ab3ca0271cfb2b609dc9aae1b7073b7774d
git -C "$WORK/public-counter-git" show \
  "2d970ab3ca0271cfb2b609dc9aae1b7073b7774d:research/machine-transfer-verification/stream-transfer/counters/RippleCounter.lean" > "$WORK/public-source/RippleCounter.lean"

# Check five immutable public sources and three exact package sources.
printf '%s  %s\n' \
  33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed "$WORK/public-source/PairedBitXorScan.lean" \
  f28dbd4d53da61436b82cdd83cd3c7b49ec637fd0c4b40b527476e3976a50bb3 "$WORK/public-source/MarkedBitXorScan.lean" \
  7729e218143ac20dac17ca3c5ecd68b784d1d1c0b70fd2f0e4d13b8961e26c92 "$WORK/public-source/SequentialBitAddition.lean" \
  bd289c3ec5857e8dfd74a6e1138e8493c49f37bdbb83c4d6912ac902a879f302 "$WORK/public-source/MarkedZeroPadding.lean" \
  2278a5fd158bd953f136204d92c9da0e6d9fc39fb1a74e8792e8e46aa0d2bc5a "$WORK/public-source/RippleCounter.lean" \
  30b4a6926738c5fa2afb74038f4a4663c514ad0d1d4b0eabfe92f887e30b67f1 "$PACKAGE_ROOT/TapeStack.lean" \
  ec0a2ae2a4363a43a18f717181848a5896a2ddc3cc533fcf40ca8b16d1e85d58 "$PACKAGE_ROOT/CounterArithmetic.lean" \
  e09af9663197683d69fa6e21c84c410d6e07a694c465488673330ea795b077e7 "$PACKAGE_ROOT/MarkedBinaryIncrement.lean" \
  | sha256sum --check - | tee "$WORK/logs/SOURCE_HASHES.txt"

# Use only already-present package objects. Missing paths stop this script.
export LEAN_PATH="$WORK/build"
for PACKAGE in batteries Qq aesop proofwidgets importGraph LeanSearchClient plausible; do
  LIB="$MATHLIB_ROOT/.lake/packages/$PACKAGE/.lake/build/lib/lean"
  test -d "$LIB"
  export LEAN_PATH="$LEAN_PATH:$LIB"
done
test -f "$MATHLIB_ROOT/.lake/build/lib/lean/Mathlib/Tactic/Ring.olean"
test -f "$MATHLIB_ROOT/.lake/build/lib/lean/Mathlib/Tactic/LinearCombination.olean"
test -f "$MATHLIB_ROOT/.lake/build/lib/lean/Mathlib/Computability/Tape.olean"
test -f "$MATHLIB_ROOT/.lake/build/lib/lean/Mathlib/Data/Fintype/Option.olean"
test -f "$MATHLIB_ROOT/.lake/build/lib/lean/Mathlib/Data/Fintype/Prod.olean"
test -f "$LEAN_SYSROOT/lib/lean/Lean/Elab/Tactic/Omega.olean"
export LEAN_PATH="$LEAN_PATH:$MATHLIB_ROOT/.lake/build/lib/lean:$LEAN_SYSROOT/lib/lean"
export LEAN_NUM_THREADS=1
export MIMALLOC_ARENA_RESERVE=64MiB

# Every output is fresh. A nonzero exit stops the serial sequence and preserves
# its logs and any earlier successful objects. No automatic retry is hidden.
compile_one() {
  local MODULE="$1" SOURCE_DIR="$2"
  test ! -e "$WORK/build/$MODULE.olean"
  (
    ulimit -v 4194304
    cd "$SOURCE_DIR"
    timeout --signal=KILL 60s "$LEAN" -s65536 -j1 \
      -o "$WORK/build/$MODULE.olean" "$MODULE.lean"
  ) > "$WORK/logs/$MODULE.stdout" 2> "$WORK/logs/$MODULE.stderr"
  test -s "$WORK/build/$MODULE.olean"
  sha256sum "$WORK/build/$MODULE.olean" >> "$WORK/logs/OBJECT_HASHES.txt"
}
compile_one PairedBitXorScan "$WORK/public-source"
compile_one MarkedBitXorScan "$WORK/public-source"
compile_one SequentialBitAddition "$WORK/public-source"
compile_one MarkedZeroPadding "$WORK/public-source"
compile_one TapeStack "$PACKAGE_ROOT"
compile_one RippleCounter "$WORK/public-source"
compile_one CounterArithmetic "$PACKAGE_ROOT"
compile_one MarkedBinaryIncrement "$PACKAGE_ROOT"
printf 'Preserved replay workspace: %s\n' "$WORK"
```

The three package modules print55 complete standard-only probes and2 types. The unchanged public RippleCounter additionally prints13 probes. The package sources have no diagnostics; public SequentialBitAddition retains its one unnecessarySimpa style warning and note. Reject every nonzero exit and every sorryAx/nonstandard axiom. Object hashes may vary under relocation; the exact source hashes and complete mathematical signatures bind the scope. This document was prepared without fetching, installing or replaying anything.

Author-checked context kappa=836330098538459/500000000000000000=0.001672660197076918. Fixed-width capacity, marked input allocation and physical-model boundaries remain explicit.
