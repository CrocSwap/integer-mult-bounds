# A complete cost obstruction for one changed scalar pair placement

Prepared for **@CubeJerry with substantial OpenAI assistance**. Apache-2.0.
This is a scoped coefficient-space and recursive-invoice result, not a new
multiplier, physical caller, kappa claim, or change to the selected frontier.

## Statement

Work over a field K of characteristic different from two. In the canonical
shortest nine-query word on eight independent fields, place one common
rank-four stage projector P at sites (1,2) and a commuting common projector Q
at sites (5,6). Require local query compatibility and commutation with the
**actual chronological prefixes** at all four sites.

1. Q has rank at least five, for arbitrary ordinary scalar projectors.
2. If Q has rank five, its form is determined below. Adding commuting rank-two
   full sites at the two endpoints forces the main target incidence
   `B×2, AB×1, C×3, CD×1, ABCD×1`, where B and C each denote the product of
   the bodies at their paired sites.
3. Even granting two independent paid idle fragments with either orientation,
   the rank-(2,4,4,5,5,2) construction with exactly one granted fragment in each
   pure paired bank has a strictly worse complete
   recursive signed invoice than an allowed allocation of the frozen #6726
   root, for every positive child allocation, every binary child tree and
   every saving `0<k<1`.
4. The same one-fragment-per-pure-bank contract loses for every larger
   second-pair rank, by the complete eight-inventory comparison in section 6.

The rank-five placement is not merely hypothetical: the exact integer fixture
and formal arbitrary-input query/stage identity are checked by `verify.py`.
Its paid fragments are **optimistically granted**, not constructed. This
strengthens the negative conclusion; refusing an unproved fragment or adding
ordinary/physical completion charges cannot improve the invoice.

## Contract and inherited ingredients

For `0<=i<8`, put `u_i=e_i`, `(v_i)_j=sign(i-j)`. Put
`u_8=(-1,1,-1,1,-1,1,-1,1)^T`, `v_8=(1,...,1)`,
`R_i=u_i v_i`, and `B_i=(I-2R_i)...(I-2R_0)`.
A projector at i satisfies `P R_i=R_i P=R_i` and `[P,B_i]=0`.
Selected projectors commute pairwise. All main inputs are arbitrary and
independent; there is no initialized or discarded input.

The complete shortest scalar/coupled normal form and the image/row inequality
are inherited from Ali Romman and the credited source chain. The latter says
that a projector containing image space A and supporting row space C has rank
at least `dim(A)+dim(C)-rank(CA)`. The canonical prefix formulas and their
characteristic scope are retained in the #6717/all-even extension cited in
`ORIGINS.json`. Ordinary common conjugation preserves every claim here.

Cinna Davis supplies the native and binary supplier lineage. #6726's two paid
fragments, root and caller are credited to zxv/OpenAI Codex and the retained
preceding authors; this note does not claim those constructions as new.

## 1. Every rank-four projector at the first pair

Split coordinates into the first three and the last five, numbered 3 through 7.
Let `k=(1,-1,1)^T`, `h3=(1,1,1)` on coordinates 0,1,2, and
`r=(1,1,1,1,1)` on coordinates 3 through 7. When used in eight-dimensional expressions, k and z are embedded in their
respective coordinate blocks with zeros in the other block. Every rank-four
common projector at sites (1,2) has exactly the form

```
P = [[I3, k a], [0, z r]],       r z=1, a z=0.             (1)
```

Compatibility and actual prefix commutation force the image hull
`span(e0,e1,e2)` and row hull
`span(e0^T-e2^T,e1^T+e2^T,r)`. Their dimensions are 3,3 and their pairing rank
is 2. These hulls force the block form except for its lower-right block.
Rank four makes that block rank one; its fixed left row r gives `z r` with
`r z=1`. Idempotence forces `a z=0`. Conversely (1) satisfies both actual
prefix conditions and is an idempotent of rank four.

## 2. Every projector at the second pair contains a forced rank-four part

Write `a4=(1,-1,1,-1,1)^T`, `h5=(1,1,1,1,1)` and

```
E = diag(a4 h5, I3).                                      (2)
```

Every compatible idempotent Q at sites (5,6), commuting with both actual
prefixes, satisfies `Q E=E Q=E`.

