# One coded helper for an all-K complex packet cell

A six-source circuit for the selected all-K cell uses one coded helper and
28 core additions. Including dirty-input preconditioning, helper restoration
and every final frame climb, its profile improves on direct delivery using
the same register stock for every recursive moment exponent `0 < s < 1`.

Both circuits also rebuild inside the pinned raw K492 construction. The
changed native words use 490 helpers; each passes independent exact replay
of all 714 input columns in forward and inverse-transpose orientations,
with native frames and dyadic primitives checked. Their paid-profile
difference is exactly the cell's difference.

**No new κ is claimed.** These are changed raw words. The later supplier
transformations, phase lowering, wrappers, global helper ownership and full
assembly have not been rebuilt for them.

The package also gives an analytic obstruction for arbitrary signed
operations confined to one target pair without helpers, and a solver-backed
exclusion for a broader, explicitly positive no-helper domain. The constructive
circuit uses several target pairs and one helper, outside both exclusions.

## Reproduce

From the repository root, with Python 3.11 or later and no third-party packages:

```sh
python3 -B research/complex-packet-borrowing23/verify.py
```

Expected first line:

```text
PASS_COMPLEX_CODED_CELL_AND_PAIR_BORROWING_OBSTRUCTION
```

The command checks the source pins and runs inherited code with assertions
enabled, including when the main checker is called with `-I -O`. It rebuilds
the unmodified raw 492-helper word, derives eight signed all-K cells, replays
the one-helper circuit on all 13 arbitrary input columns in both orientations,
and independently audits both changed 714-register native words.

It also enumerates 504 nonempty leaver joins and binds 3,600 possible shared
supports to the chronology obstruction. A separate rational scalar/frame
replay examines all 720 orders of a six-event three-source example. Of these,
120 have the required arbitrary-input scalar map and none has legal frames.
Omitting source-frame propagation incorrectly accepts 60. Deliberately
omitting compensation, cleanup or the coded helper read is rejected.

No solver is needed for these checks. The optional solver reproduction below
is separate from the explicit constructive witness and the analytic proof.

## The selected cell

The OS assignment seed was **23**, assigning the complex-supplier track.
The secondary string was `23|made, shell, arm, script, fix, tape`.
Three independently specified mechanisms were ranked by SHA-256; the
cross-factory packet-sharing experiment was selected. Hash ordering of the
52 formed pair/sign cases selected **pair (6,7), sign +1**. The base is
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

The cell has two leavers from each of the factories `(0,1,6,7)`,
`(2,3,6,7)` and `(4,5,6,7)`. Normalize the six target labels so that target
`Y_i` omits source `X_i`. For each source, its rank-two initial frame is
`E_i`; target `Y_i` has a rank-eight cap `H_i`. Exact XOR-span enumeration
checks

```text
E_i is contained in H_j if and only if i != j.
```

The required local source-to-target increment has a zero diagonal and
nonzero entries everywhere else. The coefficient signs need not agree for
the proof. All eight signed all-K cells have the same incidence pattern.
The checker derives their roles and coefficients from the pinned constructor,
then checks the subspaces independently by explicit XOR closure.

## The one-helper circuit and its paid gain

[CODED-CELL.json](CODED-CELL.json) lists the 28 positive core additions and
the legal 30-read direct control, using the normalized labels above. The
helper accumulates `X4 + X2`, spanning two different factories. Four reads
share a target's current sum with another target; one target reads the helper.

Targets and the helper start with arbitrary independent dirty values. Before
source access, invert the core's five non-source reads in reverse order at
frame zero. After the core, climb sources and the helper to rank nine and
targets to their rank-eight caps. Then undo the helper's two source additions
at the full frame. The complete local circuit has 35 scalar additions;
the direct control has 30. The comparison here concerns recursive frame cost,
not a reduction in this local scalar operation count.

Exact rational replay verifies the required map
`Y_i += sum_{j != i} X_j`, with every source and the dirty helper restored.
An independent XOR-span replay charges both participants of every read and
all final climbs:

| Circuit, with the same one-helper stock | H1 | H2 | H3 | H9 | Rank mass |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct, helper idle | 48 | 12 | 6 | 1 | 99 |
| Coded helper | 32 | 17 | 11 | 0 | 99 |

Thus coded minus direct is

```text
-16 H1 + 5 H2 + 5 H3 - H9.
```

For the moment `sum_r H_r r^s`, this is strictly negative for every
`0 < s < 1`. To see this without numerical sampling, set `x = 3^s` and
`a = log(2)/log(3)`, so `1 < x < 3` and `1/2 < a < 1`.
Concavity and the tangent to `x^a` at 3 give

```text
2^s = x^a <= 2 + (2a/3)(x-3) <= (x+3)/3.
```

Consequently direct minus coded satisfies

