# Exact Coxeter tariffs with arbitrary dirty workspace

**Written all-parameter theorem; no new kappa or supplier admission.**
For every Coxeter system with finitely many simple generators, including
infinite groups, mixing through any finite number of dirty registers cannot
reduce the direct simple-reflection bill in the formal model below.
The result holds separately for every reflection conjugacy class and hence
for every positive class-dependent price.

This extends the retained symmetric-group and dihedral theorems to one
uniform statement. The concrete new family is **all signed-permutation
groups B_n, with two independently priced types of operation and unrestricted
finite dirty workspace**. The theorem also covers exceptional,
noncrystallographic, affine and other infinite Coxeter systems; the executable
examples have the smaller, explicit coverage below. This is a mechanism
exclusion, not an improvement in the integer-multiplication exponent.

## Exact statement and relevance

Work in the full formal algebra `F2[W]`. A paid call has the form
`I + ([s]+1)N`, where s is a simple Coxeter generator and N is a binary
rank-one idempotent on the registers. Arbitrary invertible binary scalar
mixing is free. All inputs are arbitrary, and the required endpoint is
`diag([w_1],...,[w_d],1,...,1)`, restoring every spectator and removing every
off-diagonal coupling. Preparation and restoration calls count.

For a root orbit O, let `i_O(w)` count positive roots in O sent negative by
w, and price that orbit's generators at `c_O>0`. The exact minimum bill is

```
sum_j sum_O c_O i_O(w_j).
```

Each orbit's call-count lower bound is attained simultaneously by coordinate
calls along reduced expressions. With unit prices this is
`sum_j length(w_j)`, independent of the available dirty-register count.
The same exact tariff holds if arbitrary binary N, including nilpotents,
are allowed and charged `c_O rank(N)`.

For a signed permutation written `(w_1,...,w_n)`, a sign flip at the first
position costs a and an adjacent swap costs b. Its exact single-role cost is

```
a * #{i: w_i<0}
+ b * (#{i<j: w_i>w_j} + #{i<j: w_i+w_j<0}).
```

Costs add across target roles. For example, reversing every sign on n
coordinates costs exactly `a*n + b*n*(n-1)` per target, regardless of the
dirty workspace available. The coefficients are sharp separately, for all
positive a and b, not just at the sampled prices.

This eliminates all workspace-size and finite-word searches for a paid
saving **within this model**. It does not settle arbitrary involution-generated
groups such as the coordinate-CNOT alphabet in `GL_3(F2)`, prices that vary
between conjugate simple generators, non-simple unit-price primitives,
nonlinear scalar gates, or concave higher-rank invocation prices.

## Proof and evidence

