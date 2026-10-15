# One mixed good/fallback weight descriptor

The contribution is an explicit descriptor and its executable continuation,
not a new normal-form or fallback theorem. Diagonal covariance is retained
from source527 and Ross Richardson's PR #2159. Jose Manuel's PR #2171
implements good-only ancestral weights and asks for a mixed path. This note
gives the row and atom indices for its diagonal-pair subcase. The selected
good-child binding is from commdata2338's PR #2160. Exact heads and proof
hashes are in [SOURCES.json](SOURCES.json).

## 1. Conditional interface

Let `R = Z/q^w`, with q an odd prime and w >= 1. An ADDRESS residual on
`N = 2m` coarse fields acts independently on f atom columns. Its full
unweighted matrix M is invertible over R, with determinant +1 or -1.
At column j its weighted matrix is

```
M_j = B_j M B_j^-1,
B_j = diag(b_0(j), ..., b_(N-1)(j)),
b_i(j) = A[i*f+j] if i < m, and 1 otherwise.
```

Every A entry is a unit. M and A depend only on exposed parent/ancestor
fields and fixed labels, never active ADDRESS values, VALUE payloads, or
fresh descendant stock. These are explicit premises. The native selected
to stopped-GL domain bridge is not proved here.

For n incoming head atoms set `f=floor(n/m)>0`, use the first mf head
atoms and the corresponding reversed tail block, and retain the peeled
remainder as spectators under the inherited peeling contract.

The first field of a diagonal pair has index i < N-1; its partner is N-1.
Physical atom t represents logical column `sigma_i(t)=t` or `f-1-t`.
The selected layout uses the first orientation for heads and the second
for tails. This map matters even when both fields are reversed.

## 2. The row-permutation quotient

Run unnormalized unit-pivot Gaussian elimination on M, clearing all other
rows at each stage and retaining zero shear slots. Choose the first unit
in the current pivot column. Let D be the final diagonal, with entries
d_i. Track original row labels through swaps: `pi(i)` is the original row
occupying final row i, not the list of pivot choices.

For one column abbreviate B_j to B. During elimination the weighted and
unweighted matrices satisfy

```
T_weighted = L T_unweighted B^-1,
```

where L is diagonal and initially equals B. A row swap S changes L to
`S L S^-1`. A shear clearing row i using pivot row k has weighted
coefficient `(L_i/L_k)` times the unweighted coefficient: the right
diagonal entry cancels from the quotient of entries in the same column.
This shear preserves the displayed relation.

Unit scaling preserves the low-residue zero pattern, so both runs choose
the same first unit row at every step. At termination `L_i=b_pi(i)(j)`:

```
d_i(j) = d_i * b_pi(i)(j) / b_i(j).                          (1)
```

All divisors are units. The row itinerary is determined by M modulo q,
but d_i must be computed over the full ring. Replacing M by its low
representatives can change d_i with no change of itinerary. Incoming A
values likewise need their full ancestors.

The physical descriptor for the weighted reversed child is

```
a_child[t] = d_i * b_pi(i)(sigma_i(t)) / b_i(sigma_i(t)).      (2)
```

`FallbackPair.value` implements (2). Its possible incoming reads are
`pi(i)*f+sigma_i(t)` and `i*f+sigma_i(t)`; a tail-bank read becomes the
constant 1. Both head indices lie in the parent's first mf atoms. The
fallback generally has no same-flat-index product rule.

## 3. Composition with good ancestors

For the retained northeast good normal form whose active head coordinates
are `0,...,r-1`, source527 and PR #2160 give

```
A_good[k*f+j] = A_parent[k*f+j] * delta_k.                    (3)
```

Delta is the unweighted full-ring pivot vector. `Good.value` implements
(3); no different `i_k` map or unbound local-frame label is assumed.
Starting with a unit root weight, (2) and (3) inductively give only units.
Every node reads older permitted controls and at most two entries of the
previous descriptor. A requested weight can therefore be generated
without a supplied ancestor-weight oracle or access to unused child stock.
This also covers a good node after a fallback node: its incoming descriptor
is the fallback's, not the original root array.

This closure statement covers the named good normal forms and fallback
diagonal-pair children. It does not compile all fallback shear coefficients,
arbitrary role labels, or complete selected invocations.

## 4. Source-bound rank-42 example

The pinned selected template has idle child 6, rank 42, from level 2 to
level 8 on pair 0. Copy 213 hosts no part of it. Its retained projector is
`P0=diag(0_22,I_42)`; the selected receipt contains 288 rank-42 children.
The verifier authenticates the template, its decoded hash and selected-word
binding, and the PR1094 assembly's Git-blob citation of PR589's receipt.

For the GL-domain examples, S sends P0's last 42 axes to the first 42.
Each chart is explicitly `g=h S`. This is a chart in the assumed GL orbit,
not an uncharged physical route or an emitted orthogonal-cover invocation.

