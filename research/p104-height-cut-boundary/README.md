# P104 joint D+R wall: height/flag-cut relaxation

Source pin: `CrocSwap/integer-mult-bounds` PR #7852 head
`41beda1d6435760dc99e38bd7e65f36798aad212`. The six original Lean source
files used directly by the checker are in `pinned/`; `verify_relaxation.py`
checks their SHA-256 digests before doing any computation. The PR package and
the cited lemmas are by DreamingOfClouds with Claude Opus 5.5, as recorded
in the pinned README. This relaxation, witness, and its checker are new work
for the current investigation. No repository or GitHub changes were made.

## Exact claim and accounting

`RungWord7113.rung_word_7113_joint` takes a caller `cl` with `Ports7113` and
`DCount`, and 17 indexed traces, each with `Legal`, `Word`, `FramesSubsp`,
`ChartsSubsp`, and `OwnedNested`. Let `G_i` be the folded banked graph.
Its unproved mass premise is precisely

```
112 * 17 <= sum_i (D_i + R_i)
D_i = sum_b max(height(src_b) - height(dst_b), 0)
R_i = sum_b max(height(dst_b) - height(src_b), 0) - sum_f climb_f
```

It also takes `0 < κ < 1` and the crossing condition `hV` (caller paid plus
word payment at `1-κ` no greater than target credit plus helper credit).
The conclusion is `κ < 93453742 / 10000000000`. `hV` remains a condition:
neither the mass premise nor crossing is derived by the present result.
The source derives the folded graph, its height-stop contract and caller
certificate from the stated structural hypotheses. `excess_split_bank`
identifies `X_i = D_i + R_i` exactly. The invoice dependence is affine in
`X_i`, with slope `9^s - 8^s >= 0`, hence the theorem needs only the sum.

The indexed family can repeat the same trace. For a fixed caller and fixed
register types, a theorem of `hJ` for *every* 17-tuple satisfying only the
per-call structural hypotheses is equivalent to `D + R >= 112` for every
individual eligible trace: sum 17 inequalities in one direction; in the
other, choose the constant tuple. This says nothing about a theorem where
the additional coupled `hV` restricts the admissible tuple.

The caller has 104 ports and 96 D ports. There are 200 x-fields of heights
`1 -> 9` and 200 y-fields `0 -> 8`, so their total field climb is 3200;
helpers would add their own climb. Height here is dimension over F₂, not a
rank of the scalar bank transfer matrix. These are aggregate counts. The
full network carries substantially more structure.

## A tight named relaxation

We retain the following necessary constraints and deliberately drop the
rest. This defines the relaxation to which the optimality claim applies.

1. Use the actual #7113 ports, actual 96-D split, and the pinned 9-vector
   witness flag. Include the 400 main fields above and take helper climb 0.
2. Each bank has nested source and destination coordinate subspaces for
   that flag, with heights 0..9. Banks are an unordered multiset; they do
   **not** have to form a causal network or realize the output matrix.
3. For each nontrivial height subset `S` (1022 directed choices), require
   outgoing banks at least outgoing fields, plus 104 if `S` separates
   heights `{1,9}` from `{0,8}`. There are 128 such directed separating
   masks, or 64 complementary pairs. This is the directed height form of
   `BankFitHS1.dir_extras`; the two directions sum to `cut_hs`'s 208.
4. At each of the nine cuts of the pinned flag, require ascending banks at
   least ascending fields plus `atLevel OUT`, and descending banks at least
   `atLevel IN`. The pinned per-level extras are `[0,2,2,2,2,2,2,2,0]`
   in both directions. These are the `hout` and `hin` inequalities inside
   `BankHelpA.sum_cuts_gen`, with field crossings calculated from the actual
   label data, not from height intervals.

No nonzero-principal-minor matrix, acyclic bank dependency, arbitrary-chart
cuts, transfer coefficients, legal trace, verifier execution, payment, or
crossing is provided by this relaxation. Therefore the witness is **not**
a counterexample to the wall for a legal word or a full `BankedGraph`.