Here is why idempotence and the prefix condition matter. Decompose the space
as `H=ker(E)` and `V=im(E)`. Both prefixes act as `-I` on H. In the ordered
basis `(a4,e5,e6,e7)` of V, their action is exactly the four-dimensional
canonical pair (1,2). The forced image and row hulls in V have dimensions
3,3 and pairing rank 2. The common right `-1` eigenspace of the two reduced
prefixes is `span((-1,1,0,0)^T)`; it has zero intersection with the kernel of
the forced row hull. The common left `-1` eigenspace is
`span((1,1,0,0))`; it has zero intersection with the annihilator of the forced
image hull. Consequently the two off-diagonal blocks of Q between H and V
vanish. Its V block is idempotent and has rank at least four by the inherited
inequality. It is therefore `I_V`, proving (2). This argument uses the actual
prefixes, not just the two local nilpotents.

## 3. Q is the identity on ker(P)

Because P and Q commute, `W=(I-Q)(I-P)=(I-P)(I-Q)` is an idempotent.
The first ordering gives `EW=0`; the second gives `WE=0`, using (2).
No commutation of P with E is assumed. Equation (2) therefore implies
that its image lies in `ker(P) intersect ker(E)`, and its row space lies in
the corresponding common left kernel.

Compute these spaces directly from (1). A vector in the common right kernel
must be zero in coordinates 5,6,7; its remaining tail entries sum to zero.
It follows that this common right kernel is either zero or
`span(e3-e4)` (the latter requires `a3=a4`). A row in the common left kernel
must be zero in coordinates 0,1,2,5,6,7, and its entries at 3,4 must agree.
It is therefore either zero or `span(e3^T+e4^T)` (the latter requires
`z3+z4=0`). These possible one-dimensional spaces pair to zero. Thus `W^2=0`.
As W is idempotent, W=0, and

```
Q(I-P)=I-P.                                               (3)
```

In particular Q already has rank four on ker(P). Its action on im(P) cannot
be zero, since `P E` is nonzero. Hence `rank(Q)>=5`.

## 4. Rank five forces one target inventory

Assume rank(Q)=5. Then `T=QP` is a rank-one idempotent supporting `P E` on
the image side and `E P` on the row side. Both have rank at most one.
Equation (1) gives the columns of `P E`, in the four-coordinate basis of (2),
as

`alpha*k, a5*k+z, a6*k+z, a7*k+z`, where `alpha=1-a3+a4`.

Its rank is at most one only if `alpha=0` and `a5=a6=a7=s`.
The rows of `E P` include `(h3,a+(z3+z4)r)` and the three rows
`z5*r,z6*r,z7*r`. Their rank is at most one only if `z5=z6=z7=0`.
Using `r z=1` and `a z=0` now gives

```
z=(z3,z4,0,0,0)^T, z3+z4=1,
a=(z4,-z3,s,s,s),
w=s*k+z,  c=(h3,a+r),  delta=c*w=s+1 != 0,
T=w*c/delta,   Q=I-P+T.                                  (4)
```

If delta were zero, no rank-one idempotent could contain w and support c.
Conversely (4) is the complete rank-five common-pair solution.

Let L,N be commuting rank-two endpoint projectors at sites 0,8, commuting
also with P,Q. P already supports R0, and Q already supports R8. Consequently
`L<=P` and `N<=Q`: their commuting intersections support a nonzero square-zero
query and must have rank at least two.

The joint (P,Q) spaces have dimensions `(1,3,4,0)` for membership patterns
`(1,1),(1,0),(0,1),(0,0)`. Endpoint 0 has nonzero paired components in the
first two sectors: `v0 T u0=-1/delta`. Endpoint 8 has nonzero paired components
in the first and third: `v8 T u8=delta`. Therefore L and N each occupy the
entire common one-dimensional sector and one line in their respective
exclusive sectors. The complete incidence is forced:

| Main target | Multiplicity |
|---|---:|
| B | 2 |
| AB | 1 |
| C | 3 |
| CD | 1 |
| ABCD | 1 |

This is a universal inventory consequence under the stated rank-five and
endpoint hypotheses, not an inference from the finite fixtures.

## 5. Full recursive invoice and pointwise stop

