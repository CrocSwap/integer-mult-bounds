# Exact incomparable-demand dirty fanout over residue rings

**Scoped written proof with exact finite corroboration; no new κ.**
This answers Open next question 1 of Krzysztof Wójt's
[#5045](https://github.com/CrocSwap/integer-mult-bounds/pull/5045): the demand
pair `(2,3)` over `Z/6` has the five-term optimum below for every positive
price vector. An elementary CRT argument also removes the comparable-ideal
restriction for **every pair over `Z/n`, for every integer n >= 2**.
The lower-bound classification is credited to #5045. The additional step
is a choice of insertion coefficient that generates both demand ideals.

## Contract and the Z/6 result

There are exactly two dirty output rows and one disjoint preserved source.
For arbitrary independent `a_0,a_1,p in (Z/n)^w`, with `w >= 1`, require

    (A_0,A_1,p) = (a_0 + lambda_0 p, a_1 + lambda_1 p, p).

A fixed finite straight-line word may use only the following gates:

    P_i(beta):  A_i <- A_i + beta p,          price mu_i > 0;
    E_i(alpha): A_i <- A_i + alpha A_(1-i),   price c_i > 0.

Prices are arbitrary positive real numbers, stationary and independent of
coefficient. `c_i` prices the direction **into row i**. They are complete
abstract gate prices under the predecessor contract, not measured physical
costs. There are no other rows, clearing, free basis changes, intermediate
observations or input-dependent choices. Both original dirt columns must
return exactly. An inverse execution, if needed, is charged separately.

**Theorem 1.** For `n=6` and `(lambda_0,lambda_1)=(2,3)`, the exact cost is

    OPT = min(mu_0 + mu_1,
              2 mu_0 + 2 c_1,
              2 mu_1 + 2 c_0,
              mu_0 + 2 c_0 + 2 c_1,
              mu_1 + 2 c_0 + 2 c_1).

The principal ideals `(2)={0,2,4}` and `(3)={0,3}` are incomparable.
The following five words attain the five entries, in chronological order;
every coefficient is interpreted modulo six.

| Name | Word | Counts `(P_0,P_1,E_0,E_1)` |
|---|---|---|
| D | `P_0(2), P_1(3)` | `(1,1,0,0)` |
| T_0 | `E_1(5), P_0(3), E_1(1), P_0(5)` | `(2,0,0,2)` |
| T_1 | `E_0(5), P_1(2), E_0(1), P_1(1)` | `(0,2,2,0)` |
| S_0 | `E_0(5), E_1(3), P_0(5), E_1(3), E_0(1)` | `(1,0,2,2)` |
| S_1 | `E_1(5), E_0(4), P_1(1), E_0(2), E_1(1)` | `(0,1,2,2)` |

For example, the source column of `S_0`, initially zero, becomes `(5,0)`
at its only insertion, then `(5,3)`, then `(2,3)`. Its first two row gates
are the inverse of its last two, so the full original dirt matrix returns
to identity. The corresponding source columns for `S_1` are `(0,1)`,
`(2,1)`, `(2,3)`. Neither construction assumes that a nonunit is invertible.

All five terms are necessary. In price order `(mu_0,mu_1,c_0,c_1)`, they
are uniquely optimal at `(1,1,1,1)`, `(1,9,1,1)`, `(9,1,1,1)`,
`(5,20,1,1)` and `(20,5,1,1)`, respectively, with costs `2,4,4,9,9`.
For `(100,1000,1,1)`, `S_0` costs **104**, whereas the best repeated
insertion costs 202. This is a new incomparable-demand instance; #5045's
analogous `(2,1)` example over `Z/4` remains credited predecessor evidence.

## Arbitrary-word lower bound

Here we restate #5045's source-count argument, which does **not** need
comparable ideals. Delete zero-coefficient gates, since their prices are
positive. Set `p=0` and track the matrix on the two independent dirt
symbols. It starts and ends at `I_2`; source insertions do not affect it.
The all-input contract implies this matrix equality by testing the two
coordinate inputs separately.

**Directional return lemma (#5045).** A nonzero row-ADD direction cannot
occur exactly once. If the only upper shear has coefficient `alpha != 0`,
combine all lower shears before and after it. The matrix has the form

    L(x) U(alpha) L(y),

whose upper-right entry is `alpha`, so it is not identity. Swapping rows
gives the other direction. This argument holds even over rings with zero
divisors. Thus a used direction costs at least two calls.

For demand `(2,3)`, at least one source insertion is necessary: row gates
alone preserve the initially zero source column. Every legal word belongs
to one case:

1. Both rows receive a source insertion. Its count vector dominates D.
2. Only row i receives insertions, at least twice. The nonzero demand in
   row j requires an `E_j`, hence at least two of them. Its counts dominate T_i.
3. There is exactly one insertion, at row i. Again at least two `E_j`
   occur. If there were no `E_i`, the insertion coefficient would equal
   `lambda_i`, and the final row-j coefficient would be a multiple of
   `lambda_i`. Incomparability excludes this, so at least two `E_i` also
   occur. Its counts dominate S_i.

These cases exhaust arbitrary finite words, including all interleavings
and cancellations. Together with the attaining table they prove Theorem 1.
They also show that the five displayed vectors are the exact Pareto-minimal
gate-count vectors, not merely a fit to sampled prices. Their unique-price
examples show that every vector contributes to the positive-price envelope.

## Extension to every residue ring

Write `y <=_R x` for `y in Rx`, equivalently
`gcd(x,n)` divides the canonical integer representative of y. For
`i in {0,1}`, put `j=1-i` and define

    D   = [lambda_0 != 0] mu_0 + [lambda_1 != 0] mu_1,
    T_i = 2 mu_i + 2 c_j,

          { mu_i                       if lambda_j = 0,
    S_i = { mu_i + 2 c_j               if lambda_j != 0 and lambda_j <=_R lambda_i,
          { mu_i + 2 c_i + 2 c_j       otherwise.

**Theorem 2.** For every `n >= 2`, every demand pair in `Z/n`, and every
positive price vector in the stated two-row contract,

    OPT = min(D, S_0, S_1, T_0, T_1).

This is #5045's price expression on a larger commutative-ring domain.
For prime powers its comparable-demand theorem already gives the result.
The additional domain includes incomparable ideals and a nonunit common
ideal generator, not just the unimodular pair in Theorem 1.

### A coefficient-selection lemma

**Lemma.** Given x,y in `Z/n`, there are a,beta,r in `Z/n` such that

    beta = x - a y,       y = r beta,       x = (1 + a r) beta.

For x=y=0 take all three coefficients zero. Otherwise choose canonical
integer representatives and set

    g = gcd(x,y,n),       N = n/g,       X = x/g,       Y = y/g.

Then `N > 1` and `gcd(X,Y,N)=1`. For each prime q dividing N, prescribe

    a = 0 (mod q) if q does not divide X;
    a = 1 (mod q) if q divides X.

In the second case q does not divide Y, so `X-aY = -Y != 0 (mod q)`.
In the first case `X-aY = X != 0 (mod q)`. The Chinese remainder theorem
for the distinct primes supplies a satisfying all prescriptions. Hence

    gcd(X-aY,N)=1.

Let `beta = x-ay (mod n)`. It is a multiple of g, and
`B=beta/g` is a unit modulo N, since `B = X-aY (mod N)`. Set

    r = Y B^(-1) (mod N),

and lift it to `Z/n`. Then `r beta = g r B = g Y = y (mod n)`;
`x=beta+ay` proves the remaining identity. In particular `(beta)=(x,y)`
as ideals. The proof inverts B modulo N, **not** beta modulo n.

### Lower bound and constructions for Theorem 2

The directional return lemma still applies. If both rows receive an
insertion, the price is at least `mu_0+mu_1 >= D`. If only row i receives
at least two insertions and `lambda_j != 0`, it is at least T_i; if
`lambda_j=0`, it is at least `mu_i=S_i`. With exactly one insertion at i,
the bill is at least `mu_i` when `lambda_j=0`, and at least
`mu_i+2c_j` otherwise. In the latter case, absence of `E_i` would force
`lambda_j in R lambda_i`, by the same source-column argument used above.
Failure of that divisibility therefore adds at least `2c_i`. These are
exactly the S_i cases. Zero total demand has the empty word of price zero.
This proves the lower envelope for every word without any ideal-comparability
assumption.

Direct insertion attains D. For any pair, the word

    E_j(-1), P_i(lambda_j), E_j(1), P_i(lambda_i-lambda_j)

has cost at most T_i and the required endpoint: the middle transport gives
row j its demand, and the last insertion fixes row i. If `lambda_j=0`,
use `P_i(lambda_i)`. If `lambda_j=r lambda_i`, use

    E_j(-r), P_i(lambda_i), E_j(r).

These are the credited #5045 constructions. For its previously excluded
case `lambda_j not in R lambda_i`, apply the lemma with
`x=lambda_i, y=lambda_j`, and execute

    E_i(-a), E_j(-r), P_i(beta), E_j(r), E_i(a).

The two outer pairs cancel on dirt. The final two gates send the inserted
column `beta e_i` to `(1+ar)beta e_i + r beta e_j`, the desired column.
Here a, r and beta are all nonzero: a=0 would imply `y in Rx`, while r=0
or beta=0 would imply y=0. This word has exactly price S_i. Any zero
gate in the other constructions can be omitted, so each entry is attained
at no greater cost. Combining these upper bounds with the lower bound
proves equality. The literal inverse reverses the word and negates every
coefficient, with the same tariff and no additional algebraic assumptions.

For example, `(6,9)` over `Z/18` has incomparable demand ideals and common
generator 3. The lemma works although neither inserted coefficient nor
the demands need be units. A unit-only argument would not cover this case.

## Verification and scope

`verify.py` is standard-library Python. Its constructive side implements
the CRT lemma, the five candidate words and the price expression. A separate
finite oracle builds the entire reachable affine-state graph using only
the primitive gates and applies exact Dijkstra searches. It does not call
the formula or the word constructors. All states and coefficients are
exact integers modulo n; tariff comparisons use integers or `Fraction`.
There are no floating-point, depth-cutoff or probabilistic-key decisions.

The bounded replay checks all demands over `Z/2` through `Z/6` against
shortest paths, with additional price vectors over `Z/6`; all candidate
words and inverses over `Z/2` through `Z/24`; every literal scalar input
for the five displayed `Z/6` words; and larger composite CRT fixtures.
It includes zero-demand, nonunit-generator, price-tie and distinct-optimal-
regime cases, plus controls rejecting a missing dirt-return gate, a wrong
source coefficient, the invalid unit-demand shortcut and each omitted
envelope term. Exact evidence counts are printed by the replay.

The registered normal and optimized runs pass with 119 Dijkstra runs,
3,654 optimum comparisons, 9,830 ordered CRT checks, 24,575 candidate
words, 147,450 forward/inverse basis checks and 2,160 literal scalar checks.
The `Z/6` graph has 5,184 states and is searched at 91 price vectors;
the other four moduli each use seven price vectors. Sixteen built-in
controls pass. Three additional disposable script mutations are rejected:
omitting a dirt-return gate, omitting the `2c_i` charge, and replacing the
oracle's heterogeneous prices by unit prices.

```sh
python3.12 -B scripts/research_package.py --package research/z6-incomparable-fanout --check-only
python3.12 -B scripts/research_package.py --package research/z6-incomparable-fanout
python3.12 -I -W error -B research/z6-incomparable-fanout/verify.py
```

The manifest registers normal and optimized runs. Direct execution is
Git-free, read-only and needs only this package. The universal statements
rest on the written proofs above; the finite searches corroborate their
bounded instances. This is neither a proof-kernel formalization nor an
independent human review. Prices depending on coefficients, arbitrary
noncommutative rings with incomparable ideals, more than two output rows,
and actual physical caller costs are outside scope. No selected supplier,
compiler, precision/tape admission, or multiplication-exponent improvement
follows from this algebraic result.

## Task, sources and overlap

Scientific base: canonical main `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`,
priority revision 7. The explicit donor assignment refines #5045's
incomparable-demand handoff; `bit-helper-contract` is marked changed in
[TASK.json](TASK.json), with the original card preserved. The selected
record is orientation provenance, not a numerical dependency. The selected
conditional κ remains `60403/20000000`.

[SOURCES.json](SOURCES.json) pins the predecessor proof and README at this
base. They are historical provenance; no predecessor executable or mutable
external file is imported. The claim and completion record are in
[the predecessor discussion #5030](https://github.com/CrocSwap/integer-mult-bounds/discussions/5030).
Initial remote pagination covered 305 open PRs at 08:25 UTC and 4,198
Discussion records at 08:27 UTC on 2026-10-23, supplemented by all-state
PR searches for `incomparable`, `fanout` and `5045`, and the live #5030
thread. No resolving successor was identified within that coverage.
The local checkout is sparse; omitted notes, arbitrary diffs and unpublished
work were not exhaustively searched. Submission-time refresh is recorded
in the PR.

## Open next questions

1. **Which other rings admit the coefficient-selection lemma?** This
   isolates the sufficient algebraic hypothesis for the same two-row
   tariff. First study finite commutative rings with nonprincipal
   two-generated ideals; either construct beta or prove that a single
   insertion cannot reach the demand. The missing obligation is an orbit
   criterion, not another residue-ring price sample.
2. **What replaces the five-term envelope for three rows?** This matters
   for sharing more demands. Start with #5045's `(2,1,1)` over `Z/4`,
   retaining every dirt column, and classify words by insertion supports.
   The two-row directional-return argument does not extend automatically
   when other rows can carry dirt.
3. **Can an actual caller use these tariffs?** First supply its complete,
   coefficient-independent source and ADD prices, including preparation,
   routing and restoration, then compare the full completed bill.
   A concrete caller and its physical cost matrix are currently missing.

## Credit

Prepared by lee-phys with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. Apache-2.0. Credit Krzysztof Wójt's
#5045 for the comparable-demand theorem, source-count lower bound,
directional return lemma and repeated-insertion construction; Nick Petalas's
#4916 for the ring-valued contract and unit-demand result; Ross Richardson
#3121/#3063; Cinna Davis #1944/#1968; Anthony #774; Oscar Fennell #759;
Tekalign #3130; and the predecessor packages' retained lineage.
The CRT coefficient selection and the resulting incomparable/residue-ring
extension are the additional contribution here. No novelty is claimed for
the Chinese remainder theorem or the inherited lower-bound argument.
