# Destination spectators for marked writeback

The source-matched context is κ = 836330098538459/500000000000000000 = 0.001672660197076918. This generic theorem derives confinement of the accepted marked equal-width writeback destination and lifts its actual steps, every-prefix storage and first-halt run through arbitrary left/right spectator lists. It reuses the explicit PR1933 writeback controller and changes no transition. The left spectator list is in the zipper’s stored reverse order. Storage includes both complete ambient contexts and the source/destination local cells. Prepared source/destination representations and equal width remain premises; key search, allocation, global travel and the full selected multiplier are outside this result.

## Result

The unchanged finite-symbol controller copies source first-track bits into the destination first track, preserves the destination second track and complete source tape, returns both local heads, and clears arbitrary input scratch. This module derives destination confinement through arbitrary surrounding symbols, including markers. Exact first halt is 7*n+9, including n=0. Every-prefix cells are bounded by left.length+(2*n+4)+right.length. The left context uses stored reverse zipper order.

ACCEPTANCE_SUMMARY.json lists all six actual probes and their axiom dependencies. There were no warnings. Its exact source hash binds actual acceptance despite the preserved historical uncompiled-candidate comment. No additional full-type prints are claimed.

## Attribution

James Chang with OpenAI assistance, Apache-2.0. PR1933 supplies the unchanged writeback controller; PR1840 supplies marked/paired tape foundations. The proof follows PR1921’s marked-XOR confinement method. This package adds destination spectator framing only; packed metadata/source-refresh clients are excluded.

https://github.com/CrocSwap/integer-mult-bounds/pull/1933
https://github.com/CrocSwap/integer-mult-bounds/pull/1840
https://github.com/CrocSwap/integer-mult-bounds/pull/1921

## Exact reproduction

Requires an existing official Lean 4.21.0 installation, Git and standard Linux timeout/flock tools; no Mathlib is needed. Set LEAN_HOME to that prepared installation and LEAN_REPLAY_LOCK to the shared serial replay lock used by all local proof jobs. This recipe performs no toolchain installation. From this package directory, the following fetch immutable public dependencies into a fresh temporary directory, verify every source hash and compile the four-module closure. They do not modify the checkout.

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
git -C "$work/upstream" show 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645:research/lean-paired-bit-xor-machines/MarkedBitXorScan.lean > "$work/sources/MarkedBitXorScan.lean"
git -C "$work/upstream" fetch --no-tags --depth=1 https://github.com/CrocSwap/integer-mult-bounds.git ad36a85e226f72fe9cb300236cc004049394c389
git -C "$work/upstream" show ad36a85e226f72fe9cb300236cc004049394c389:research/lean-prepared-xor-writeback/MarkedTrackWriteback.lean > "$work/sources/MarkedTrackWriteback.lean"
cp MarkedWritebackFraming.lean "$work/sources/MarkedWritebackFraming.lean"
printf "%s  %s\n" "33a93351132f90fbb21f3dc06aa959c2a92d5202498540490df67149719279ed" "$work/sources/PairedBitXorScan.lean" | sha256sum -c -
printf "%s  %s\n" "f28dbd4d53da61436b82cdd83cd3c7b49ec637fd0c4b40b527476e3976a50bb3" "$work/sources/MarkedBitXorScan.lean" | sha256sum -c -
printf "%s  %s\n" "687f06c8ec773294cc0c7f4735292058e9adcb850aa94ad79961c763e691697a" "$work/sources/MarkedTrackWriteback.lean" | sha256sum -c -
printf "%s  %s\n" "2ccd5b3ca827838e7d634bdb929bd855afe6fae94d96494c8adb5e209b8735f9" "$work/sources/MarkedWritebackFraming.lean" | sha256sum -c -
for module in PairedBitXorScan MarkedBitXorScan MarkedTrackWriteback MarkedWritebackFraming; do
  available_kib=$(df -Pk "$work" | awk 'NR==2 {print $4}')
  [ "$available_kib" -ge 8388608 ] || { echo "Need at least 8 GiB free"; exit 1; }
  set +e
  (ulimit -v 4194304; LEAN_PATH="$work/objects" timeout --signal=KILL 60s "$LEAN_HOME/bin/lean" -j1 -o "$work/objects/$module.olean" "$work/sources/$module.lean") >"$work/logs/$module.stdout" 2>"$work/logs/$module.stderr"
  result=$?
  set -e
  printf '%s\n' "$result" >"$work/logs/$module.exit-code"
  [ "$result" -eq 0 ] || { echo "Stopped; complete logs retained in $work/logs"; exit "$result"; }
done
printf 'Sources, objects and complete per-module logs retained in %s\n' "$work"
```

These are reproduction instructions, with no claim of a separate publication-candidate replay. Accepted source bytes and public dependencies are unchanged.
