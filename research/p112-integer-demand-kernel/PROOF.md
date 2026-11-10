# Exact integer projection of the fixed P112 demand system

The source matrix has 280 distinct nonempty 14-bit masks `H_t`, each with integer
demand `1 <= d_t <= 8`. Its row is `sum_(k in H_t) x_k >= d_t`. This proof fixes
the common domain `x in Z^14`, `x >= 0`, with no upper bounds. Source objects are
authenticated before parsing. The original clique census and geometry-to-demand
equivalence remain credited PR6425 premises, not new replays.

## Complete finite projection of a counterexample

An integer vector violating target `(I,d)` has

    sum_(k in I) x_k <= d-1 <= 7.

Thus its inside coordinates are one of the finitely many weak compositions with
total at most `B=d-1`. This is a consequence of a target violation, not an assumed
global bound on multiplicities.

For any such inside assignment, set every coordinate outside `I` to 8. Every
other source row either has support contained in `I`, or has an outside bit. The
latter row has LHS at least 8 and hence satisfies its demand. Distinct masks mean
that a different row contained in `I` is a **proper** subset row. Consequently a
global integer counterexample to the target exists if and only if one of the
inside weak compositions satisfies every proper-subset source row.

The forward implication follows by restricting any global counterexample. For
the reverse, extend by 8 as above. Each resulting full vector is nevertheless
checked literally against all 279 other original rows before acceptance as a
separating point. No inference from a partial point or solver status is used.

## Enumeration and coverage

For `k=|I|`, the number of nonnegative inside vectors of total at most `B` is

    binomial(k+B,k).

Introduce a slack coordinate equal to `B - sum inside` to obtain ordinary weak
compositions of exactly `B` into `k+1` parts. Stars and bars gives this count.

The primary traverses coordinate multisets of each total `0..B`; counting the
multiplicity of each coordinate is a bijection to the inside vectors. The
separate checker uses an iterative vector-budget tree: at each coordinate assign
an integer from zero through the remaining budget, then continue with the
remainder. At depth `k`, each inside vector occurs exactly once; leftover budget
is the implicit slack. These are distinct executable enumerations of the same
complete domain.

For a negative classification, every profile must be visited and fail at least
one proper-subset source inequality. The exact closed-form count and the
histogram of the first failing row are checked. The count or histogram alone is
not the proof of exhaustive rejection: both implementations regenerate all
profiles, and the enumeration bijections justify coverage. Positive search may
stop early only after producing an actual full integer separating point.
Capacity exhaustion is UNKNOWN and nonzero; it must not produce a complete
minimum certificate.

## One integer-only implication

One concrete integer-only deletion illustrates the domain change. Target
`0x1ada` has demand 5. One half of each source row `0x5a` (demand 4), `0x1a98`
(demand 3), and `0x1ac2` (demand 2) has **exactly** the target coefficient vector
and RHS `9/2`. Hence its integer LHS is at least `ceil(9/2)=5`. The corresponding
real-domain separator from PR6455 has target LHS `9/2` and satisfies the other
279 rows, so deleting this row over the reals would be unsound. The new complete
projection independently checks all 495 inside integer profiles for this target.
The half-sum/rounding example is explanatory; the full result uses complete
negative projections and literal integer separating points.

## Reused predecessor evidence

PR6455 already supplied 43 exact real-domain deletion certificates and 134
integral separating points. These are validated as data and credited, not new
integer discoveries. Each reused deletion is checked as a nonnegative rational
combination of proper-subset source rows whose coefficient vector is at most
the target and whose RHS is at least its demand. Each reused integral point is
parsed as integral/nonnegative and rechecked against all 279 other original
rows. The new classification resolves the remaining 103 labels.

No predecessor executable, LP solver or 262,928-clique census is imported or
replayed. The earlier real minimum gives a 237-row candidate integer system;
the 134 literal integral points force at least those 134 rows. These are existing
coverage bounds, not the new answer.

## Joint deletion and the restricted integer minimum

Let `R` be the new retained rows. Every deleted row is justified either by a
reused rational implication or by exhaustive rejection of its finite inside
counterexample domain. Both types use only proper-subset original rows as
premises. Induct on support cardinality: an integer solution of `R` satisfies
each earlier proper-subset row, whether retained or already implied. The rational
implication then establishes a reused target. For a new negative target, a
violation would give a visited profile failing one of those already-established
proper-subset rows, a contradiction. Therefore every integer solution of `R`
satisfies all original rows. The converse is immediate because `R` is a
subfamily. Simultaneous deletion has no circular premises.

Every retained row has a full nonnegative integer point satisfying all 279
other originals and violating that row. Any original-row subfamily equivalent
to the full integer system must contain that row, since otherwise this point
would satisfy the subfamily. Hence, once all classifications and witnesses pass,
`R` is the unique minimum-cardinality and unique inclusion-minimal equivalent
**subfamily of the original 280 inequalities** over the integer orthant.

This does not minimize arbitrary new inequalities. The minimum claim concerns
unrestricted integer multiplicities: its witness points need not satisfy an
additional cost/COPY budget or multiplicity cap. The all-orthant equivalence can
still be conjoined with any identical additional constraints on both systems;
the minimum property itself need not persist in that restricted domain.

## Scope and credit

This is a source-bound necessary-condition screen. Integer separating points
are inequality counterexamples, not decoders or physical call constructions.
Changed supports require a new matrix and extension bound. Coefficients, full
decoder/COPY pricing, native/access/dirty restoration/precision/tape/stock/compiler
and outer admission remain outside scope; no κ or frontier change follows.

Credit Nick Petalas/PR6425, Jeremy Diviney/PR1422, Cinna Davis/PR1347/1323 and the
retained E8/label/decoder lineage. Credit ToikY with OpenAI Codex/PR6455 for the
real certificates, literal integral points and explicit integer-domain question.
Weak compositions, monotonicity and finite integer implication are classical.
New code/proof uses substantial OpenAI Codex assistance. Separate AI checking
does not constitute human or formal proof-kernel acceptance.
