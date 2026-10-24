# Separate E8 inner products do not lower the H6 rank

Claim type: scoped mathematical proof with an exact finite support certificate.
This contribution was produced by Nick Petalas. Apache-2.0.

Over every characteristic-zero field, the canonical 28,800-port H6 root-product
block has minimum rank **800** among all fitting kernels that depend separately
on the two E8 inner products and are odd under simultaneous sign reversal.
The unique minimizer is the existing cubic

```text
F(s,t) = ((s+t)^3 - 4(s+t))/48.
```

Ross Richardson's [PR3649](https://github.com/CrocSwap/integer-mult-bounds/pull/3649)
proved rank 800 for this cubic and sharp larger ranks for the other kernels
depending only on s+t. Its first open question asks about nonisotropic kernels.
The new result excludes an improvement throughout the larger six-dimensional
affine family below, including kernels without exchange symmetry. The existing
800-rank witness and E8 projector theorem are cited premises, not new claims
or re-verification deliverables. This does not optimize arbitrary nonisotropic
kernels, a physical supplier, or the full 30,960-port H6 matrix.

## Exact domain

Let E be the 240 signed E8 roots of ordinary norm two, with inner products in
D={-2,-1,0,1,2}. The canonical root-product ports are E x E modulo simultaneous
antipodes. Its representatives use the 120 first roots whose first nonzero
coordinate is positive and all 240 signed second roots. For ports
(a,b),(c,d), put s=a dot c and t=b dot d.
The kernel has entry F(s,t), with values in an arbitrary characteristic-zero
field K. Require

```text
F(-s,-t) = -F(s,t),
F(2,2) = 1,
F(s,t) = 0 whenever s+t is even, except at (2,2) and (-2,-2).
```

Oddness forces F(-2,-2)=-1. That value belongs to the signed lift, not a
second diagonal of the canonical matrix. The other even entries are exactly
the forced off-diagonal zeros of the retained scalar fitting interface.
Odd s+t entries are unconstrained. There is no requirement F(s,t)=F(t,s),
F(s,t)=f(s+t), or any polynomial formula away from D x D.

Modulo oddness, the fitting conditions are exactly the six evaluations

```text
(s,t):       (2,2) (2,0) (0,2) (2,-2) (1,1) (1,-1)
F(s,t):         1     0     0       0     0      0.
```

Every pair in D x D occurs on signed root products. The canonical orientation
and simultaneous oddness retain all these constraints.

## Proof