The individual flag inequalities prove `D >= 14` and `R >= 14` inside this
relaxation: nested bank crossings sum separately to ascent and descent mass;
field crossings sum to field climb; seven cuts each contribute two extras in
each direction. The same paper derivation, using the `hout`/`hin` proof in
`BankHelpA` and `BankWire.cross_nested_lt`, applies to its full banked graph
hypotheses including arbitrary helper climbs. The separate inequalities have
not been added to Lean or independently kernel-replayed in this round.

The checker constructs an integer nested-coordinate witness meeting both
floors at once. Its bank height multiplicities are:

| src → dst | count | src → dst | count |
|---|---:|---|---:|
| 0 → 2 | 200 | 0 → 3 | 14 |
| 1 → 0 | 14 | 1 → 2 | 90 |
| 1 → 3 | 96 | 2 → 3 | 90 |
| 2 → 5 | 200 | 3 → 6 | 200 |
| 5 → 8 | 200 | 6 → 9 | 200 |

The actual field flag-cut demand is
`[306,332,374,391,392,390,373,336,306]`; witness ascent counts are
`[306,334,376,393,394,392,375,338,306]` and descent counts are
`[0,2,2,2,2,2,2,2,0]`. Thus ascent = 3214, `D=14`, `R=3214-3200=14`,
and `D+R=28`. All 1022 height inequalities hold, 142 tightly. The
checker uses an integral max-flow and a verified explicit materialization
of each nested coordinate pair; it checks the resulting multisets and cuts
using only integer arithmetic.

Consequently 28 is the **exact** minimum of this named relaxation: 28 is a
lower bound by the two flag sums and the witness attains it. In fact its
attainable integer `(D,R)` pairs are exactly `D >= 14, R >= 14`: append any
needed number of one-step nested ascending and descending banks to this
witness. Adding banks cannot invalidate these lower-bound cut inequalities.
This is a statement about the relaxation only, with no claim that the added
banks are executable or satisfy an output-matrix rank condition. As checked
controls, `(D,R)=(14,98)` and `(98,14)` each meet the joint 112 threshold
while violating a different per-side 56 threshold. Repeating
the relaxed witness 17 times gives 476 against the required 1904, a deficit
of 1428, again only in the relaxation.

## A concrete missing full-model constraint

The difference is not merely hypothetical. The first actual port label is
11 and is a D port, so two x-fields have `A = span(11)` and `B = top`.
Every bank source in this witness is a coordinate subspace for the flag;
since 11 is not one of its basis vectors, no source is the one-dimensional
`span(11)`. For the arbitrary chart predicate `P(c) := c = span(11)`, the
base directed cut from `BankFitHS1.dir_extras` would require at least two
banks from `P` to its complement, while the witness supplies zero. Hence it
cannot be a full banked network with the required principal-minor and
locality/acyclic hypotheses. Any stronger attempt must retain the actual
chart/label placement, not just these height and one-flag marginals.

## Replay and controls

From this directory, run:

```
python3 -S verify_relaxation.py
```

The output is stored in `verify.log`. It verifies six source SHA-256 pins;
the two main field families; all 1022 directed height cuts; all 18
directed flag inequalities; actual coordinate containment and bank counts;
and all mass totals. Both tradeoff examples are rechecked against every
retained cut. Negative controls remove a descent, failing flag level
2, and decrement a `0 -> 2` bank, failing eight height cuts. The singleton
`span(11)` failure is also checked. The initial 90-variable scalar LP is
reconstructible with `python3 -S height_cut_lp.py > height.lp` followed by
`lp_solve height.lp`; its floating-point solver result is merely a discovery
aid, not the proof of optimality. The independent finite checks and flag
lower bound do not rely on the LP solver. No Lean build was launched here.

## Open next questions

Add the missed single-port paired cuts jointly and test whether they raise the lower bound.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
