# Sharp-window two-target macro

**Scoped finite check. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

CRT.md §4 restores every good address at once when the guard windows lie
in the published margin `2B ≤ W < 2^m − 2B` and the `K`-bit blocks are
disjoint. The isolated post-increment step also holds on the larger range
`0 ≤ W ≤ 2^m − B + 1`. PR #4646 substituted that range into the density
term and left the two-target macro itself open on the extra windows.

The live macro is two post-increment steps with a load of `f` between
them and an unload after. Positions are `(0, K)` with `K = m + 1`, so
each window occupies the `m` bits above its target and stops before the
other target. Digits of both control words stay in `0, ..., B − 2`.
Sources are constant bits, or, in one family, bits inside the restored
windows. They do not read either target bit.

On these inputs both control words return to their start, and the data
word ends as the XOR of the two source bits into the two target positions.
The tested edges `W = 0` and `W = 2^m − B + 1` sit outside the published
margin.

| Row | Edges | Restorations |
| --- | --- | --- |
| `B = 4`, `m = 5`, `K = 6`, the two edges chosen independently | `0` and `29` | 5,184 |
| `B = 2`, `m = 5`, `K = 6`, both targets on the same edge | `0` and `31` | 32 |
| `B = 8`, `m = 6`, `K = 7`, both targets on the same edge | `0` and `57` | 76,832 |
| `B = 4`, `m = 5`, source reads window bits 3 and `K + 2` | both targets on `0`, and both on `29` | 648 |

One step past the sharp edge does not restore the switch digit. With
`B = 4`, `m = 5`, first window `W = 30`, second window `0`, and
`(u, t, y) = (1, 2, 60)`, the macro ends at `(1, 10, 60)` rather than
`(1, 2, 60)`. A source that reads the two target bits on `(1, 0, 0)`
ends at `(1, 0, 1)`. The overlapping positions `(0, 1)` on
`(u, t, y) = (0, 1, 80)` still end at `(0, 5, 81)` rather than
`(0, 1, 81)`.

## Scope

Card `formal-interface-lemma`, scope **refined**. This is the first open
question of the sharp-density comparison, PR #4646. The live-digit
identity and the published-margin pair sweep are PR #4321. This package
does not repeat that sweep.

The check is finite. It does not prove the macro for every base and every
placement, and it does not move CRT.md's simultaneous argument off the
`2B` margin. The twelve paid `H`-bit exchanges, the reservoir shuttle, and
the tape repair are not replayed. No Lean proof and no multiplication
theorem are claimed.

Canonical main fetched 2026-10-22T23:23:25Z at
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/compact-switch-sharp-two-target/verify.py
python3.12 -B scripts/research_package.py --package research/compact-switch-sharp-two-target
```

The direct command prints `PASS_COMPACT_SWITCH_SHARP_TWO_TARGET`.

## Open next questions

1. Is `L ≤ p` true for a real #4174 placement, or only a sufficient
   hypothesis inherited from #4328? The constant `1/6400` in the
   sharp-density comparison uses that hypothesis. First step: read one
   production plan's address length against its `p`. Blocker: reservoir
   placement is not an input here.

## Credit

Cinna Davis, PR #4100, for CRT.md. The live-digit lemma, the sharp window,
and the published-margin pair sweep are PR #4321. The density comparison
that left this macro open is PR #4646. The published density identity and
the `L ≤ p` hypothesis are PR #4328.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
