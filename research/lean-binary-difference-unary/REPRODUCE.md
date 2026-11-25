# Reproduce the four control modules

Commands only; this document was prepared without installation, downloading or replay. Use existing Lean4.21.0 and complete Mathlib308445d7985027f538e281e18df29ca16ede2ba3 objects and pinned package caches. Set the four path variables to caller-owned locations. Public prerequisites are fetched only into a fresh caller scratch directory; this package vendors none of them. No installer or cache downloader is invoked.

```sh
set -euo pipefail
unset LEAN_OPTS
export LEAN_SYSROOT=/absolute/path/to/existing/lean-4.21.0-linux
export MATHLIB_ROOT=/absolute/path/to/existing/mathlib4
export PACKAGE_ROOT=/absolute/path/to/research/lean-binary-difference-unary
export SCRATCH_PARENT=/absolute/path/to/caller/scratch
LEAN="$LEAN_SYSROOT/bin/lean"
test -x "$LEAN"
test -d "$SCRATCH_PARENT"
"$LEAN" --version | grep -F 'version 4.21.0,'
test "$(git -C "$MATHLIB_ROOT" rev-parse HEAD)" = \
  308445d7985027f538e281e18df29ca16ede2ba3
test "$(cat "$MATHLIB_ROOT/lean-toolchain")" = leanprover/lean4:v4.21.0
test -z "$(git -C "$MATHLIB_ROOT" status --porcelain --untracked-files=no)"

WORK="$(mktemp -d "$SCRATCH_PARENT/binary-difference-replay.XXXXXXXX")"
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

git init -q "$WORK/public-adder-git"
git -C "$WORK/public-adder-git" fetch --no-tags --depth=1 \
  https://github.com/CrocSwap/integer-mult-bounds.git 6282571be5a5654cfb82568d8d70987bc4596add
test "$(git -C "$WORK/public-adder-git" rev-parse FETCH_HEAD)" = 6282571be5a5654cfb82568d8d70987bc4596add
git -C "$WORK/public-adder-git" show \
  "6282571be5a5654cfb82568d8d70987bc4596add:research/lean-padded-signed-addition/MarkedBitAddition.lean" > "$WORK/public-source/MarkedBitAddition.lean"

# Check all five public and four new exact source bodies.
printf '%s  %s\n' \
  33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed "$WORK/public-source/PairedBitXorScan.lean" \
  f28dbd4d53da61436b82cdd83cd3c7b49ec637fd0c4b40b527476e3976a50bb3 "$WORK/public-source/MarkedBitXorScan.lean" \
  7729e218143ac20dac17ca3c5ecd68b784d1d1c0b70fd2f0e4d13b8961e26c92 "$WORK/public-source/SequentialBitAddition.lean" \
  bd289c3ec5857e8dfd74a6e1138e8493c49f37bdbb83c4d6912ac902a879f302 "$WORK/public-source/MarkedZeroPadding.lean" \
  ae494a2841876ecbf4cb9ccae3cc12f11c66297660e2d63d534b4da051d4630d "$WORK/public-source/MarkedBitAddition.lean" \
  a71f74f37160cd0877eda624a97a2010fbfae467073fdc0755553ea1bc723136 "$PACKAGE_ROOT/BinaryToUnaryControl.lean" \
  4ac5d39ef7912e852e2c62553e28f2d322214a0601119529eb6068108b6208e4 "$PACKAGE_ROOT/PairedDifferenceArithmetic.lean" \
  7dc3752deed02c88bc1b90884c61cf62414dd8b0c0fe635af5ebea2018a23049 "$PACKAGE_ROOT/MarkedBitDifference.lean" \
  3677137c2cfc4cd5926bfecf7ec4729bd8c33e1196be934b51bb1a730e7e5cc4 "$PACKAGE_ROOT/PairedDifferenceUnary.lean" \
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
compile_one MarkedBitAddition "$WORK/public-source"
compile_one BinaryToUnaryControl "$PACKAGE_ROOT"
compile_one PairedDifferenceArithmetic "$PACKAGE_ROOT"
compile_one MarkedBitDifference "$PACKAGE_ROOT"
compile_one PairedDifferenceUnary "$PACKAGE_ROOT"
printf 'Preserved replay workspace: %s\n' "$WORK"
```

Inspect all logs and complete probes/types. The four new modules print34 standard-only probes and7 types. PairedDifferenceUnary retains one unnecessarySeqFocus style warning/note. Public SequentialBitAddition retains its unnecessarySimpa warning/note. No sorryAx or nonstandard axiom is accepted. The script stops on nonzero compiler exit and preserves earlier outputs/logs. Newly built object hashes may differ under relocation; exact source hashes and printed scientific interfaces bind the claims.

Author-checked context kappa=836330098538459/500000000000000000=0.001672660197076918. Numeric magnitude, supplied layout and physical representation caveats in README.md remain.