Use six positive child sizes `(a,b,c,d,e,f)`. Let A have a leaves, B have b+c,
C have d+e, and D have f. Write `F=a+b+c+d+e+f`, `H(x)=x^(1-k)` and
`i(n)=H(8n+1)-H(8n)`. Retain **all** native paid children and productive helpers,
all six binary child trees, their internal idle jobs and thin queries, and
three root thin queries. Let their common native/binary contribution be G.
The eight root targets before fragmentation contribute

`H(8F+1)+H(8(a+b+c)+1)+H(8(d+e+f)+1)+2H(8(b+c)+1)+3H(8(d+e)+1)`.

The whole paired-bank idle bill is
`2H(8(b+c))+3H(8(d+e))`. Both are complete debits; none of the larger pair's
third idle is omitted.

Grant one independent fragment in each pure B/C group. A split of B into
head-free rank 8b and header-bearing rank 8c+1 replaces its original target
`H(8(b+c)+1)`; it also replaces one paid idle by paid ranks 8b and 8c.
The net change is exactly `i(c)-i(b+c)`. The other orientation replaces c by b.
The analogous C change is `i(d)-i(d+e)` or `i(e)-i(d+e)`.

The best granted signed moment is thus

```
G + H(8F+1)+H(8(a+b+c)+1)+H(8(d+e+f)+1)
  + i(b+c)+2*i(d+e)+max(i(b),i(c))+max(i(d),i(e))-3.       (5)
```

For #6726's frozen root, choose the orientation-compatible ordered child
allocation (swapping the two children within either pair if needed). Its
complete moment is exactly (5) with one `i(d+e)` removed and the final `-3`
replaced by `-2`. These swaps preserve all native counts and binary tree
invoices. Therefore the candidate minus that valid reference is

```
i(d+e)-1 < 0,                                            (6)
```

