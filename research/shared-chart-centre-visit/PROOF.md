# One shared exit-chart visit still loses

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

This is a scoped negative result in the chart model of
`research/center-chain-terminal-feasibility`. It does not change κ, admit a
caller, or replay the Clifford compiler. The selected conditional exponent
stays `60403/20000000`.

## What #4839 already charges

After the normalized #4694/#4698 word, centre `j` exits on the empty chart
with value `z_j + R_j x`. The support of `R_j` is 56 X coordinates plus one
pivot helper. Each affected Y coordinate carries a nonzero multiple of that
centre. The strip-all policy moves every one of those registers to the empty
chart, subtracts, and restores it.

For centre 0 that bill is `112` width-8 transports and `114` width-9
transports, against one optimistic rank-8 reward. The same sign holds for
every singleton, every pair, and the full set of eight centres.

## The changed word

The source frames give a stricter geometry than “one strip per register”:

- Chart 0 is the empty frame.
- Chart 1 is one width-9 frame, and the empty frame is strictly contained in it.
- All 57 observation supports of every centre, including the pivot, exit on chart 1.
- Each of the 112 affected Y charts is a distinct width-8 frame strictly contained in chart 1. The dimension gap is 1.

The retained evaluator charges a transport only when the two frames are
nested, and the recursive width is the difference of their lengths. A common
chart is required for an ADD. Transport does not change the scalar
coefficient vector; it changes only the chart label.

So the following word is legal. For a selected set `S`:

1. Transport each selected centre from chart 0 to chart 1. Width 9.
2. Subtract that centre’s whole observation at chart 1.
3. For each distinct affected Y field, hop that field from its chart up to chart 1, subtract every selected centre that touches it, and hop back. Each hop has width 1.
4. Transport each selected centre back to chart 0. Width 9.

Every original exit chart is restored. No register is created or discarded.
X registers are never moved. The scalar map is exactly the strip-all map,
because the same coefficients are subtracted and transport contributes the
identity on coefficients.

## Bill

Let `s = |S|`, let `n_Y` be the number of distinct affected Y fields, and let
`t = 1 - C` with `C` in `[0, 1]`. The new recursive requests are

```text
2 n_Y    of width 1,
2 s      of width 9.
```

The optimistic new reward remains `s` rank-8 jobs, the same grant used by
#4839, including a free positive-job normalization. Scalar ADDs, routing,
storage and precision are given cost zero in this screen. The resulting
incremental moment is at most

```text
Delta(t) = s * 8^t - 2 n_Y - 2 s * 9^t.
```

For real `t >= 0`, `9^t >= 8^t >= 1`. Therefore

```text
Delta(t) <= -s * 8^t - 2 n_Y <= -s - 2 n_Y.
```

The census, checked on all 37 selections, is:

| Selection | `n_Y` | Added requests | `Delta` upper bound | Same bound if both width-9 moves are free |
| --- | ---: | --- | ---: | ---: |
| Each singleton | 56 | 112 width 1 + 2 width 9 | -113 | -104 |
| Each pair | 88 | 176 width 1 + 4 width 9 | -178 | -160 |
| All eight | 112 | 224 width 1 + 16 width 9 | -232 | -160 |

The free-round-trip column uses only `8^t <= 8`, so `s * 8^t - 2 n_Y <= 8 s - 2 n_Y`. The width-9 charges are not what keeps the sign negative. One rank-8 reward is worth at most 8 on this interval, and the width-1 hops alone cost `2 n_Y >= 112`.

The old strip bill for centre 0 was `112` width-8 requests and `114` width-9 requests. The same endpoint is now `112` width-1 requests and `2` width-9 requests. That is a real reduction, and it is still strictly negative on the whole interval.

## Finite certificate

`verify.py` rebuilds the normalized source word from the pinned #4694 emitter and the pinned helper-normalization header. For every one of the 37 selections it checks:

- the shared-visit endpoint equals the declared target;
- the strip-all endpoint equals that same target;
- the gatewise raw inverse transpose of the shared visit equals the transpose of the two-sided scalar inverse;
- the paid widths are exactly the counts above;
- six malformed tails are rejected: a missing X term, a missing Y correction, an ADD on the empty chart against a chart-1 register, a width-8 charge for the width-9 centre hop, a centre hop that claims to start on chart 1 before arrival, and a width-2 charge for a width-1 Y hop.

The source profile remains `{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}`. The joint 379+379 normalization is not removed.

## What this does not show

This is not a lower bound for every heterogeneous producer. A word that changes Y’s exit frames, changes which registers may share a chart, or changes the demanded outputs can have a different bill. The evaluator’s rule that transport preserves scalar coefficients is the predecessor’s rule; this package does not replace it with a fresh phase-aware Clifford execution. Chart 1’s frame was already one of the frames lowered in #4839, but those recipes are not rerun here.

Direct hops between two Y charts are not used. Those charts need not be nested, and this schedule does not need them: every Y chart meets chart 1 in one rank.
