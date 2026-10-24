# The sharp rank boundary for P112 diagonal completions

This package was produced by Nick Petalas. Apache-2.0.

**Scoped mathematical proof with exact finite corroboration.** For the P112
Gram matrix G and an arbitrary complex diagonal matrix Delta, write s for the
number of nonzero diagonal corrections. For every integer q with 8<=q<=58,

```text
rank_C(G+Delta)<=q  if and only if  s<=q-8.
In that range, rank_C(G+Delta)=8+s.
```

The upper endpoint 58 is sharp. A constant diagonal correction on 53 positions
has rank 59, rather than the additive prediction 61. This answers Open next
question 1 of Arham-Tahir64's [PR #1313](https://github.com/CrocSwap/integer-mult-bounds/pull/1313),
which gives the sufficient range through 20 and leaves its sharpness open.
The new result is the sharp completion boundary. The root-code distance,
hyperplane classification and original completion argument are credited
premises. No COPY improvement, physical supplier or new kappa is claimed.

## Model and inherited geometric premises

Let X contain the 112 doubled E8 root-line representatives after removing
the eight lines e_(2j)+/-e_(2j+1), j=0,1,2,3. Each row of X has squared norm
eight. Set G=XX^T. With conventional norm-two roots R=X/2, the target
2RR^T is G/2. Scaling Delta by the same factor transfers every rank statement
between these conventions. All ranks are over C and transposes are ordinary.

This is the mask that fixes every off-diagonal entry and frees diagonals.
The genuine odd-only decoder mask fixes diagonals and frees certain
off-diagonal entries. Our witness is not an odd-only completion.

We use two predecessor premises without auditing them:

