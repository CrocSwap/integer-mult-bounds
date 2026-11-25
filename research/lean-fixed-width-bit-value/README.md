# Fixed-width Boolean decoder injectivity

At contextual κ = 836330098538459/500000000000000000 = 0.001672660197076918, this reusable Lean theorem derives literal Boolean-word equality from equal lengths and equal accepted little-endian values, and literal paired-word equality from both decoded tracks. Equal length is essential. It adds no physical encoding, allocation, runtime bound or selected multiplication theorem. The author checked this context and scope.

## What is proved

- `value_injective_of_length`: any two equal-length Boolean lists with the same PR1840 unsigned value are literally equal.
- `paired_injective_of_length`: equal-length lists of Boolean pairs are equal when both projected track values agree.

Both statements include the empty word. Without equal length, an extra high false bit would preserve value and defeat injectivity. The proof is generic structural induction and reconstruction through core `List.zip`; no finite census is used. These are reusable decoder API consequences, with no claim that binary-representation uniqueness is new mathematics.

`ACCEPTANCE_SUMMARY.json` binds the exact accepted source, two complete axiom probes and the full paired theorem type. Both probes use only `propext` and `Quot.sound`; there were no warnings. No separate publication-candidate replay is claimed.

## Reuse and related work

James Chang with OpenAI assistance, Apache-2.0. The unchanged value definition comes from [PR1840](https://github.com/CrocSwap/integer-mult-bounds/pull/1840), which proves the explicit XOR scans, source preservation and decoded XOR. This module adds fixed-length injectivity; it does not republish that implementation.

Existing [PR519](https://github.com/CrocSwap/integer-mult-bounds/pull/519) supplies automatic-width counting. [PR872](https://github.com/CrocSwap/integer-mult-bounds/pull/872) proves a nine-bit `Fin512`/`ZMod2` coordinate equivalence with `BitVec`, rather than this arbitrary-list decoder theorem. These results and core bitvector APIs are prior representation work. A bounded open/closed PR search and exact predecessor source comparison found no matching module or theorem; that is not a global novelty proof.

## Exact reproduction

Requires an existing official Lean 4.21.0 installation, Git, and standard Linux timeout/flock tools. No Mathlib is needed. Set `LEAN_HOME` to that prepared installation and `LEAN_REPLAY_LOCK` to the existing shared serial replay lock. This recipe performs no installation and preserves complete per-module logs. From this package directory:

```sh
set -eu
: "$LEAN_HOME" "$LEAN_REPLAY_LOCK"
test -x "$LEAN_HOME/bin/lean"
unset LEAN_OPTS LEAN_PATH
"$LEAN_HOME/bin/lean" --version | grep -Eq '^Lean \(version 4\.21\.0([,)]| )'
exec 9>"$LEAN_REPLAY_LOCK"
flock 9
work=$(mktemp -d)
mkdir -p "$work/sources" "$work/objects" "$work/logs"
git init -q "$work/upstream"
git -C "$work/upstream" fetch --no-tags --depth=1 https://github.com/CrocSwap/integer-mult-bounds.git 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645
git -C "$work/upstream" show 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645:research/lean-paired-bit-xor-machines/PairedBitXorScan.lean > "$work/sources/PairedBitXorScan.lean"
cp FixedWidthBitValue.lean "$work/sources/FixedWidthBitValue.lean"
printf '%s  %s\n' '33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed' "$work/sources/PairedBitXorScan.lean" | sha256sum -c -
printf '%s  %s\n' '08b09879a95bc6694e35147deeb6ea0782a64c03b1362814910c20e36e0484db' "$work/sources/FixedWidthBitValue.lean" | sha256sum -c -
for module in PairedBitXorScan FixedWidthBitValue; do
  available_kib=$(df -Pk "$work" | awk 'NR==2 {print $4}')
  [ "$available_kib" -ge 8388608 ] || { echo 'Need at least 8 GiB free'; exit 1; }
  set +e
  (ulimit -v 4194304; LEAN_PATH="$work/objects" timeout --signal=KILL 60s "$LEAN_HOME/bin/lean" -j1 -o "$work/objects/$module.olean" "$work/sources/$module.lean") >"$work/logs/$module.stdout" 2>"$work/logs/$module.stderr"
  result=$?
  set -e
  printf '%s\n' "$result" >"$work/logs/$module.exit-code"
  [ "$result" -eq 0 ] || { echo "Stopped; complete logs retained in $work/logs"; exit "$result"; }
done
printf 'Sources, objects and complete logs retained in %s\n' "$work"
```