Modulo 25, a good ancestor has disjoint blocks `[[1,1],[c,1+c]]` on axes
`(0,43),(1,42),(25,44)`, with c=5,10,15. All determinants are one. Exact
northeast elimination gives `delta_0=6`, `delta_1=11`, `delta_25=16`, all
others one. At root column width 5 its child has 210 atoms and
`A[x]=delta_floor(x/5)`.

The next parent uses f=3 and peels 18 atoms. Its chart has blocks
`[[5,4],[1,1]]` on `(0,43)` and `[[1,0],[1,1]]` on `(1,42)`, both of
determinant one. Its projector has `P[0,0]=5`, a nonzero nonunit, so the
generic good branch is unavailable. Its full 128-coordinate residual is

```
M = [[I-P, P C_64], [C_64 P, I-C_64 P C_64]].
```

This is an involution of determinant one. Its exact fallback plan gives
`pi(1)=42, d_1=-1` and `pi(126)=1, d_126=1`.
For the first pair, (2) reads two different ancestor locations:

```
numerator:   A[126], A[127], A[128] = 16,16,16
denominator: A[3],   A[4],   A[5]   =  6, 6,11
child:       -16/6,  -16/6,  -16/11 = 14,14,19 mod 25.
```

Field 126 has denominator one and reversed first-field orientation, so
its descriptor is `A[5],A[4],A[3] = 11,6,6`. Omitting orientation gives
`6,6,11`; using only the good ancestor's low residues gives `1,1,1`.

A further fixture starts with 6,400 atoms. Its good child has 4,200; the
bad parent uses f=65 and peels 40; the diagonal-pair child has 65. The next
good parent uses f=1, peels one atom and produces 42 weights. Entries
`0,1,29,30,41` are `16,21,11,6,6`. A separate forward-elimination oracle
computes all 65 incoming fallback weights before the final comparison.
This exercises a good/fallback/good descriptor chain, with callees still
conditional.

## 5. Chronology, reversals and charges

The completed weighted reversed-child premise is

```
F_a(H,D) = (diag(a) C_f D, C_f diag(a)^-1 H),
```

preserving exposed controls and complete spectators and restoring its row.
A logical diagonal pair is `J_a J_1`: execute J_1 first, then J_a.
For equal field orientations, each ordinary swap is `R_tail F_a R_tail`.
Each reversal is one unweighted reversed child on the first/last
`floor(f/2)` atoms, with a possible middle atom fixed. The tested tail126
pair at f=3 thus pays six children of widths `1,3,1,1,3,1`. For opposite
orientations each swap is already a reversed child: field1's pair uses two
width-three children. In both cases the physical weights are (2).

No reversal or variable scaling is free. The inherited fallback allowance
remains

```
6N(N-1) + 3N + 6(N-1) = 98,682 < 32*64^2 = 131,072,
```

with every child at most f atoms. This is the prior conservative allowance,
not a selected cost improvement. The preceding good call still pays its
one 42f child and adapters. Later-target shifts, the fixed determinant
sign, preparation and required routing remain charged.

For fixed q and m=64, an unweighted plan needs a fixed number of ring operations
on O(w)-digit values and is prepared from the full exposed chart once.
A good descriptor follows one parent index; (2) follows at most two. With
D ancestors a direct depth-first evaluator uses at most
`O(2^D poly(w,log n_root,D))` control work per value, and
`O(D(w+log n_root))` storage for fixed-dimensional prepared data and its
stack. The executable realizes this finite recursion; no memoization or
unit-cost arbitrary-prefix oracle is assumed.

As in source527 and PR2171, impose `n_root<=E0`,
`D<=c(1+log2 E0)`, and `w=ceil(E0^s)` for fixed `0<s<1`. Then
`2^D<=C E0^c` and `E0<=w^(1/s)`, making preparation polynomial in w.
It must remain in the retained ordered-affine tape estimate:

```
T_adapters <= N_slots V (C + 2 E_max / q^w).
```

Only under that stopping relation does the complete fiber absorb the
polynomial preparation. For unrelated w and D retain E_max explicitly.
This supplies a descriptor to the interface, not a new execution of its
physical tapes or proof of the weighted callee.

## 6. Evidence and limits

The replay checks 46,848 cases: all 1,344 determinant +/-1 matrices of
size two modulo 3 and 9, each under every unit diagonal conjugator. The
oracle uses normalized forward elimination; the compiler uses unnormalized
all-row elimination. Four selected-size fixtures check all 127 diagonal
pairs in both orientations over 11 weighted columns, with full operator
reconstruction. The additional mixed chain checks 65 fallback and 42 good
weights. The same-orientation test covers 5,625 complete coordinate-pair
and stock cases; the opposite-orientation test covers six basis columns.
Fifteen semantic controls reject.

Small primes are arithmetic fixtures, not admitted selected primes. This
is a written conditional proof with author-run exact evidence, not formal
kernel verification, external independent review, a complete high-fiber
census, native admission, or a new exponent. The stopped-GL/orthogonal-cover
bridge, other local-frame bindings, all fallback instruction descriptors,
completed weighted callees and internal borrowing, physical scheduling,
restoration, full invocation hosting, precision and outer transfer remain
outside this result.
