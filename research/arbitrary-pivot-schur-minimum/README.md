# Exact Schur dimension for arbitrary invertible block pivots

Krzysztof Wojt, with substantial OpenAI Codex assistance and a bounded Luna
subagent for the separate binary checker. New work: Apache-2.0.

For any field K, any d >= 1, arbitrary invertible d-by-d matrices A,B and
arbitrary H, the least dimension of commuting idempotents P,Q with
`P11=A`, `Q11=B`, `(PQ)11=H` whose Schur complements have commutator rank
`2d` is exactly

```
n_min = 3d + rank(I-A-B+H)
           + nullity(A-H) + nullity(B-H) + nullity(H).
```

The matrices A,B,H need not commute. [PROOF.md](PROOF.md) proves the lower
bound and constructs a pair attaining it over every field. It also gives
the simultaneous minimum input ranks

```
rank P = 2d + nullity(A-H) + nullity(H),
rank Q = 2d + nullity(B-H) + nullity(H).
```

The new step is extending the six-map criterion from scalar pivots to
arbitrary invertible pivots, with the matrix order retained throughout.
This resolves Open next question 1 of both
[#4774](https://github.com/CrocSwap/integer-mult-bounds/pull/4774) and
[#4785](https://github.com/CrocSwap/integer-mult-bounds/pull/4785), and goes
beyond their unequal-scalar-block question. The ordered Schur factorization
itself is the existing result of
[#4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597).
This package is a new theorem and construction, not a replication of those
predecessors. [Claim and coordination: #5121](https://github.com/CrocSwap/integer-mult-bounds/discussions/5121).

## Scope and evidence

The proof is universal; the computations are finite corroboration. The
standard-library exact constructor [verify.py](verify.py) checks:

* All 576 ordered triples `A,B in GL_2(F_2), H in M_2(F_2)`.
* 648 ternary triples: eight explicitly enumerated noncommuting pivot pairs,
  each with all 81 choices of H.
* 162 further structured cases over F_2, F_3, F_5, F_7 and Q, in dimensions
  d=2,3,4. These include noncommuting pivots and singular compressed products.
* The idempotence and commutation of the full matrices, all three prescribed
  blocks, literal Schur complements, the ordered factor identity, sector
  dimensions, input and residual ranks, and the exact minimum formula.
* Six controls with one active X or Y map deficient, two singular-pivot
  rejections, and factor-order mutations. Swapping the H and B-inverse
  factors in either ordered factor is detected on 1,017 cases.

This is 1,386 constructed cases, plus two explicit noncommuting rational and
ternary examples and the deficient-map controls. The rational example uses

```
A=[[2,1],[0,2]], B=[[2,0],[1,2]], H=[[3,1],[1,3]],
```

and attains n=6, input ranks 4 and Schur-commutator rank 4. All three pairwise
commutators of A,B,H are nonzero. The same example works modulo three.

[binary_check.py](binary_check.py) independently implements raw matrix
arithmetic with bitsets. It imports no primary-verifier code and reads the
576 complete matrix fixtures in [FIXTURES.json](FIXTURES.json). It verifies
exact coverage, the defining equations and all claimed ranks, including
288 inputs with noncommuting A,B and 180 with pairwise noncommuting A,B,H.
Its seven rejection controls cover matrix corruption, a false dimension,
altered H, singular A, and missing or duplicate coverage. [RESULT.json](RESULT.json)
records the primary counts, full rational/ternary examples and fixture digest.

No independent human proof acceptance or formal proof-kernel check is claimed.
The finite domains are not an exhaustive
search for all full matrices or all dimensions; minimality follows from
the sector argument in PROOF.md. No physical header, dirty-owner restoration,
precision, stock, fixed-tape, recursive-compilation or outer-transfer claim
is made. The selected frontier and kappa are unchanged.

## Reproduce

Python 3.12, standard library only. Each command is read-only; `-O` replay
also checks that verification does not rely on Python assertions.

```sh
python3.12 -I -W error -B research/arbitrary-pivot-schur-minimum/verify.py
python3.12 -I -O -W error -B research/arbitrary-pivot-schur-minimum/verify.py
python3.12 -I -W error -B research/arbitrary-pivot-schur-minimum/binary_check.py
python3.12 -I -O -W error -B research/arbitrary-pivot-schur-minimum/binary_check.py
python3.12 -B scripts/check_research_commit.py --package research/arbitrary-pivot-schur-minimum --check-source-history
```

The first four commands can also be run by absolute path from a read-only,
Git-free export with an empty PATH. `VERIFY.json` registers them. Explicit
`verify.py --write` regenerates only FIXTURES.json and RESULT.json; normal
verification regenerates in memory and requires byte-for-byte agreement.
All external source files in SOURCES.json are provenance, not replay inputs.

## Open next questions

1. For the same prescribed A,B,H, which smaller Schur-commutator ranks are
   feasible at each ambient dimension? The six-map equivalence here treats
   only the maximal rank 2d. A bounded first step is to classify rank-two
   residual commutators for d=2 over F_2 with fixed noncommuting A,B,H,
   before attempting a general theorem. No such classification is claimed.
2. Can the explicit n=6 ternary witness be realized by an admitted complete
   header with fully priced producer and consumer? First identify an actual
   caller and its interface requirements. Algebraic attainment alone gives
   neither a physical construction nor a multiplication improvement.

## Credit and provenance

Nick Petalas's #4774 and #4785 state the open unequal-block-pivot questions;
#4771 and #4746 supply the scalar and all-field identity-pivot predecessors.
ssafwann's #4657/#4671 supply the sector and split-factor method. Nick
Petalas's #4597/#4278 supply the ordered block and scalar factorizations.
Ryanson Jonathan's #4609/#4617 and lee-phys's #4634 supply earlier sharpness
constructions. Nick Petalas's #4259/#4228 retain the laminar-header and
single-request context. Cinna Davis supplies the BIT request setting;
source527, commdata2338 and Jose Manuel retain the normalizer lineage credit.
No historical priority is claimed for the underlying linear algebra.

The checkout starts at canonical main
`81e9bd69e4a5b00ba9c713a1620e36d576d5522e`. TASK.json preserves the original
priority-revision-7 card and explicitly changes its scope to this algebraic
side result. SOURCES.json pins the predecessor documents at that base.
The predecessor scientific heads are #4597
`dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb`, #4774
`a012548529a25a103345e8e8a8afa707a2b3a3e6`, and #4785
`1c9996b87d497a1690630302a0ac65748affbf16`. Their proofs supply the starting
point and attribution; their earlier computational receipts are not re-audited.
