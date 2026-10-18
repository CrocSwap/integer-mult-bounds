# A complete rational rank-cut screen before scalar-word search

This package decides **all rational linear projection/rank cuts** for a bounded
input of paid rational frames and diagonal target frames. A rejection includes
an exact integer functional and every evaluated label. Passing establishes only
these necessary inequalities, not an identity, feasible supplier or new kappa.

The contribution is the finite coverage argument and reusable checker. The
projection/rank inequality is inherited from Ali Romman's
[three-register proof, section 2](../bit-three-register-lower-bound/README.md),
[PR468](https://github.com/CrocSwap/integer-mult-bounds/pull/468), head
`07a78bf335b0b5039a1fecd7cd74a0fe1d1605ea`. This screen is independent of the
number of scalar registers and the order or choice of their rank-one couplings.

The motivating [four-role example](https://github.com/CrocSwap/integer-mult-bounds/discussions/2200#discussioncomment-18936190)
was rejected by hand before a proposed search over eight scalar factors with
120 choices each. Its eight paid frames generate only 16 distinct subspaces.
The new checker rejects it with two surviving paid factors against three
nonidentity target roles. All nine coordinate-only cuts pass. The package also
checks the discussion's simpler functional `ell(X) = X11 - X12`, using one-based
indices. The example and its rejection belong to that predecessor.

## Model and inherited necessary inequality

Let the address space be `V = M_d(Q)`. In the formal additive group algebra
over `F2`, a paid factor is

`P_j = I + ([A_j] - 1) N_j`,

where `A_j` is a nonzero rank-one rational matrix and `N_j` is a binary
rank-one matrix on the scalar roles. The reversible idempotent model is
included. The claimed endpoint is `diag([C_1], ..., [C_w], 1, ..., 1)`.
Targets may repeat, may be singular, or may be zero. Zero targets and any
additional restored dirty roles contribute zero to the cut. No free address
maps between factors are admitted. Free scalar basis changes are covered
when normalized into these factors with identity residual scalar map, as
forced by augmentation at this endpoint.

For any rational linear functional `ell: V -> Q`, applying `[A] -> [ell(A)]`
is an algebra homomorphism. Clear the finitely many rational denominators and
work over the fraction field of `F2[t, t^-1]`. A nonzero exponent gives a
nonzero `t^k - 1`, even when `k` is negative or even. Rational frame entries
are never reduced modulo two.

Each projected paid factor differs from identity by rank at most one, and by
rank zero when `ell(A_j)=0`. Telescoping the product and applying rank
subadditivity gives the inherited inequality

`#{j: ell(A_j) != 0} >= #{i: ell(C_i) != 0}`.

The right side is the exact rank of the diagonal target minus identity over
that fraction field. Repeated target labels retain their full multiplicity.
Thus a violating functional excludes every factor order and every allowed
scalar coupling, with any finite number of extra restored dirty roles. It
does not exclude changed address alphabets or endpoints.

## Why finitely many paid spans cover every rational cut

For any span `S` of a subset of the paid frames, define

`m(S) = #{j: A_j not in S} - #{i: C_i not in S}`.

**Coverage.** Given any `ell`, let `S` be the span of the paid frames it kills.
A paid frame lies in `S` exactly when `ell` kills it. Every target in `S`
is killed too, so `m(S)` is at most the margin of the original cut. Hence
any violated cut produces a negative paid-span margin.

**Attainment.** Conversely, choose a functional in the annihilator of `S`
that is nonzero on every paid and target vector outside `S`. Such a
functional exists over `Q`, since a finite union of proper hyperplanes
cannot cover the annihilator. It realizes margin exactly `m(S)`. When `S`
is the whole address space, the zero functional realizes its zero margin.

Consequently the minimum cut margin equals the minimum paid-span margin.
There are at most `2^n` paid-subset spans. The checker builds their canonical
rational reduced row bases incrementally and deduplicates spans, while
retaining all paid and target occurrences in the counts. This proves coverage
of all rational functionals, without bounding their coefficients.

For a negative margin, the implementation constructs the separating functional
without random search. For an annihilator basis `b_0,...,b_(q-1)`, set
`ell_t = sum t^k b_k`. Each of the `B` outside occurrences excludes at most
`q-1` integer values of `t`. One of `0,...,B(q-1)` works. Clearing denominators
and dividing by the integer gcd preserves every zero and nonzero evaluation.
The emitted witness is then checked against the actual margin.

These are written proofs supported by exact finite checks, not proof-assistant
formalization. The algorithm proves completeness for this family of cuts only.

## Run the checker

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -B research/bit-rational-rank-cut-screen/verify.py --input research/bit-rational-rank-cut-screen/EXAMPLE.json
```

The example intentionally exits **1** with `REJECT_RATIONAL_RANK_CUT`, margin
`-1`, 16 checked spans and a witness with `paid_nonzero=2`, `target_nonzero=3`.
Exit 0 means `PASS_NECESSARY_CUTS_ONLY`. Invalid inputs or failed checks exit 2.
JSON has exactly `address_dimension`, `paid_frames` and `target_frames`.
Matrices are square row lists. Entries are integers or rational strings such
as `"-3/5"`; floats and booleans are rejected.

The CLI accepts address dimensions 1 through 4, zero through 12 paid frames,
and 1 through 12 target roles. Reduced entry numerators in absolute value and
denominators are at most 65,535; rational strings are at most 13 characters.
Input files are at most 65,536 bytes. These are implementation capacity limits,
not hypotheses needed by the mathematical coverage proof.

To reproduce this package's evidence and source pins:

```sh
python3.12 -I -O -B research/bit-rational-rank-cut-screen/verify.py
python3.12 -I -B research/bit-rational-rank-cut-screen/cli_controls.py
python3.12 -I -B scripts/research_package.py --package research/bit-rational-rank-cut-screen --check-only
python3.12 -I -B scripts/research_package.py --package research/bit-rational-rank-cut-screen
```

Expected direct replay:

```text
PASS_RATIONAL_RANK_CUT_SCREEN oracle_cases=525 invalid_controls=17 example=2<3 no_new_kappa
```

Normal replay is read-only. `--write` regenerates only `RESULT.json`. The
registered command pins the inherited mathematical source; the CLI itself
needs only the new verifier and its input, and imports no predecessor code.

## Evidence and limits

`RESULT.json` retains the exact example witness and verification counts.
The independent oracle tests every paid multiset of size at most three from
the four directions `(1,0),(0,1),(1,1),(1,-1)`, and every two-target multiset
from those directions plus zero. All 525 cases agree with direct enumeration
of 169 actual integer functionals in `[-6,6]^2`. Each vector is embedded in
the first row of a 2-by-2 address matrix. This oracle uses literal integer
dot products, not the row-space or annihilator implementation.

The integer box covers every cut pattern in that small domain. A paid line
has a normal with coefficients at most one. The zero paid span has a generic
normal `(1,t)` for some `0 <= t <= n+w <= 5`, avoiding all nonzero paid and
target vectors. The whole plane is represented by the zero functional.

The nine-call direct construction passes. Removing a call rejects. Corrupting
the output witness rejects. Rational signs, fractional values, repeated target
roles, zero paid count, even exponents and maximum accepted input shape are
checked. Seventeen malformed-input controls cover rank, shape, types, capacity,
denominators, duplicate JSON keys and excessive JSON nesting. Two receipt
mutants check that booleans and floating-point numbers cannot replace integer
fields. No check relies on Python assertions. `cli_controls.py` checks actual
subprocess exit codes, malformed and missing files, read-only behavior and
both receipt mutations in disposable package copies.

Passing is explicitly insufficient: scalar paid labels `1,1` and target label
`3` pass every cut. They cannot realize the target because their determinant
exponent is at most 2 instead of 3. A binary rank-one coupling has trace
zero or one, so each factor determinant is either 1 or `[1]`. The package
checks that the screen passes this impossible instance. The separate
determinant argument explains why passing is not a construction certificate.

The checker does not test determinant equality, full formal coefficients,
native operations, physical ownership/movement, restoration implementations,
precision/tape, recursive bills or the selected cold replay. It does not
replace the stronger three-register theorem or screen nonabelian group words.
The selected frontier is unchanged.

## Implementation review

Build the Lever led to a reusable CLI. Prove It Works led to the
independent integer-functional oracle,
literal witness checks and failure controls.

Power of Ten review is scoped to this package's two Python files. Control flow
is nonrecursive; functions stay below 60 lines. Loops are bounded by the validated matrix sizes,
at most 4,096 spans, or the fixed oracle domain. Witness search has at most
`24 * 15 + 1 = 361` trials. State is local except immutable capacity constants.
Input failures use checked exceptions and all files have scoped lifetimes.
There is no code generation or dynamic import. Library callbacks have fixed
local targets. Exact Fraction arithmetic and runtime invariant checks stay
enabled under optimization.

Rule 3 deviation, `verify.py`: Python and Fraction allocate during execution.
The scope is this finite command. The input limits bound current and temporary
span sets to fewer than two million rational coefficient slots, with bounded
coefficient sizes; the registered replay has a 120-second timeout. The
12-independent-frame capacity probe reaches all 4,096 spans. Direct CLI
capacity does not imply a latency guarantee. A fixed-memory implementation
would be needed before embedding this in a steady service. `cli_controls.py`
uses one temporary directory and sequential subprocesses, each with a
30-second timeout and a checked return code. Rule 10 uses the documented
warning, compilation and lint commands recorded in `TASK.json`; changing
repository-wide diagnostics is outside this package's scope.

## Open next questions

Can a proposed larger-register candidate pass both this complete rational
rank-cut screen and determinant equality, then realize its full formal
endpoint? Start by saving the exact candidate JSON and its screen output,
then examine scalar couplings only if both necessary conditions pass. For
idempotent couplings, determinant equality is `sum A_j = sum C_i`; allowing
nilpotent couplings requires the corresponding subset-sum condition. The
missing candidate and its full cost, including a native caller, are blockers.
There is no justification here for expanding an unchanged scalar search.
The structured question is in [TASK.json](TASK.json).

## Credit

Nick Petalas. Substantial AI assistance was used for derivation, implementation,
internal independent checks and writing. No independent human review is claimed.
New material is under the repository's Apache-2.0 license.

Ali Romman supplied the retained projection/rank method and three-register
theorem in PR468, with eumemic's PR288 and huxint's PR203 lineage credited in
that source. `1337isnot1337` supplied the eight-frame example and its explicit
projection rejection in Discussion2200. Their claims and source files remain
unchanged. No new projection inequality or literature priority is claimed.
