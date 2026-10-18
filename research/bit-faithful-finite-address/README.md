# When a finite-address replay certifies a bounded formal identity

A finite-address identity alone does not prove a rational-frame group-algebra
identity. For a **fixed finite word with a certified support bound**, however,
an explicitly injective cyclic quotient makes a complete finite replay decisive.
This note supplies that criterion, a fail-closed implementation and separately
implemented formal/regular-action checks on both retained three-register fixtures.
It is a verification side result, not a new register mechanism or a new bound.

## Exact criterion and proof

Clear a common denominator from all rational frame entries and target frames.
This embeds their generated group in Z^d; do not reduce rational entries modulo
two. For a product of factors I+([A_j]-1)N_j, every exponent is a subset sum of
the A_j. Form S from all such sums and all target exponents (including zero).
Let coordinate i range from lo_i through hi_i on S, with width b_i=hi_i-lo_i.
Define mixed-radix weights w_0=1, w_i=product_{k<i}(b_k+1), and
q=product_i(b_i+1). The additive homomorphism phi(a)=sum_i w_i a_i mod q is
injective on S. Indeed subtracting the constant lo vector gives ordinary unique
mixed-radix digits in [0,b_i], with encoding in [0,q-1].

The finite difference between candidate and target has support within S. Its
image in F2[Z/q] vanishes iff each original matrix coefficient vanishes, because
distinct support exponents have distinct residues. Finally the regular action
of F2[Z/q] is faithful: applying an element to the unit vector at0 recovers its
coefficient vector. Checking all role/address columns therefore proves exactly
the original formal identity. No primality, random evaluation, floating point,
or probabilistic polynomial-identity test is used. Negative coordinates are
allowed; clearing denominators is an injective group rescaling, not scalar-field
reduction. The bound may be exponentially large and is not a runtime promise.

## Source-bound evidence

The pinned `bit-three-register-lower-bound/controls.py` supplies the nine-call
full-rank fixture and the eight-call noncommuting rank-two control. Scalar codes
are read from its AST; no source verifier is imported. The new formal product
engine and cyclic bitset-permutation engine share literal fixtures only.

| fixture | subset support | safe cyclic size | full role/address columns |
| --- | ---: | ---: | ---: |
| nine-call identity |64|64|192|
| eight-call noncommuting rank-two |162|432|1296|

Doubling the first frame of each fixture is rejected by both engines using a
freshly recomputed support bound. Ten unsafe quotient controls, q=2..11, replace
the first rank-one frame E00 by(q+1)E00. Each passes its unfaithful quotient but
fails the formal identity and the recomputed faithful quotient. The q=2 warning
already appears in the predecessor and is credited, not presented as discovery.
The added result is the sufficient bound and exact finite certification path.

## Reproduce and limits

`python -I -O -B research/bit-faithful-finite-address/verify.py`

The verifier checks source pins, support injection, all finite regular-action
columns, independent formal coefficients, mutations and aliases. Python3.12
registered replay and selected integrity pass. This does not rerun the full
21-million-word predecessor exclusion, establish an actual compiler realization,
or replace native/precision/hosting/analytic obligations. The finite cyclic space
is an algebraic certificate representation, not a proposed multiplication tape.
The scope change from new-register synthesis is explicit in TASK.json: the
boundary between finite tests and a uniform identity is audited first.

## Open next questions

Can exact collision analysis choose a substantially smaller faithful cyclic
quotient than the box bound for a genuinely larger-register candidate? First
retain all subset sums and search short integer weights, rejecting every collision.
Exponential support enumeration is the blocker; heuristic fingerprints alone
cannot substitute for the injection check.

## Credit

The two fixtures and torsion warning are from the retained three-register bound,
which credits eumemic PR288 and huxint PR203. The mixed-radix injection and faithful
regular representation are standard algebra, applied here to this verifier need;
no literature-priority claim. Prepared by woklerx with substantial OpenAI Codex
assistance. Apache-2.0. Cached overlap limits are recorded in OVERLAP.json.