Use the five mutually orthogonal root-algebra projectors P_i in
[PR3649's proof](../h6-odd-gram-rank/PROOF.md), of ranks

```text
(d0,d1,d2,d3,d4) = (1,8,35,112,84).
```

Their entries at root inner product s are

```text
p0(s) = 1/240
p1(s) = s/60
p2(s) = s^2/24 - 1/48
p3(s) = (1_{s=2} - 1_{s=-2})/2 - s/60
p4(s) = (1_{s=2} + 1_{s=-2})/2 - s^2/24 + 1/60.
```

These five functions form a basis on D. Functions p1,p3 are odd; p0,p2,p4
are even. Therefore every allowed odd F has a unique expansion

```text
F(s,t) = sum lambda_ij p_i(s)p_j(t),
```

over the twelve pairs with exactly one odd index. On the signed product its
operator is the same sum of P_i tensor P_j, so its rank is exactly
sum_{lambda_ij != 0} d_i d_j. Simultaneous antipodal oddness expresses the
signed matrix as [[M,-M],[-M,M]], where M is the canonical matrix. In
characteristic zero this has rank rank(M), with twice M on its odd subspace.
Consequently the same rank formula holds on the 28,800 canonical ports.
The signed eigenvalues lambda_ij are twice the canonical eigenvalues.

The twelve sector ranks, followed by all possible solutions after the four
sectors of rank at least 3920 are set to zero, are as follows.

| Sector ij | Rank d_i d_j | Low-rank coefficient lambda_ij |
|---|---:|---|
| 01 | 8 | 14y-390 |
| 03 | 112 | 60-2y |
| 10 | 8 | 30-7x |
| 12 | 280 | x+30 |
| 14 | 672 | 30-x/2 |
| 21 | 280 | 90-2y |
| 23 | 3920 | 0 |
| 30 | 112 | x |
| 32 | 3920 | 0 |
| 34 | 9408 | 0 |
| 41 | 672 | y |
| 43 | 9408 | 0 |

Here x,y range independently over K. To derive this table, substitute the
five p_i in the six evaluation equations and solve linearly. For an explicit
rank certificate, multiply the six-by-twelve coefficient matrix by 57600.
The minor on columns 01,03,10,12,21,30 has determinant -94371840000.
Thus those six columns are independent over every characteristic-zero field.
The displayed affine table satisfies all six equations and has free
coordinates lambda_30=x, lambda_41=y. It is therefore the complete low-sector
solution. The full six-by-twelve system also has rank six, so the entire
fitting family has affine dimension six.

If any of the four omitted coefficients is nonzero, rank is at least 3920,
already larger than the cubic's 800. Otherwise split the rank sum into the
four x-dependent sectors 10,12,14,30 and the four y-dependent sectors
01,03,21,41.

At x=60 the first group has rank 8+280+112=400. At every other x its
rank-672 coefficient 30-x/2 is nonzero, so this group's rank is at least
672, strictly greater than 400. At y=0 the second group has rank
8+112+280=400. At every other y its rank-672 coefficient y is nonzero,
so it too has rank strictly greater than 400. Hence the total minimum is
800, attained only at x=60,y=0.

At these parameters the nonzero signed eigenvalues are

```text
lambda_01=lambda_10=-390,
lambda_03=lambda_30=60,
lambda_12=lambda_21=90.
```

Substitution into the p_i expansion gives the cubic on every point of
D x D. It satisfies all fitting conditions and has rank 800. This proves
both attainment and uniqueness. QED.

## Exact evidence and reproduction

[verify.py](verify.py) implements the new optimization using only rational
arithmetic and the standard library. It does not import or run a predecessor
verifier. The written proof uses PR3649's root projectors and ranks as cited
mathematical premises.

The checker enumerates every one of the 4096 sector supports. For each, it
compares the rational ranks of the restricted six-equation coefficient matrix
and its augmentation. Exactly 1764 supports permit a fitting solution. This
counts permitted supports, which may contain zero coefficients; it does not
claim that all those supports occur exactly. The unique least-cost permitted
support is the six cubic sectors, cost 800, and its coefficients are unique.
Rational solvability is equivalent to solvability over any characteristic-zero
extension field because these matrices have rational entries.

Separately, the checker certifies the two-parameter table by affine identities
and matrix ranks, checks every possible one-parameter zero stratum and one
generic stratum, checks all 25 cubic values, and verifies 300 basis-parity
identities. Thirteen controls reject a cheaper nonfitting kernel, six omitted
minimum sectors, an asymmetric redistribution with the same diagonal,
infeasible cheap/empty supports, and three invalid matrix shapes. The generated
[RESULT.json](RESULT.json) binds the other five package files by SHA256.
Normal verification writes no files and checks remain active under -O.

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/h6-bivariate-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/h6-bivariate-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/h6-bivariate-rank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/h6-bivariate-rank --check-source-history
```

Any CPython 3.12 installation can replace that local path. The scientific
marker is `PASS_H6_BIVARIATE_RANK minimum=800 unique=cubic supports=4096`.
The standalone verifier also works in a Git-free export containing all six
package files. `--emit-to NEW_EXTERNAL_FILE` exclusively creates a regenerated
receipt outside the checkout.

## Scope, provenance and limitations

Canonical base ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c, priority revision 7.
The complex-rank-shape-decoder card is changed to this algebraic side result
from PR3649's open nonisotropic-kernel question. The first control was its
rank-800 cubic. The selected-source metadata baseline passed as orientation
only. The selected result and its frontier are unchanged.

[SOURCES.json](SOURCES.json) pins exact predecessor proof/README bytes and
catalogue/selected-record provenance in ancestral main history. Those sources
are cited historical premises, not runtime inputs or rechecked scientific
results. The novel step is the minimum and equality theorem for the larger
bivariate family. Live PRs, handoffs, recent account work, local reservations,
main-tree and merged-PR term searches found no matching claim. The cached
overlap snapshot covered 341 open PRs and 4444 Discussion records; sparse local
coverage was incomplete. No exhaustive novelty or literature-priority claim
follows.

The theorem assumes characteristic zero, simultaneous oddness, dependence only
on s,t, the fixed root-product ports and the retained fitting zeros. It gives
no rank bound for arbitrary coordinate-dependent kernels, operator-valued
factors, changed geometry, nonodd kernels or positive characteristic. Its
800 is the root-product rank, not the full H6 kernel rank or a physical
helper count. Scalar factorization rank does not price reuse, partial-frame
visits, copies, compensation or restoration. Those costs, physical/native
realization, hosting, stock, precision/tapes, compiler and complete outer
transfer remain unpriced. No supplier, new kappa, selected cold replay,
Lean or Docker result is claimed. Independent human and formal proof-kernel
review are unclaimed.

The checker has no recursion, subprocesses or dynamic code generation. Its
4096 support iterations use at most 25-by-13 rational elimination matrices.
Each function is below 60 lines. CPython managed allocation is the documented
deviation from fixed preallocation; collection sizes and all loops are bounded
by these fixed domains. Registered commands treat warnings as errors.

## Open next questions

Can a kernel that distinguishes root pairs with the same (s,t) reduce the
root-product rank? This would escape the exact obstruction proved here.
Start with one explicit coordinate-dependent orbit refinement and its full
fitting constraints. The present tensor-projector diagonalization no longer
applies, and no such fitting kernel or complete physical cost is supplied.
The structured question and remaining obligations are in [TASK.json](TASK.json).

## Credit

Credit Ross Richardson for PR3649's projectors, rank formula, cubic witness,
odd-Gram classification and open nonisotropic-kernel question, and for
PR1830's H6 compensation/encoder and spectral context. Credit Dominik Scholz
for PR606's E8 geometry/factorization and DreamingOfClouds for the H6/Walsh
proposal. The retained predecessor notices and earlier source lineage remain
unchanged. The new theorem is the exact bivariate minimum and its unique
optimizer. No priority is claimed for tensor-product projector algebra or
linear-system support optimization.