```text
16 + 9^s - 5*3^s - 5*2^s
  >= x^2 - (20/3)x + 11
   = (3-x)(11/3-x) > 0.
```

The standard checker binds this argument to the exact integer profiles.
It does not claim that the coded circuit is optimal, or compare it with every
possible direct circuit or helper lifetime convention.

## Replay inside the native construction

[native.py](native.py) applies a checked, in-memory recipe to the pinned
constructor. It adds the selected positive `(6,7)` cell to the four existing
raw triangles, removes its three formed packet copies, and reserves one of
those slots for the coded helper: `492 - 3 + 1 = 490`. The direct control
reserves the same slot and leaves it idle.

The recipe delays the six own reads, inserts the chosen circuit, and inverts
its extra target basis in both the zero-frame precondition and the center
scatter. The original constructor still checks its clean scalar identity.
The unchanged `hpe_audit_and_transport.py` then independently derives dirty
helper compensation and checks the complete native word, including all 714
arbitrary input columns in both orientations. Its assertions remain enabled.

Both words have rank mass 6,266 and 490 full-width helpers. The auditor recovers
the same difference `-16 H1 + 5 H2 + 5 H3 - H9`. Exact content hashes and all
mathematical audit receipt fields are in [EXPECTED.json](EXPECTED.json).
The raw and canonical words are rebuilt in temporary directories; no generated
word is trusted as an input certificate.

This establishes a native local improvement over the specified matched-stock
direct control. It is not a comparison against the admitted, globally hosted
incumbent, and does not transfer its owner map or its κ to this new word.

## Resolved no-helper search

Replacing a step-by-step state model with event clocks resolved the earlier
five- and six-source timeouts. The unrestricted target graph is now included,
with these restrictions on the source-dependent part of the circuit:

- Sources are immutable; there are no helpers or register resets.
- Operations are positive unit additions of disjoint signal supports.
  There is no source-dependent subtraction, rescaling or repeated coefficient.
- Each target must receive exactly one copy of every source except its own.
  Both participants inherit every read's common frame.
- At least one target-to-target read carries a nonempty signal.

One potential event per ordered register pair suffices in this domain.
Repeating an edge would resend a source term that the receiver already has,
since supports never shrink. Using both directions between targets would
likewise resend a term from the first read. Events sharing a register have
distinct clocks; disjoint events can be ordered arbitrarily. Each event's
frame contains every earlier frame touching either participant.

The model permits source-free dirty-input preconditioning optimistically.
It requires no dirt-restoration certificate for a hypothetical solution, so
its UNSAT result also excludes the corresponding realizable circuits in this
positive domain. It does not exclude signed or rescaled circuits.

Z3 5.1.0 and CVC5 1.4.2 both returned **UNSAT** for six sources, on the same
exported formula with SHA-256
`e9d8e27bac9d4b2dc78f5a745847d99b9396c5b6476b87cac415d71dba5507ef`.
They took approximately 12.4 and 130.7 seconds respectively. The direct-only
control and the control omitting frames both return SAT. These are recorded
solver outcomes, not an independently checked UNSAT proof certificate.

Optional reproduction, with `z3-solver==5.1.0.0` and `cvc5==1.4.2` installed:

```sh
python3 research/complex-packet-borrowing23/search_events.py --engine z3 --out /tmp/packet-z3
python3 research/complex-packet-borrowing23/search_events.py --engine cvc5 --out /tmp/packet-cvc5
python3 research/complex-packet-borrowing23/search_events.py --control direct --out /tmp/packet-direct
python3 research/complex-packet-borrowing23/search_events.py --control no-frames --out /tmp/packet-no-frames
python3 research/complex-packet-borrowing23/search_events.py --helpers 1 --max-adds 28 --out /tmp/packet-helper
```

Use fresh output directories. The script writes the formula and a result
receipt. `--export-only` regenerates the formula without solving. Solver
timings are observations, not runtime guarantees; unknown remains inconclusive.
The one-helper SAT witness is checked separately by the solver-free replay.

## Single-pair proposition and proof

Let there be `n >= 3` sources and targets with
`E_i` contained in `H_j` exactly when `i != j`, as above. Consider any finite
linear circuit with these conditions:

1. The `X_i` values are independent source variables and are not modified.
   A source frame can grow when the source is read.
2. Targets start with independent arbitrary values at frame zero. Each
   target must acquire a nonzero coefficient of every other source.
3. Every two-register operation lifts both registers to a common frame
   containing their previous frames. Frames never shrink, and target `Y_i`
   must stay inside `H_i`.
4. Apart from source reads `X_i -> Y_j`, operations may rescale targets or
   mix the targets of one unordered pair `{a,b}`. There are no additional
   carriers. Other target-to-target operations are allowed only as
   source-free preconditioning at frame zero.

