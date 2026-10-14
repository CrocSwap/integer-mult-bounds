# Reproduce the prepared XOR write-back

Prospective commands for an existing Lean 4.21.0 installation. Set LEAN_SYSROOT, PACKAGE_ROOT and SCRATCH_PARENT to existing directories; PACKAGE_ROOT contains the two sources and this manifest. These commands were not run for publication preparation. No Mathlib cache, installer or private object is needed.

```sh
set -euo pipefail
LEAN="$LEAN_SYSROOT/bin/lean"
"$LEAN" --version | grep -F "version 4.21.0,"
WORK="$(mktemp -d "$SCRATCH_PARENT/prepared-xor-writeback.XXXXXXXX")"
mkdir "$WORK/public-source" "$WORK/build" "$WORK/logs"
test "$(df -Pk "$WORK" | awk 'END {print $4}')" -ge 8388608
git init -q "$WORK/pr488"
git -C "$WORK/pr488" fetch --no-tags --depth=1 https://github.com/jamesyc/integer-mult-bounds.git 34eb901441affffaba76b00920f2f9cb05777117
test "$(git -C "$WORK/pr488" rev-parse FETCH_HEAD)" = 34eb901441affffaba76b00920f2f9cb05777117
git -C "$WORK/pr488" show "34eb901441affffaba76b00920f2f9cb05777117:research/lean-binary-input-preparation/Lean/FixedTapeMachine.lean" > "$WORK/public-source/FixedTapeMachine.lean"
git -C "$WORK/pr488" show "34eb901441affffaba76b00920f2f9cb05777117:research/lean-binary-input-preparation/Lean/BinaryWordReversal.lean" > "$WORK/public-source/BinaryWordReversal.lean"
git -C "$WORK/pr488" show "34eb901441affffaba76b00920f2f9cb05777117:research/lean-binary-input-preparation/Lean/BinaryInputPreparation.lean" > "$WORK/public-source/BinaryInputPreparation.lean"
git -C "$WORK/pr488" show "34eb901441affffaba76b00920f2f9cb05777117:research/lean-binary-input-preparation/Lean/IntegerConvolution.lean" > "$WORK/public-source/IntegerConvolution.lean"
git init -q "$WORK/pr1840"
git -C "$WORK/pr1840" fetch --no-tags --depth=1 https://github.com/jamesyc/integer-mult-bounds.git 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645
test "$(git -C "$WORK/pr1840" rev-parse FETCH_HEAD)" = 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645
git -C "$WORK/pr1840" show "3f1b0641d5866f9d0b6cdd8e46db416fed6c5645:research/lean-paired-bit-xor-machines/PairedBitXorScan.lean" > "$WORK/public-source/PairedBitXorScan.lean"
git -C "$WORK/pr1840" show "3f1b0641d5866f9d0b6cdd8e46db416fed6c5645:research/lean-paired-bit-xor-machines/MarkedBitXorScan.lean" > "$WORK/public-source/MarkedBitXorScan.lean"
git init -q "$WORK/pr1921"
git -C "$WORK/pr1921" fetch --no-tags --depth=1 https://github.com/jamesyc/integer-mult-bounds.git 69fefa9c2b2d3e5aa9bc11537537fd25ed3ea72c
test "$(git -C "$WORK/pr1921" rev-parse FETCH_HEAD)" = 69fefa9c2b2d3e5aa9bc11537537fd25ed3ea72c
git -C "$WORK/pr1921" show "69fefa9c2b2d3e5aa9bc11537537fd25ed3ea72c:research/lean-prepared-pair-xor/MarkedXorFraming.lean" > "$WORK/public-source/MarkedXorFraming.lean"
git -C "$WORK/pr1921" show "69fefa9c2b2d3e5aa9bc11537537fd25ed3ea72c:research/lean-prepared-pair-xor/BackwardPairedInput.lean" > "$WORK/public-source/BackwardPairedInput.lean"
git -C "$WORK/pr1921" show "69fefa9c2b2d3e5aa9bc11537537fd25ed3ea72c:research/lean-prepared-pair-xor/PreparedPairXor.lean" > "$WORK/public-source/PreparedPairXor.lean"
git -C "$WORK/pr1921" show "69fefa9c2b2d3e5aa9bc11537537fd25ed3ea72c:research/lean-prepared-pair-xor/PreparedPairXorSpace.lean" > "$WORK/public-source/PreparedPairXorSpace.lean"
cat > "$WORK/SHA256SUMS" <<EOF
33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed  $WORK/public-source/PairedBitXorScan.lean
f28dbd4d53da61436b82cdd83cd3c7b49ec637fd0c4b40b527476e3976a50bb3  $WORK/public-source/MarkedBitXorScan.lean
92dadedc9f6e23d12633549b53ca8f917360e4fedac0b64a58d18feea741a5ed  $WORK/public-source/FixedTapeMachine.lean
354e6a9653ec452f62fd65866a1575500abc333d4af6128d40ecd82c67e08a1d  $WORK/public-source/BinaryWordReversal.lean
f56928c32f334cebaa1cf335f63fe62bb6d6e22c8833eb3169beaebc2693c77d  $WORK/public-source/BinaryInputPreparation.lean
0bc86f2fa8e68f39df77be603d2a9634bc008745093286903105378ab45938ea  $WORK/public-source/IntegerConvolution.lean
fa08ca77d29ab24a7166951cc83602776c8d322df88b30217ea21c923134f3e6  $WORK/public-source/MarkedXorFraming.lean
9906e9ac73404aed361a684b78e6f60bdac0e2f2989ae265e80cecbbe2418da4  $WORK/public-source/BackwardPairedInput.lean
66d4d118c2513e638f0ead5768c6de82115c30ac6177d66f8dd3f87d237fd503  $WORK/public-source/PreparedPairXor.lean
48e2f1cadafb5957d82ded19e4abdeedfa895a7489cd3d6e4cb45600fdf6cb45  $WORK/public-source/PreparedPairXorSpace.lean
687f06c8ec773294cc0c7f4735292058e9adcb850aa94ad79961c763e691697a  $PACKAGE_ROOT/MarkedTrackWriteback.lean
5e127af916a77c876d33efdb4d634a5cc41a42148892b75a691f9026b236abdd  $PACKAGE_ROOT/PreparedXorWriteback.lean
EOF
sha256sum --check "$WORK/SHA256SUMS"
unset LEAN_OPTS
export LEAN_PATH="$WORK/build:$LEAN_SYSROOT/lib/lean"
export LEAN_NUM_THREADS=1
export MIMALLOC_ARENA_RESERVE=64MiB
for MODULE in PairedBitXorScan MarkedBitXorScan IntegerConvolution FixedTapeMachine BinaryWordReversal BinaryInputPreparation MarkedXorFraming BackwardPairedInput PreparedPairXor PreparedPairXorSpace MarkedTrackWriteback PreparedXorWriteback; do
  if test -f "$PACKAGE_ROOT/$MODULE.lean"; then SOURCE="$PACKAGE_ROOT/$MODULE.lean"; else SOURCE="$WORK/public-source/$MODULE.lean"; fi
  (ulimit -v 4194304; cd "$(dirname "$SOURCE")"; timeout 60 "$LEAN" -s65536 -j1 -o "$WORK/build/$MODULE.olean" "$(basename "$SOURCE")") > "$WORK/logs/$MODULE.stdout" 2> "$WORK/logs/$MODULE.stderr"
done
```

Inspect every complete axiom list and printed type. Reject errors and sorryAx; retain the documented three inherited deprecation warnings. Publication preparation introduces no new runtime or CI success claim.
