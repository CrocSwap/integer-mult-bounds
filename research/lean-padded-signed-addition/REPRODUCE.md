# Reproduce the accepted padded signed-addition chain

These commands are instructions only. No installation, cache fetch, compiler
replay or publication was performed to prepare this file. They require an
existing Lean 4.21.0 installation and an existing complete Mathlib cache for
commit 308445d7985027f538e281e18df29ca16ede2ba3, including its pinned packages.
They intentionally do not invoke elan, lake, installers or cache downloaders.

Run under Bash on Linux. Set the first three paths to existing local locations.
PACKAGE_ROOT is this publication package, containing the six new Lean modules. SCRATCH_PARENT is an existing writable directory.
All new dependency source, Git metadata, object files and logs go into a fresh
caller scratch directory. The public XOR modules are not copied into this
publication package.

```sh
set -euo pipefail
export LEAN_SYSROOT=/absolute/path/to/existing/lean-4.21.0-linux
export MATHLIB_ROOT=/absolute/path/to/existing/mathlib4
export PACKAGE_ROOT=/absolute/path/to/research/lean-padded-signed-addition
export SCRATCH_PARENT=/absolute/path/to/caller/scratch
LEAN="$LEAN_SYSROOT/bin/lean"
test -x "$LEAN"
test -d "$SCRATCH_PARENT"
"$LEAN" --version | grep -F 'version 4.21.0,'
test "$(git -C "$MATHLIB_ROOT" rev-parse HEAD)" = \
  308445d7985027f538e281e18df29ca16ede2ba3
test "$(cat "$MATHLIB_ROOT/lean-toolchain")" = leanprover/lean4:v4.21.0
test -z "$(git -C "$MATHLIB_ROOT" status --porcelain --untracked-files=no)"

WORK="$(mktemp -d "$SCRATCH_PARENT/bit-add-padding-replay.XXXXXXXX")"
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

# Check all public and new source bytes before compiling.
printf '%s  %s\n' \
  33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed "$WORK/public-source/PairedBitXorScan.lean" \
  f28dbd4d53da61436b82cdd83cd3c7b49ec637fd0c4b40b527476e3976a50bb3 "$WORK/public-source/MarkedBitXorScan.lean" \
  7729e218143ac20dac17ca3c5ecd68b784d1d1c0b70fd2f0e4d13b8961e26c92 "$WORK/public-source/SequentialBitAddition.lean" \
  bd289c3ec5857e8dfd74a6e1138e8493c49f37bdbb83c4d6912ac902a879f302 "$WORK/public-source/MarkedZeroPadding.lean" \
  bdd5766e7ee47b565748d6d8abb89ef51498c02f2d5f3aeaaedd8676048fed2a "$PACKAGE_ROOT/SignedWordAlignment.lean" \
  ae494a2841876ecbf4cb9ccae3cc12f11c66297660e2d63d534b4da051d4630d "$PACKAGE_ROOT/MarkedBitAddition.lean" \
  ceffcc4ac3e65c5a45a5e6ccc41e774522756146579818c7c9e32498a0316063 "$PACKAGE_ROOT/MarkedPairLayout.lean" \
  44e7d0b7535f5085ab18cb61f750b63bec9f46629383c9dfe89e76cb5caa1f3a "$PACKAGE_ROOT/MarkedLayoutAddition.lean" \
  9a0e22b6769f55677c3a877627a8fa8dbeb5be2adad881dc3f2f61064a43deba "$PACKAGE_ROOT/PaddedSignedAddition.lean" \
  9402cd2c9bb9983d1020ee1a431ce8f217a65b51e67c5f01066b8aa62a4d539c "$PACKAGE_ROOT/PaddedAdditionLinearInvoice.lean" \
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
compile_one SignedWordAlignment "$PACKAGE_ROOT"
compile_one MarkedBitAddition "$PACKAGE_ROOT"
compile_one MarkedPairLayout "$PACKAGE_ROOT"
compile_one MarkedLayoutAddition "$PACKAGE_ROOT"
compile_one PaddedSignedAddition "$PACKAGE_ROOT"
compile_one PaddedAdditionLinearInvoice "$PACKAGE_ROOT"
printf 'Preserved replay workspace: %s\n' "$WORK"
```

Inspect every stdout/stderr pair and complete probes/types. The six new sources
print 41 standard-only probes and 10 full types with no accepted diagnostic.
Public SequentialBitAddition retains one unnecessarySimpa style warning and its
note. Compiler exit 0 and an object are necessary evidence; no sorryAx or
nonstandard axiom is accepted. Newly recorded object hashes need not equal
historical relocated builds. The exact author-checked context remains
kappa=836330098538459/500000000000000000=0.001672660197076918.