Then the pair cannot interact after either target has accessed a source.
This excludes a shared partial sum and a two-target basis-change circuit,
including repeated interactions interleaved with source reads.

Suppose otherwise. Let `T` be the last interaction of the pair. Since an
earlier interaction followed source access, at `T` both target frames
contain some `E_k`. Necessarily `k` differs from `a` and `b`, since the
common frame must fit both target caps.

`Y_b` still requires `X_a`. Its paired target `Y_a` can never read `X_a`,
and no other target can supply it under condition 4. Thus a direct read
`A: X_a -> Y_b` is required. It must occur **after T**: an earlier read
would put `E_a` into the common frame at `T`, violating `Y_a`'s cap.
Likewise a direct read `B: X_b -> Y_a` must occur after `T`.

At `A`, source `X_a` acquires `E_k` from `Y_b`. It cannot subsequently
be read by `Y_k`. Hence the required direct read `C: X_a -> Y_k` occurs
before `A`. Similarly `D: X_b -> Y_k` occurs before `B`.

If `C` precedes `D`, the read at `D` puts `E_a` into the frame of `X_b`.
That forbids its later required read `B` into `Y_a`. If `D` precedes `C`,
the read at `C` puts `E_b` into `X_a`, forbidding its later read `A` into
`Y_b`. Both strict orders are impossible.

Cancellation, rescaling and repeated reads cannot remove a frame already
acquired. Earlier reads or extra frame promotions only add restrictions.
The five-event checker explicitly examines all 120 strict orders; 16 satisfy
the four required precedences, and the two contradictions reject eight each.

## A three-source escape and controls

Use three sources and targets, where `Y_i` needs the other two sources.
Introduce dirty helpers `H0,H1`. At frame zero, apply

```text
Y1 -= Y0; Y0 -= H1; Y1 += H1; Y1 -= H0.
```

Then run these operations at the joins of their current frames:

```text
H0 += X0; H1 += X1;
Y0 += X2; Y1 += Y0;
Y0 += H1; Y1 += H0;
Y2 += X0; Y2 += X1.
```

Climb every source and helper to the full nine-dimensional frame and each
target to its own cap. Restore `H1 -= X1; H0 -= X0` at the full frame.
Exact rational replay checks all eight arbitrary input columns in both
forward and inverse-transpose orientations. The helpers retain their original
dirty values. Omitting cleanup or compensation, or doubling the shared read,
is rejected.

The escape's profile is `6 H1 + 5 H2 + 3 H5 + 3 H6 + 2 H7`.
A direct six-read circuit with the same two helpers left idle has profile
`6 H1 + 3 H2 + 3 H5 + 3 H6 + 2 H9`. Both have rank mass 63. Their difference is

```text
2 H2 + 2 H7 - 2 H9.
```

For the recursive moment `sum_r H_r r^s`, every `0 < s < 1` gives a strict
loss: `2^s + 7^s > 9^s`. Thus the added carriers are not free in this control.
This is a local comparison with fixed stock and unchanged surrounding work;
it does not assert a new globally hosted supplier or an outer exponent.

A second positive control drops one required off-diagonal entry. It admits
the formerly blocked target broadcast, showing why the all-but-one demand
is part of the proposition rather than a dispensable assumption.

## Relation to prior work and limits

[PR #651](https://github.com/CrocSwap/integer-mult-bounds/pull/651) studies
raw-face sharing and target hosting with an own-first
restriction. This argument permits own-read movement and repeated coded
operations on one target pair.
[PR #683](https://github.com/CrocSwap/integer-mult-bounds/pull/683) studies mixed K/M bypass with pure
carriers; this package concerns all-K cells and a target-pair mechanism.
Neither those broader titles nor the present proposition establishes a
barrier for arbitrary network coding.

The analytic proposition does not cover additional carriers, mutable source
values, source-dependent coupling through three or more targets, register
lifetime resets, different decoder demands, or different geometry. The
positive event model covers broader target coupling under narrower coefficient
restrictions. Neither establishes a barrier for arbitrary network coding.
The one-helper construction and the three-source two-carrier control do not
establish optimal profiles or a helper minimum for general linear circuits.

The [local claim](CLAIM.json) records the draw and candidate selection.
[SEARCH-LOG.md](SEARCH-LOG.md) records the earlier timeouts and the event-model
follow-up; [SEARCH-RESULTS.json](SEARCH-RESULTS.json) retains the solver receipts.
Those searches are not dependencies of the analytic proof or standard checker.
The [source pins](SOURCE-PINS.json), [exact finite evidence](EXPECTED.json) and
[attribution](NOTICE.md) accompany this note.
No selected certificate, existing supplier or `upstream/` source is changed.
All inherited all-size, physical realization and analytic assumptions remain.
This is not a complete formal proof of integer multiplication.
