# Reproduce the two accepted modules

These commands are instructions only. No installation, cache fetch, compiler
replay or publication was performed to prepare this file. They require an
existing Lean 4.21.0 installation and an existing complete Mathlib cache for
commit 308445d7985027f538e281e18df29ca16ede2ba3, including its pinned packages.
They intentionally do not invoke elan, lake, installers or cache downloaders.

Run under Bash on Linux. Set the first three paths to existing local locations.
PACKAGE_ROOT is this publication package, containing SequentialBitAddition.lean
and MarkedZeroPadding.lean. SCRATCH_PARENT is an existing writable directory.
All new dependency source, Git metadata, object files and logs go into a fresh
caller scratch directory. The public XOR modules are not copied into this
publication package.

```sh
set -euo pipefail
export LEAN_SYSROOT=/absolute/path/to/existing/lean-4.21.0-linux
export MATHLIB_ROOT=/absolute/path/to/existing/mathlib4
export PACKAGE_ROOT=/absolute/path/to/research/lean-counted-bit-addition-padding
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

# Fetch the immutable public PR1840 source commit into scratch only.
PUBLIC_HEAD=3f1b0641d5866f9d0b6cdd8e46db416fed6c5645
git init -q "$WORK/public-git"
git -C "$WORK/public-git" fetch --no-tags --depth=1 \
  https://github.com/jamesyc/integer-mult-bounds.git "$PUBLIC_HEAD"
test "$(git -C "$WORK/public-git" rev-parse FETCH_HEAD)" = "$PUBLIC_HEAD"
for MODULE in PairedBitXorScan MarkedBitXorScan; do
  git -C "$WORK/public-git" show \
    "$PUBLIC_HEAD:research/lean-paired-bit-xor-machines/$MODULE.lean" \
    > "$WORK/public-source/$MODULE.lean"
done

# Check all four exact Lean source bodies before compiling anything.
printf '%s  %s\n' \
  33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed \
  "$WORK/public-source/PairedBitXorScan.lean" \
  f28dbd4d53da61436b82cdd83cd3c7b49ec637fd0c4b40b527476e3976a50bb3 \
  "$WORK/public-source/MarkedBitXorScan.lean" \
  7729e218143ac20dac17ca3c5ecd68b784d1d1c0b70fd2f0e4d13b8961e26c92 \
  "$PACKAGE_ROOT/SequentialBitAddition.lean" \
  bd289c3ec5857e8dfd74a6e1138e8493c49f37bdbb83c4d6912ac902a879f302 \
  "$PACKAGE_ROOT/MarkedZeroPadding.lean" \
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
compile_one SequentialBitAddition "$PACKAGE_ROOT"
compile_one MarkedZeroPadding "$PACKAGE_ROOT"
printf 'Preserved replay workspace: %s\n' "$WORK"
```

Inspect all four stdout/stderr pairs and full axiom/type probes. The two public
XOR modules print thirteen probes/four types; the new two-source package prints
24 probes/four types. The accepted adder output has one `unnecessarySimpa` style
warning at line146:8 and its note; accepted padding has no diagnostic. Compiler
exit0 and an object are necessary evidence, with semantic/probe review separate.
No `sorryAx` or nonstandard axiom is accepted. Original native object hashes are
provenance in the receipts; these commands record the actual new object hashes
rather than assume relocated builds are byte-identical.

No selected bit-cost theorem follows merely from this replay. The author-checked
context remains kappa=836330098538459/500000000000000000 =0.001672660197076918.
