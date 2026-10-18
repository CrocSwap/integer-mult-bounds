# JP8 frame-zero compensation batching

This is a finite replacement of one scalar panel of the selected PR626 JP8
supplier. It reduces an executable local primitive bound; it does not change
the native supplier, certify a new global invoice, or claim a new kappa.
Prepared for Varun-Mittal-1001 with substantial OpenAI Codex assistance.

## Pinned interface and admissible region

The input is the JP8 `CANONICAL-WORD.json.gz` and `LOCAL-PROGRAMS.json.gz`
under `research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8`
at base `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The inherited emitter is
`research/complex-k492-owner-repair/code/hpe_emit_local.py`; its independent
scalar/frame checker is the adjacent `hpe_audit_local.py`.

The canonical compensation is exactly 8,800 dyadic additions, each at frame
0 (the empty binary frame). Its destination set is exactly `112..223`; its
266 sources are a subset of `224..592`. These sets are disjoint. Every
referenced register starts at frame 0 and none has a residual wrapper. The
8,800 ordered destination/source pairs are distinct. The absolute
coefficient census is:

| Magnitude | Additions |
|---|---:|
| 1 | 144 |
| 1/2 | 2,832 |
| 1/4 | 5,596 |
| 3/4 | 228 |

The replacement occupies precisely the compensation interval after all 168
precondition gates and before `entry_adapters`. It neither moves a gate
across those boundaries nor changes any adapter, climb, center, A/B gate,
cleanup gate, helper allocation, or frame label. One private coefficient
stream is used at frame 0 and is cleared at both ends of each source group.
This is the coefficient-work slot already permitted by the inherited
lowering, not an additional helper or recursive call.

## Commutation and inverse-transpose orientation

Write an addition as `T(t,s,q) = I + q E_ts`. If `t,u` are destinations and
`s,v` are sources, disjointness gives `E_ts E_uv = E_uv E_ts = 0`.
Consequently every pair commutes, and their product is exactly
`I + sum q E_ts`, independently of order. This argument uses arbitrary
initial values in all 716 native registers, including dirty helpers.

The inherited backward orientation replaces every addition by
`T(s,t,-q)` in the same chronological event order. This is the
inverse-transpose convention: for a chronological product
`P = G_m ... G_1`, its inverse transpose is
`P^(-T) = G_m^(-T) ... G_1^(-T)`. Reversing the chronological list again
would be incorrect in the surrounding noncommuting program.

The backward compensation is again a disjoint rectangular panel, now with
112 sources and 266 destinations. It is grouped independently by its
actual sources after transposition. Reusing the forward grouping as a
backward source grouping would be invalid. Within either panel the same
commutation proof applies.

## Fully charged one-stream lowering

For one source `S`, let `W` be the sole private coefficient stream. Each
listed operation costs one real-component primitive: clear, add/subtract
the unchanged source, double, halve, or add/subtract `W` into a destination.
The route starts and ends with a charged clear of `W`. Negative values of
`W` are allowed; a destination's update sign is adjusted accordingly.

For all four required magnitudes, the preparation route is

```
clear W
W += S             # W = S; serve magnitude 1
W /= 2             # W = S/2; serve magnitude 1/2
W /= 2             # W = S/4; serve magnitude 1/4
W -= S             # W = -3S/4; serve magnitude 3/4 with reversed signs
clear W
```

Only destination updates required at a visited magnitude are emitted.
Every one of the 8,800 destination updates is charged separately. Source
access in both `W += S` and `W -= S` is charged. Both clears are charged,
even though the preceding group also ended with a clear. There is no free
scalar multiplication, sign change, materialization, accumulation, or
clearing. Each complex operation is charged twice, for its real and
imaginary components. At every preparation step `W = lambda S` with
`|lambda| <= 1`; no mutable native source is used as work storage.

The bounded route search, when used, has state `(k, visited_mask)` for
`W = (k/4) S`, integer `-4 <= k <= 4`. It starts at `(0,0)`. Its unit-cost
transitions are `k -> k+4`, `k -> k-4`, `k -> 2k`, and `k -> k/2` when
the new state remains in the interval and halving has even `k`. The mask
records requested absolute magnitudes visited. Destination updates do not
change this state. Breadth-first search through this finite graph finds
the least preparation length in this stated class; the two mandatory
clears and all destination updates are then added to its cost. It is not
a claim of optimality among all arithmetic circuits or cross-source
reuse policies.

For the magnitude sets that actually occur, minimal preparation lengths
also have a direct proof. The first nonzero state must be `+4` or `-4`.
Reaching magnitude 2 requires a second step; reaching magnitude 1 requires
a third. If magnitude 3 is also required, a fourth step is necessary and
is attained by `4,2,1,-3`. Thus the routes below attain the bounded-class
minimum without relying on a search solver.

| Requested magnitudes | Forward groups | Backward groups | Preparation steps | Clears |
|---|---:|---:|---:|---:|
| 1/2 | 70 | 0 | 2 | 2 |
| 1/4 | 72 | 0 | 3 | 2 |
| 1/4, 1/2 | 82 | 46 | 3 | 2 |
| 1/2, 1 | 18 | 0 | 2 | 2 |
| 1/4, 1/2, 1 | 5 | 22 | 3 | 2 |
| 1/4, 1/2, 3/4 | 0 | 21 | 4 | 2 |
| 1/4, 1/2, 3/4, 1 | 19 | 23 | 4 | 2 |

## Boundary equality and prefix allowance

At a visited coefficient `lambda`, a requested update `t += q S` is
implemented by `t += sign(q/lambda) W`, because
`|q| = |lambda|`. The source is never written, so this substitution is
valid throughout the group. After the last update `W` is erased. Applying
this identity to each update, followed by the panel commutation identity,
proves the same complete native-register boundary map. The unchanged
suffix therefore yields the inherited complete local map in both
orientations.

Equality of endpoint matrices alone would not control intermediate
growth. Let `b_r` be the inherited nonnegative, cancellation-free row
envelope at compensation entry. Sources are fixed throughout the panel.
For every destination, the exit envelope is exactly

```
b_t(exit) = b_t(entry) + sum_(updates to t) |q| b_s(entry).
```

Every reordered prefix contains a subset of these nonnegative summands,
so it is bounded by that same exit envelope. Every private-work prefix
has the exact invariant `W = lambda S`, with `|lambda| <= 1`, hence its
row norm is bounded by `b_s(entry)`. This uses the exact invariant at
`W -= S`: blindly applying a triangle inequality to that work instruction
would give `5 b_s/4`, an unnecessary overestimate of the actual `3 b_s/4`.
No such cancellation is assumed for destination accumulations.

The recomputed maximum source-entry envelopes are 1 forward and 4
backward. The panel's complete positive exit envelopes have maxima 42
forward and 125 backward. These are independent of the panel's order.
The unchanged remainder starts with exactly its inherited native envelope;
the coefficient slot is clear. Thus the original full-local bounds

```
forward:  4536094588619580433782972610869617 / 281474976710656
backward: 16753412757380464429924108070201913461 / 8388608
```

remain valid. Their inherited bit bounds are respectively 64 and 101,
both below the charged 192-bit local payload allowance. Literal primitive
replay and all-column equality provide separate executable checks of the
replacement, including every work-register prefix and final erasure.

## Exact local accounting and scope

The inherited `primitive_bound` charges a dyadic addition with absolute
reduced numerator `a` and power-of-two denominator `b` as
`3 + (bit_length(a)-1) + popcount(a) + (bit_length(b)-1)` primitives per
real component. This is the fixed binary-Horner macro with preparation,
signed accumulation, and clearing. It prices the four panel magnitudes
at 4, 5, 6, and 8 respectively. The original panel bound is therefore
`2*(144*4 + 2832*5 + 5596*6 + 228*8) = 100272`.

| Real-component primitive bound | Forward | Backward |
|---|---:|---:|
| Inherited complete local program | 257,232 | 257,280 |
| Inherited compensation panel | 100,272 | 100,272 |
| Batched preparation plus clears, before factor 2 | 1,261 | 604 |
| Batched complete panel, including 8,800 accumulations | 20,122 | 18,808 |
| Replacement complete local bound | 177,082 | 175,816 |
| Reduction in the inherited bound | 80,150 | 81,464 |

The unchanged paid profile is
`{1:2512, 2:400, 3:448, 4:160, 5:70, 6:8, 8:8}`. These are local
scalar-lowering savings with unchanged recursive geometry. They are not
additive with another pending lowering of the same instructions, are not
an update to PR626's admitted global cost constants, and do not by
themselves establish a larger kappa, an unconditional integer-multiplication
theorem, a new all-size compiler contract, or a practical speedup.