by strict concavity of `x^(1-k)` for `0<k<1`. This is a pointwise comparison for
every positive allocation and every binary subtree, rather than a numerical
search or a claim that equal local ranks imply identical circuits. Conditional on #6726's separately claimed frozen-model exclusion, this
dominance transfers its numerical ceiling to the rank-five placement on
`[0.0033072446849,0.004]`, even under the granted fragments. The exact source
is retained as `inputs/pr6726-allocation_tail.py`; the written statement is in
[the pinned all-size allocation note](https://github.com/zxv/integer-mult-bounds/blob/435bbe91fb28cb1d7a569ca70c6c4e9eb302d486/research/p104-paid-idle-fragmentation/frozen/RESEARCH-NOTES.md#all-size-allocation-ceiling-for-this-exact-complex-root).
That allocation-tail certificate is not replayed or independently admitted
here. Our new pointwise dominance (6) holds for every `0<k<1` independently
of that numerical certificate; no numerical ceiling is extrapolated beyond
its claimed range.

At `(4,4,1,1,4,4)`, the full signed histogram delta is
`+104 H(41) -104 H(40) -104 H(1)`. The checker reconstructs the complete native,
binary and root histograms and verifies this exact delta. The candidate has
13,670 productive fields and 66,956 paid requests in that granted invoice;
its rank-mass surplus remains 760. These are accounting figures for a rejected
optimistic construction, not an admitted physical caller.

## 6. Every higher-rank second pair also loses in this fragment contract

This accounting extension was independently derived alongside the literal
invoice review in `INDEPENDENT-INVOICE-REVIEW.md`. It uses the universal
geometry (2),(3), not an unproved construction at a larger rank.

For every second-pair rank, E supports the endpoint query R8. Thus the same
intersection argument gives `L<=P` and `N<=Q`. Moreover `LN` is nonzero:
otherwise `v0*u8=v0*L*N*u8=0`, contradicting `v0*u8=-1`.
The joint eigenspaces of L,P,Q,N therefore satisfy all of the following:
there are eight scalar coordinates, the L,P,N marginals are 2,4,2,
P and Q cover the space by (3), and the L/N intersection has dimension at
least one. To grant one pure B and one pure C fragment, each of those two
sectors must have positive dimension.

The only possible labels are B,AB,C,BC,ABC,CD,BCD,ABCD. These necessary
conditions give exactly eight inventories:

| rank Q | Necessary target inventory |
|---:|---|
| 5 | B², AB, C³, CD, ABCD |
| 6 | B², C⁴, (ABCD)² |
| 6 | B², C³, ABC, CD, ABCD |
| 6 | B, AB, C⁴, BCD, ABCD |
| 6 | B, AB, C³, BC, CD, ABCD |
| 7 | B, C⁴, BC, (ABCD)² |
| 7 | B, C⁴, ABC, BCD, ABCD |
| 7 | B, C³, BC, ABC, CD, ABCD |

There is also a short enumeration proof. Let x be the ABCD multiplicity,
which is one or two. If x=2, all other endpoint-bearing labels vanish,
C has multiplicity four, and the B and BC multiplicities sum to two.
If x=1, put u=AB and v=CD. Then `u,v` each belong to `{0,1}`,
`ABC=1-u`, `BCD=1-v`, `B+BC=1+v` and `C=4-v`.
The condition B>=1 gives precisely the table. No rank-eight Q permits a
pure B target. Some listed inventories may fail stronger geometry; allowing
them is favorable to the proposed construction.

Let `T_X=H(1+8*body_size(X))`, `J_C=H(8C)`, and use the rank-five row as
reference R5. Every rank-six row pays one more whole C idle. Native work,
binary nodes, root thin queries and the two granted-fragment corrections
are unchanged. The exact candidate-minus-R5 differences, in table order,
are

| Rank-six row | Complete signed difference |
|---:|---|
| 1 | `T_ABCD+T_C-T_AB-T_CD-J_C` |
| 2 | `T_ABC-T_AB-J_C` |
| 3 | `T_C+T_BCD-T_B-T_CD-J_C` |
| 4 | `T_BC-T_B-J_C` |

Rows 2 and 4 are strictly negative by
`H(x+y)-H(x)<H(y)` for positive x,y and `0<k<1`.
For row 1, diminishing increments give
`T_ABCD-T_AB <= T_CD-1`; for row 3 they give
`T_BCD-T_CD <= T_B-1`. Both differences are therefore at most
`T_C-J_C-1=i(C)-1<0`.

Every rank-seven row allows one C incidence to be deleted from a BC or ABC
label to obtain a listed rank-six row, preserving both pure groups. The
rank-seven minus rank-six difference is again
`H(x+y)-H(x)-H(y)<0`, with `y=8C`: the added C incidence earns less than its
extra paid idle. The independent checker retains an explicit deletion for
each row.

Thus every possible second-pair rank is retired for this placement and
this exact one-fragment-per-pure-bank contract. Rank four is impossible;
rank five loses by (6); ranks six and seven lose more; rank eight cannot
supply the required pure B group. This does not cover two fragments in one
bank, additional retirements, fragments from nonpure groups, a larger first
pair, different site placements, or changed native schedules.

## Evidence and limits

`python3 -I -B verify.py` checks canonical prefixes, the forced block geometry,
a literal rank-five integer fixture, all arbitrary-input polynomial matrix
entries in both central characters, the complete invoice delta, and a local-
compatibility fixture that fails the actual prefix condition. The written
arguments establish arbitrary-parameter scope; finite fixtures are not an
all-field proof kernel. The separate standard-library `independent_invoice.py` rebuilds every source
and candidate histogram, checks 16 allocation/orientation fixtures, and
enumerates all eight necessary inventories with their formal price reductions.
Exact sources and notices are retained in `ORIGINS.json`.

The settled domain is pair placement (1,2),(5,6) with a rank-four first pair,
any second-pair rank, rank-two endpoints, and exactly one granted fragment
in each pure B/C bank in the stated shortest scalar contract. Other placements,
additional retirements, two fragments in one bank, nonpure fragment groups,
cases with no pure B or no pure C group,
noncommon projectors at paired sites, longer words, coupled controls and changed
native suppliers remain outside the priced theorem.
No claim is made that all scalar roots are exhausted. No native supplier replay,
physical fragment construction, compiler qualification or all-size framework
assumption discharge was performed for this rejected candidate.

Open next question: a construction outside this settled fragment contract
needs an actual new retirement or changed site geometry and a favorable complete
invoice before further source qualification. Larger second-pair ranks alone
do not reopen this placement.