[PROOF.md](PROOF.md) supplies the universal argument. It uses the established
Coxeter root sign/length facts from Gert Heckman's
[Coxeter Groups, Section 4.2](https://www.math.ru.nl/~heckman/CoxeterGroups.pdf#page=71),
then applies the predecessor cut-rank inequality separately to each root
orbit. A simple generator crosses exactly one root. The diagonal endpoint
has the sum of the targets' crossing ranks. The proof treats the infinite
root module as an algebraic direct sum with finite-rank crossing blocks;
it never takes a finite quotient or a truncation as a proof of the infinite
case. Attaining endpoints are proved in the full group algebra.

The B_n section also provides a direct root-count formula and sorting
construction. The general theorem is a written proof using cited root
theory, **not a Lean theorem or an exhaustive computer proof**.

| Evidence | Exact finite coverage |
| --- | --- |
| Primary Cartan-coordinate engine | All 1,946 elements of A2, A3, A4, B2, B3, B4, D4, F4 and G2; all root signs, orbit counts, reduced words and directed Cayley edges |
| Infinite-family probe | Affine A2 through word radius 9, using exact integer matrices and actual inversion-root labels; 136 elements, no finite-field quotient |
| Arbitrary scalar couplings | All 530 binary matrices through three roles, for both B2 simple generators: 1,060 exact formal involution and orbit cut-rank checks |
| Full formal endpoints | All 64 B2 ordered target pairs with a restored spectator; all 256 single-call omissions disagree with the claimed endpoint |
| Independent signed-window engine | All 4,282 elements of B1 through B5, three exact Dijkstra price pairs `(1,1)`, `(2,3)`, `(5,1)`: 12,846 tariff comparisons |
| Independent dirty-state replay | Nine heterogeneous B2–B4 endpoints, with one to three dirty helpers genuinely coupled by scalar gauges; 75 omission, nine dirty-leak and nine wrong-order controls |
| Integrity controls | Six public-CLI test groups: read-only Git-free export, missing source pin, changed source, typed receipt mutations, duplicate JSON key, and an actual rank-undercharging code mutation |

The primary engine uses integer matrices in simple-root coordinates and
packed binary coefficient matrices. [independent.py](independent.py) imports
neither that engine nor its receipt: it uses signed windows, weighted graph
search, a separate window/root formula and a separate formal interpreter.
Both use exact standard-library arithmetic.

The primary engine explicitly checks a representation-kernel trap: the
eight-term norm of B2 is nonzero in `F2[B2]` but zero on the root permutation
module. An off-diagonal dirty leak made from that norm passes the quotient
test and fails the formal boundary. Thus a root-action image is used only
for a lower bound, never as an endpoint oracle. Rank-two undercharging,
reducing signed root coordinates modulo two, and unequal prices on the
conjugate A2 generators are separate boundary demonstrations.

[RESULT.json](RESULT.json) is a fixed, type-sensitive primary receipt.
[REVIEW.md](REVIEW.md) records the separate AI review, source hashes and
its limits. [VALIDATION.md](VALIDATION.md) records environments and commands.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/coxeter-root-tariff
```

The registered commands run both engines and the six integrity test groups.
Direct commands also work in an export containing the pinned source inputs:

```sh
python3 -I -O -B research/coxeter-root-tariff/verify.py
python3 -I -O -B research/coxeter-root-tariff/independent.py
python3 -I -B research/coxeter-root-tariff/test_package.py
```

Expected markers: `PASS_COXETER_ROOT_TARIFF` and
`PASS_INDEPENDENT_COXETER_ROOT_TARIFF`. Default replay writes nothing.
Explicit receipt regeneration is
`python3 -I -B research/coxeter-root-tariff/verify.py --write`.

## Sources, overlap and limits

Scientific base: `7f90cb9985624b86b0e9dd8737b4e9ba2f795e31`, priority revision 5.
[SOURCES.json](SOURCES.json) pins the selected record, task catalogue and
three retained predecessors. [OVERLAP.json](OVERLAP.json) records the live
coverage, exact related PR heads and freshness limits. The local task card
records the assigned nonabelian model and the refinement to a scoped
obstruction. No public claim was posted, respecting the donor's instructions.

Credit Adam Gall's PR1941 cut method and PR1911 infinite-dihedral theorem;
Ross Richardson's PR1966 and PR1989 adjacent-permutation theorem; the retained
finite-dihedral theorem and its credited D8/D16 lineage; and the underlying
register model of eumemic/PR288, Ali Romman/PR468 and Gareth Davidson/PR1333.
All symmetric and dihedral special cases are inherited, including the
arbitrary-workspace D16 result. The rank-priced arbitrary-coupling extension
is also already present for the infinite dihedral case in
[ywz65's PR2716](https://github.com/CrocSwap/integer-mult-bounds/pull/2716);
our new scope for it is the Coxeter family. Heckman's root-theory facts and
the elementary cut inequality are not claimed as new. No literature-priority
claim is made.

Native address realization, scalar-operation charges, hosting, precision,
tape use, recursive profiles, selected-supplier adoption and multiplication
theorem obligations are **not** verified here. No selected cold replay is
needed or claimed because the selected construction is unchanged.

Prepared for David Arias with substantial OpenAI Codex assistance, including
separate AI proof review and an independently implemented checker. No
independent human review is claimed. New work is Apache-2.0.

## Open next questions

1. **Non-class-invariant prices.** Can extra restored dirty registers beat
   the direct tariff for S4 prices `(2,1,2)`? This proof cannot price conjugate
   adjacent generators differently. First read Nick Petalas's
   [PR2583](https://github.com/CrocSwap/integer-mult-bounds/pull/2583), which
   certifies the two-register domain; then seek a stronger invariant or a
   complete formal witness with an extra dirty register. The arbitrary-role
   lower bound is the blocker; another two-register census adds no coverage.
2. **A different operation alphabet.** Is there a physically realizable
   non-Coxeter mechanism that changes the paid recursive profile? The first
   step is an exact complete endpoint and native cost contract outside the
   simple-reflection hypothesis, checked against current GL3 and other
   nonabelian work. A finite quotient identity alone is not a supplier.
   No further expansion of the excluded Coxeter model is justified by this
   result; a changed price, alphabet or endpoint hypothesis must be named.