1. Every nonzero complex root-code vector Xa has support at least 53 on
   P112. This is the distance statement in woklerx's
   [PR #1447](../p112-sparse-completion-rank/README.md).
2. Every real root-spanned hyperplane of E8 is one of the eight types in
   themilkman216's [PR #968, premise F6](../complex-frame-pair-decoders/PROOF.md).
   Only E7 has more than 42 root lines. It has 63 and its normal is a root.
   The classification remains a cited premise, as in the predecessors.

One additional finite fact used below is that the intersection of two
distinct root-normal E7 hyperplanes contains at most 36 E8 root lines.
The verifier enumerates every unordered pair of distinct normals: 3,780
intersections have 30 lines and 3,360 have 36. These are exact integer zero
tests, independent of any predecessor executable.

It follows that a root-spanned subspace of dimension at most six contains
at most 42 E8 root lines. Otherwise extend its root basis to a basis of R^8.
Omitting two different added basis roots gives two distinct root-spanned
hyperplanes containing the original subspace. Both contain more than 42
lines, so both are E7. Their intersection has at most 36 lines, a
contradiction. The bound 42 is sufficient here; no sharp rank-six count is
claimed. It also bounds any subset of P112 of root rank at most six.

## Rank stratification and the sharp lower bound

Let S be the changed diagonal support and J its complement. Put
r=rank(X_J). Choose r independent unchanged rows B in J. Their real Gram
matrix is positive definite, so G[B,B] is invertible over C. Pivoting on
that principal block leaves the unchanged rows in J minus B zero.
On S, the remaining original Gram matrix H has rank 8-r: it is the Gram
matrix of the root vectors projected orthogonally off span(X_B).
The correction Delta_S is invertible. Therefore

```text
rank(G+Delta) = r + rank(H+Delta_S)
             >= r + s - (8-r) = s+2r-8.          (1)
```

If r=8, H=0 and the rank is exactly 8+s. If r=7, a nonzero normal to X_J
gives a nonzero root-code vector supported on S. Premise 1 gives s>=53,
and (1) gives rank(G+Delta)>=59. If r<=6, the preceding subspace bound
gives |J|<=42, hence s>=70. Rank subadditivity alone then gives
rank(G+Delta)>=s-8>=62. Thus every completion of rank at most 58 has
r=8 and rank exactly 8+s.

Conversely, if s<=q-8 with q<=58, then s<=50. Premise 1 implies that
X_J spans all eight dimensions, since at most 50 rows were removed.
The r=8 equality gives rank(G+Delta)=8+s<=q. This proves both directions
for arbitrary complex diagonal values. The finite checks below do not
enumerate those values; the written rank argument provides that scope.

## A rank-59 witness

Take the live root alpha=(1,1,1,1,1,1,1,1) and c=X alpha. Let S=supp(c)
and let D_S be the diagonal projection onto those coordinates. Exact
enumeration gives |S|=53 and rank(X_J)=7. The new completion is

```text
K = G - 112 D_S.                                  (2)
```

The P112 tight-frame identity is X^T X=112I. Consequently P=G/112 is the
orthogonal projection onto U=col(X). Let V be the coordinate subspace on S.
Since X_J has rank seven, dim(U intersect V)=1. Also dim(U)=8, dim(V)=53,
and dim(U+V)=60. For two orthogonal projections P,D_S,

```text
ker(P-D_S) = (U intersect V) direct_sum (U^perp intersect V^perp).
```

Indeed, if Px=D_S x=y, then y belongs to both images and x-y belongs to
both kernels. The converse is immediate. The two summands have dimensions
one and 112-60=52. Thus K has nullity 53 and rank 59. Its correction has
53 nonzero diagonal entries, so additivity would predict 61. This proves
that the lower-rank range cannot include 59. On the convention G/2,
replace the coefficient -112 by -56.

The standalone verifier constructs (2) and obtains rank 59 by exact
rational elimination. It also checks Kc=0, the tight-frame identity,
the 53-position support and the rank-seven unchanged rows. It checks all
12,432 off-diagonal entries against G. This is a finite witness and a
scoped universal proof, not a failed search.

## Reproduction and verification

From the repository root, CPython 3.12 and standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p112-diagonal-rank-boundary/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/p112-diagonal-rank-boundary/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p112-diagonal-rank-boundary
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p112-diagonal-rank-boundary --check-source-history
```

Any CPython 3.12 path may replace the displayed interpreter. Expected status
is `PASS_P112_DIAGONAL_RANK_BOUNDARY`, with first nonadditive rank 59.
Each run prints a generated receipt with SHA256 hashes of all five package
files. Optional `--receipt /absolute/scratch/new.json` saves the receipt
outside the package and refuses to overwrite an existing file. No receipt
is hand-written or committed.

Eight direct completion fixtures cover diagonal-support sizes 21,31,40,50,
with two distinct support/value patterns at each size. Their ranks are
29,39,48,58 respectively. A separate five-row, three-dimensional fixture
checks (1) on all 32 supports and four nonzero correction values, giving
128 cases. Six controls reject a false rank-58 witness, extending additivity
through 59, the wrong projection scale, an omitted correction, a forbidden
off-diagonal edit and confusion with the odd-only mask. Checks remain
enabled under optimization. The verifier imports no predecessor code.

## Scope, sources and implementation limits

The scientific base is canonical main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7.
SOURCES.json pins the task, selected record and predecessor proof texts as
historical provenance. There are no live predecessor executable inputs.
The complex-rank-shape-decoder card changes to an algebraic side question
following #1313's explicit handoff. Ordinary completion rank is not a
recursive child rank, so no packing-cap or physical-budget inference is
made. The card's historical positive control raises
`KeyError: 'complex_profile'` under the changed selected schema. The current
selected source-binding orientation passes with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; this is metadata orientation only.

Credit Arham-Tahir64 #1313 for the diagonal-mask question and pivot method;
woklerx #1447 for the code-distance premise and #1077 for complex-coefficient
scope; themilkman216 #968 for the root-flat framework; DreamingOfClouds
#717/#595/#446 for the geometric decoder model; Mihir Srivastava #845,
Joel Pulikkan #620, icekylinx and the retained E8/Hamming lineage for their
predecessor contributions. Schur rank inequalities and the difference-of-
projections identity are classical. The new application gives the sharp
diagonal-completion threshold. Predecessor files and credit are unchanged.

Independent human and formal proof-kernel review are unclaimed. The proof
retains the cited geometric premises. No copied-information optimum,
arbitrary off-diagonal mask, rounded identity, physical source access,
dirty-workspace schedule, native realization, compiler, stock, tape,
precision or analytic transfer is supplied. Lean, Docker and a selected
operator replay were not run. No unknown physical cost is priced as zero.
The first verified improvement ends discovery; no construction expansion
or larger-rank classification follows.

The exact verifier is the retained evidence artifact. Functions have
fewer than 60 lines, with no recursion or dynamic code
execution. Root lists have at most 120 elements, normal pairs number 7,140,
and elimination matrices have at most 112 rows and columns with integer
inputs bounded in absolute value by 224. Fixed allocation requires a
managed-runtime deviation: Python allocates integers, fractions and lists
during these finite computations. The fixed dimensions bound live storage;
Hadamard's bound controls the elimination minors. This deviation is
confined to the standalone verifier. A fixed-storage implementation is
a follow-up only if this becomes a persistent service or accepts larger
inputs. Warning-strict ordinary and optimized commands are registered;
no separate static analyzer is configured for this package.

## Open next questions

1. Which diagonal corrections attain the first nonadditive rank 59?
   Begin with r=7, s=53 and the rank-one Schur complement in (1), retaining
   arbitrary complex diagonal values. A complete minimum-support codeword
   classification and its parameter equivalences remain needed.
2. Does a specified diagonal-completion factorization change any complete
   paid decoder bill? First state whether the caller allows changed diagonals
   and price its repair. This rank boundary supplies no copied-information,
   physical realization or restoration contract; those obligations block a
   supplier or kappa claim.

Structured questions are in TASK.json.
