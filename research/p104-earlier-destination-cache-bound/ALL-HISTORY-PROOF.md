# Every original same-coframe MOVE is an innovation

The sole primary input is exact #7481 WORD.json.gz, SHA256
`acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`,
canonical payload `64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8`.
The independent engine reads no root prototype, precomputed ROWS receipt,
prior target rows or prior history generators. It freshly interprets all
76,475 instructions using sparse exact rational rows for all1,501 public
inputs and68 owned slots. Charts, strict native nesting, ownership flags,
coframed contacts, fresh COPY, lifetimes and endpoints are checked.

## Complete final matrices imply every prefix innovation

For each coframe, collect all original public initial rows in that coframe
and every MOVE arrival row in chronological order. Exact normalized MOVE
transport preserves the latent rational row, so its pre-MOVE target row is
the row appended at its destination. There are1,501 initial rows plus6,279
arrivals,7,780 total, across979 nonempty coframe classes. The largest final
matrices have1,060 rows(frame3) and1,052 rows(frame127).

The fresh exact-Q matrices are certified full ROW rank by a distinct
prime1000033 and sparse COLUMN elimination. The prime is verified by
exhaustive trial division. All575,804 stored rational entries have
invertible denominators at this prime; there are46 distinct denominators.
Every final matrix has modular rank equal to its literal row count.
Nonzero pivots supply a full-size nonzero minor over the prime field.
Because all rational denominators are invertible, the same minor is
nonzero over Q. Thus each exact rational final matrix has full row rank.
This is a full-rank certificate, not a modular nonmembership heuristic.

Every chronological prefix is a subset of an independent final row set.
Consequently every one of the6,279 original MOVE targets lies outside its
strictly earlier destination history. Initials precede all events; a
candidate's own arrival is never included in its earlier history.

Current same-coframe values remain in this history span: ADD/COPY/SCALE
form linear combinations; zero INIT adds no information; CLEAR or moving
out removes fields; each new arrival is recorded. The pool keeps every
historical value as if storage and normalization were free. This is more
information than an actual same-coframe cache need have. Phase/frame
aliases are overgranted normalized equivalences; no new physical adapter
admission is inferred. In this source the nonidentical alias1092 is unused.

## Fresh maximal-neutral certificate

The engine derives the neutral helper set from its own exact replay. A
helper is selected exactly when it has one singleton pure MOVE with paid
rank equal to its original target rank. The72 helpers and72 events are
freshly determined; no external neutral list is needed.

Set all72 helper inputs to zero. Exactly144 observations vanish:72 initial
unit rows and72 MOVE arrivals. Every vanishing row is a nonzero multiple
of a SINGLE neutral-coordinate unit. Within each coframe these units have
distinct helper coordinates. All other rows remain nonzero. The projected
final matrices, after deleting exactly those144 zero rows, are independently
certified full row rank at the same distinct prime:7,636 rows total.
Thus all6,207 remaining nonzero MOVE targets are strict innovations under
the maximal restriction.

The exact source paid/target histogram for the72 zero MOVEs is pointwise
identical: {1:12,2:8,3:24,4:4,5:18,6:1,7:4,8:1}. Every selected helper has
exactly one such occurrence. The initial observations have no MOVE credit.

## Unit-extension lemma covers all2^72 subsets

Fix any subset S of the neutral set N. In a coframe, divide the unrestricted
rows into general rows w_i whose maximal projections pi_N(w_i) are nonzero,
and maximally zero rows c_h e_h, with distinct h in that coframe. Under S,
the remaining row family is

    pi_S(w_i), together with c_h e_h for h in N minus S.

Suppose a linear combination vanishes. Project further by pi_N. The unit
terms disappear and the certified independent pi_N(w_i) force every general
coefficient to zero. The remaining distinct coordinate units are independent,
so their coefficients also vanish. Therefore every subset-restricted final
coframe matrix, after deleting its actual zero rows, has full row rank.

There are exactly|S| zero MOVEs and|S| zero initial rows: total nonzero row
rank7,780-2|S| and nonzero MOVE count6,279-|S|. All of those nonzero MOVE
targets are outside their earlier destination histories, at every public
AND owned cut. This is a proof for all subsets, not a finite subset census.
Pointwise zero-MOVE credit cancels the matching helper target debit for
every S. No extra nonzero cached deletion is enabled.

Maximal-restriction nonmembership alone would NOT suffice. The explicit
counterexample history x+y,target x with N={x,y} has independent full rows
and no nonzero maximal projected rows, but zeroing only y enables the
nonzero target. Its maximally zero history is not a coordinate unit. The
production unit classifier rejects this control. Full original independence
and the distinct-unit property are retained as explicit hypotheses/data.

## Any deterministic processing of these histories

On the remaining arbitrary input field coordinates, a linear target outside
the history row span has an input direction annihilating every history row
but not the target. Compare that assignment with zero input: identical
histories, different targets. Therefore no deterministic function of those
histories, linear or nonlinear, recovers that nonzero target. For arbitrary
finite arrays, choose this scalar input direction times one nonzero entry
vector; all observed arrays remain zero and the target array differs.
No native tariff or dimension scaling is introduced.

This scope uses arbitrary retained field inputs with coordinate-zero
restrictions. Finite-grid-only digit decoding, arbitrary nonlinear helper
promises, imported other-coframe information, changed operations/frames,
changed providers, partially cached jobs and newly decoded target types are
outside this result. Physical public zero reframe, allocation and complete
supplier admission remain separate. No changed source or kappa is claimed.

## Reproduction and controls

The package verify.py runs both the incremental prime1000003 engine and this
independent exact-Q/final-matrix column engine at prime1000033. Both freshly
derive the72 helpers and72 zero MOVE events from the primary source. The
independent core all_history_independent.py also exposes verify(source) and
controls(), both read-only. To reproduce the complete per-coframe pivot
certificates without saving them inside the package:

```sh
python3 -I -W error -B research/p104-earlier-destination-cache-bound/all_history_independent.py research/p104-earlier-destination-cache-bound/inputs/WORD.json.gz
```

The full output contains every row label, exact rational matrix hash, zero-unit
record and modular pivot-column certificate. The main package checker reports
a compact digest and compares the two methods' complete counts, neutral sets,
zero-event lists and price histograms. Matrices are rebuilt from source rather
than stored as another large input snapshot.

The independent controls include126 dense-row/sparse-column rank comparisons
and seven rejected failures: invalid prime/denominator, duplicate rows, naive
modular nonmembership after rank loss, missing zero-row deletion, repeated zero
units and the x+y all-subsets pitfall. The author engine checks every strict
cut before arrival and all6279 membership controls after the arrival, plus its
own rank-drop and nonunit counterexamples. Both reject altered source bytes.
All tests use explicit exceptions that remain active under python -O.

The universal all-subsets and deterministic-provider conclusions follow from
the written proofs above, not the finite toy controls. VALIDATION.json records
executed normal/optimized and read-only Git-free export checks. Prepared for
Jerry Chen / @CubeJerry with substantial OpenAI assistance, retained source
credit, and no independent human or formal-kernel acceptance.
