# Every dyadic rank-one shear admits one borrowed readout hub

Every nonzero rank-one matrix over D = Z[1/2] admits a common-chart scalar
program with these three stages:

1. Prepare one existing source as an integer combination of the sources,
   using only source-to-source integer ADDs.
2. Read that one source exactly once into each nonzero target row.
3. Reverse the preparation, restoring every source exactly.

No extra field, clean entry, CLEAR, SCALE or odd-denominator native coefficient
is required. This removes the dyadic-ratio pivot restriction from David Ganz's
[#4502](https://github.com/CrocSwap/integer-mult-bounds/pull/4502) sufficient
single-pivot adapters. Its explicit matrix `[[9,15],[15,25]]` has neither a
legal source pivot nor a legal target pivot; the new compiler handles it.

Claim type: **scoped constructive proof with finite corroboration**, produced
by Nick Petalas. The improvement is universal admissibility of this single-hub
topology. Direct entrywise ADDs already implement any dyadic shear without
scratch. This theorem does not claim that zero-scratch implementation itself
is new, or that the new topology always reduces scalar work.

## Contract and complete bill

Let X have n >= 1 existing source fields and Y have m >= 1 disjoint target
fields. All fields use the same linear chart; all may contain arbitrary initial
data. The required action is `(X,Y) -> (X,Y+MX)` for a fixed dyadic matrix M
of rational rank one. Exterior fields remain untouched. No intervening query,
frame transition or source read may occur inside the replacement.

The legal instruction is `Z_i += q Z_j`, i != j, with fixed q in D. Source
preparation and restoration use integer q. Target updates use dyadic q.
If the preparation coefficients are q_1,...,q_L and the primitive factorization
below is M = a b, the complete native scalar allowance is

```text
B = 2 sum_(l=1..L) A(q_l) + sum_(j:a_j != 0) A(a_j),
A(u/2^v) = 2 (3 + bitlength(|u|)-1 + popcount(|u|) + v),
```

where the fraction is reduced and nonzero. Both source passes are charged.
There are `2L + #{j:a_j != 0}` ADDs and zero additional owned fields. This is
the retained ADD tariff, not a claim about optimal circuits or physical time.

The emitted first fixture has 32 ADDs and allowance 270. Direct evaluation
has four ADDs and allowance 76. The universal compiler deliberately makes no
cost selection or optimization claim. No native window is replaced here.

## Proof

**Primitive factorization.** Take any nonzero row r of M. Clear its dyadic
denominators by a power of two s. Divide the resulting integer row by the gcd
of its entries and choose the sign so its first nonzero coordinate is positive.
This gives a primitive integer row b. Rank one implies each row of M is a
rational multiple a_j b. Since gcd(b_1,...,b_n)=1, Bezout gives integer c_i
with `sum_i c_i b_i = 1`. Consequently

```text
a_j = sum_i c_i M[j,i] in D.
```

Thus M = a b with a dyadic and b primitive integral. This is the rank-one
specialization of the classical integer reduction already used in David Ganz's
[#4494](https://github.com/CrocSwap/integer-mult-bounds/pull/4494). The new
step below uses a source basis itself, instead of its owned temporary.

**Elementary preparation.** If n=1, b=(1) and no preparation is needed.
For n>=2, reduce b by elementary column ADDs. At each pair of coordinates
0,j, subtract an integer multiple of coordinate j from coordinate 0 using
integer division truncated toward zero, then replace `(r_0,r_j)` by
`(r_j,-r_0)`. The latter signed swap equals three elementary ADD matrices:

```text
E_(0,j)(-1) E_(j,0)(1) E_(0,j)(-1),
E_(i,j)(q) = I + q e_i e_j^T.
```

The absolute remainder strictly decreases, so the Euclidean process terminates.
Processing j=1,...,n-1 leaves `(g,0,...,0)` with |g|=1. If g=-1, square the
signed swap on coordinates 0,1 to negate both coordinates. This yields a
finite product `E=E_1...E_L` with `b E=e_0^T`.

Set T=E^-1. Then `e_0^T T=b`. Chronologically executing the source ADDs
`E_1^-1,...,E_L^-1` acts by `E_L^-1...E_1^-1=T` on the source column.
This order distinction matters: row reduction multiplies on the right,
whereas chronological execution multiplies on the left. All inverse
coefficients are integers. The prepared source X_0 is exactly bX.

**Readout and return.** Execute `Y_j += a_j X_0` for each nonzero a_j.
The target increment is a_j bX, hence MX. Readout does not modify any source.
Apply the reversed, sign-negated preparation to restore all source fields.
This proof holds for arbitrary initial source and target values; it does not
assume a clean borrowed field. Every instruction preserves exterior fields.
Sign symmetry A(-q)=A(q) proves the complete bill above.

M=0 uses the empty program. The same theorem can be applied separately to
`-M^T` after exchanging source and target groups, but the particular Euclidean
programs and their bills need not agree in the two orientations.

## Evidence and reproduction

The executable uses only the Python standard library and imports no predecessor
code. Exact symbolic execution starts from the full identity matrix on all
source and target fields, so arbitrary dirty inputs are independent columns.
It checks the complete output matrix, exact source restoration, integral
source preparation, the prepared primitive hub, one read per nonzero target,
and the complete scalar invoice.

The fixed finite domains are:

- 3,939 two-by-two cases: every numerator tuple in {-6,...,6}^4 with zero
  determinant, at each common denominator 1, 2 and 4. This count includes zero
  matrices and repeated matrices at different numerator/denominator choices.
- 768 deterministic rank-one fixtures with 1 through 8 sources and targets.
- The displayed no-pivot matrix and a three-source row (6,10,15), whose
  coordinates have gcd one but no coprime pair.
- Three boundary cases cover the admitted coefficient limits, eight-by-eight
  role limit and a long Euclidean chain from consecutive Fibonacci numbers.
- Nine rejected input cases and five mathematical omission controls: missing
  preparation, missing restoration, wrong hub, wrong inverse order and missing
  readout. All checks stay enabled under optimized Python.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/dyadic-rankone-borrowing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/dyadic-rankone-borrowing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-rankone-borrowing
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dyadic-rankone-borrowing --check-source-history
```

Any CPython 3.12 interpreter can replace the absolute path. The verifier prints
a generated JSON receipt bound to the SHA256 of all six package files, then
`PASS_DYADIC_RANKONE_BORROWING`. It writes no artifacts. Each registered
command is bounded to 60 seconds; local timings are recorded in the PR body.

The written theorem covers every finite m,n and dyadic rank-one M. The executable
accepts at most eight sources and targets, numerator bit lengths at most 64 and
denominators at most 2^16. Clearing denominators gives a primitive integer row
with entries below 2^80 in magnitude. Euclidean division halves the remainder
within two steps; the 264-step per-coordinate cap exceeds the required 162.
At most 7*264*4+6=7,398 elementary reduction gates and eight readouts fit the
16,384-gate complete program cap. Every function has fewer than 60 lines.

Python allocates exact integers, fractions and lists dynamically. This is a
Power of Ten rule 3 deviation for a bounded offline verifier. Role, coefficient,
iteration and gate caps bound its live state. The code has no recursion,
subprocess, network access, file writes or hidden persistent state. Warning-strict
normal and optimized execution are the applicable interpreter diagnostics.
No separate Python linter or type checker is installed locally; AST parsing
and a function-size inspection also pass.

## Scope and remaining obligations

All claims concern ideal common-chart scalar ADDs. Coefficient growth,
rounded numerical error, native window adoption, stock, tape movement, physical
dispatch, a complete supplier bill and outer admission are unproved. No saving
in recursive calls or kappa is claimed. No independent human review, formal
proof-kernel check or selected-construction cold replay is supplied.

The card's scope is explicitly changed to this algebraic side result. Its old
ceiling example was attempted and raises `KeyError: 'complex_profile'` against
the changed selected schema; it was not repaired or treated as scientific
evidence. The current selected metadata baseline passes separately. Its retained
conditional kappa is 0.00302015 and remains unchanged. This package stops at
the local theorem; it proposes no dependent construction expansion.

Scientific base is canonical main 81e9bd69e4a5b00ba9c713a1620e36d576d5522e,
priority revision 7. The cached overlap search covered 320 open PRs at
09:27:40 UTC and 4,236 Discussion records at 09:29:14 UTC on 2026-10-23.
Sparse local note coverage was incomplete and supplemented by main-tree and
merged-PR searches. Arbitrary diffs and unpublished work remain outside coverage.
The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19142749)
states the same scope. Exact provenance is in [SOURCES.json](SOURCES.json).

## Open next questions

1. Can a cost-selecting compiler choose a short unimodular preparation that
   improves the complete bill on an actual no-pivot native window? Start by
   finding one such window and compare direct ADDs, both single-pivot methods
   and the complete borrowed-hub bill. No favorable native instance is supplied.
2. What coefficient-growth and rounded-error bounds permit source-basis
   borrowing inside an actual caller? First bound every intermediate row norm
   of one proposed preparation and its restoration. The present exact theorem
   supplies neither a numerical precision prescription nor caller admission.

## Credit

This contribution was produced by Nick Petalas. David Ganz / Dugongue's
#4494 supplies the dyadic integer-reduction factorization setting; #4499
supplies the exact-gauge context; #4502 supplies borrowed source/target
conjugation, complete restoration pricing and the explicit no-pivot example;
#4505 installs its four particular adapters. Classical Bezout, Euclidean
reduction, elementary unimodular matrices and reversible uncomputation retain
their existing mathematical credit. No literature priority is claimed for them.

Retain zxv's native reconstruction lineage, Jacob Alan Sussman's mixed-target
compiler and Cinna Davis's padding, query-thinning, retiming and joint-boundary
work, as credited by those predecessors. No predecessor implementation or
certificate is replayed here. The new step is the universal single borrowed
hub theorem and its standalone exact compiler. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.
