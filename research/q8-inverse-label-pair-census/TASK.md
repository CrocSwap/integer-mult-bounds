# Task card (autoresearch.md section 3)

Task ID / proposed scope key: `bit-new-register-model` (OS draw, nonce
`8fc01583fcbd95feac4206b7bfb68f7d`); refined scope key
`q8-inverse-label-pair-census`.

Base commit; exact predecessor and dependency heads: base main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; predecessors
`research/q8-central-commutator-pair` (https://github.com/CrocSwap/integer-mult-bounds/pull/1822,
head `ee736b4b`) and `research/q8-mixed-three-register-seedcbd5ebc4` (both merged
at this base). Concurrent open https://github.com/CrocSwap/integer-mult-bounds/pull/2248
(head `835bd7b1`) is read for scope only; it is not an input.

Concrete object and question: in the formal `F2[Q8]` register model at `r = 2`
with **unit-priced inverse labels** `x, x^-1, y, y^-1` (24 paid factors = 6
binary rank-one idempotents x 4 labels), what is the exact paid-call minimum of
each of the 64 ordered diagonal pair targets `diag([g1],[g2])`? The
predecessor's named endpoints `diag([z],[z])` and `diag([xy],[yx])` are members
of this family. Comparison baseline: the same complete pair table under the
positive label set `{x, y}` (12 factors).

Scope status: **refined**. Reason: the drawn generic card is saturated and the
pair-collision/overlap checks showed the neighbouring Q8 objects claimed or
completed in the last hours (discussion 1317 October 14 line; discussion 2243 /
https://github.com/CrocSwap/integer-mult-bounds/pull/2248 for the `r = 3`
three-role positive-label minima; discussion 2300 /
https://github.com/CrocSwap/integer-mult-bounds/pull/2303 for `diag(i,j,k)`
two-factor words). The chosen object is open question 1 of the merged
predecessor package's `Open next questions` ("does a label set including the
inverses compress any pair target?"), extended from its two named endpoints to
the complete pair family. The predecessor's open question 2
(`diag([z],[z],[z])` at `r = 3`) is **not** taken: it is covered under positive
labels by the concurrent PR above.

Existing restriction being changed (or exact claim being audited): the paid
label set of the predecessor is `{x, y}` with inverses priced as three calls.
This card prices `x^-1, y^-1` at one call each, which changes word-length
pricing and makes the factor set closed under inversion
(`D_N(g)^-1 = D_N(g^-1)`, verified). Counted roles: exactly `r = 2`, both
registers arbitrary dirty inputs, endpoint restored exactly in the formal
group algebra; no COPY/ERASE, no clean ancilla, no free address maps.

Method; explicit parameter ranges/candidate alphabet: complete BFS of the
formal matrix monoid `M_2(F2[Q8])` to depth 3 (all distinct states), 24
generators (inverse alphabet) and 12 (positive alphabet); acceptance is
equality in all eight group-algebra coefficients (a uniform identity on
arbitrary dirty inputs), never a finite-column test. Pairs whose direct bill
reaches 5-6 in the positive alphabet are settled by an invertible-factor
meet-in-the-middle (prefix ball <= 2, suffix ball <= 3). Every minimum is
attained by a replayed word. Two independently written engines (bitmask
convolution vs frozenset/Hamilton-quaternion arithmetic) must agree on the
group table, every layer digest and every witness.

Nearest overlapping PRs and why this adds something:
https://github.com/CrocSwap/integer-mult-bounds/pull/1822 settles only three
endpoints under positive labels; https://github.com/CrocSwap/integer-mult-bounds/pull/2248
settles `r = 3` triples under positive labels; discussion 2300 /
https://github.com/CrocSwap/integer-mult-bounds/pull/2303 checks one- and
two-factor words at `r = 3` with all-nonidentity labels. No located work gives
the `r = 2` pair table under inverse pricing, and no located work completes the
64-pair positive-label table.

Optimistic full cost budget; required observable improvement: none — this is a
complete local census in the unit-cost formal call model, no supplier profile,
no paid reserve, no kappa. The `a < D/E` moment diagnostic does not apply (no
candidate improvement is priced; the scalar-cost relaxation here is more
optimistic than any physical invoice).

Success evidence; falsification test; time/compute cap: exact minima for all
64 pairs in both alphabets with attainment words and complete exclusion of all
shorter words (layer digests + MITM receipt); falsifier is any word shorter
than a recorded minimum (engine disagreement or an omission/mutation control
passing would falsify the harness); 45-minute budget, stdlib Python only.

Predecessor authors; intended artifact and reproduction command: eumemic
(PR 288 section 1.2 model), woklerx (`research/bit-dihedral-commutator`), Aaron
Wang / navinor (`research/q8-central-commutator-pair`); artifact
`research/q8-inverse-label-pair-census/`; reproduction:
`python3.12 -I -B research/q8-inverse-label-pair-census/verify.py`.
