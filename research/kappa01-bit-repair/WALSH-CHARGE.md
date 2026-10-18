# A character-rank constraint on asymmetric scalar queries

For binary rank-k ports and complex scalar queries, the complete
support-pairing tariffs obey the dimension-dependent inequality

```
sum_j (2^r_j - 1) >= V*(2^k - 1).                         (1)
```

This is a constructive test of the remaining low-tariff route. A term with
`r_j<k` can help cancel forbidden off-diagonal entries, but cannot contribute
to the diagonal. Such cancellation does not evade (1). In particular, at
`(h,k)=(8,3)`, a decoder restricted to tariffs at most six has a two-bank
target floor greater than `1.023562078533451`; the pressure test below also
rejects it for general W. Any viable decoder in this model
must use rank-seven or rank-eight queries. Those higher ranks remain open:
the rank-eight relaxation is below one and is not a construction.

## Exact model

Let `E_1,...,E_V` be k-dimensional subspaces of a binary h-dimensional
space with bilinear pairing B. Its restriction to `E_i x E_i` is required
to be nondegenerate. Repeated ports are permitted. A scalar fitting matrix
K over the complex numbers, or `Q(i)`, has `K_ii=1` and

```
K_ij=0 unless B(E_i,E_j)=0,          i != j.
```

Thus full orthogonality is the free mask. Factor K by actual scalar queries,

```
K = sum_j u_j v_j^T.
```

For a term let U be the span of all port spaces in its nonzero reader
support and T the corresponding source span. Its charged rank is
`r_j=rank_F2(B restricted to U x T)`. Source and reader supports and
coefficients may be unrelated. All cancellations are allowed. No symmetry
or positivity of K is imposed. Each query is charged separately; this is
not a statement about a joint operation serving several scalar totals.

The geometry is binary while the scalar field has characteristic zero.
This binary-character version does not directly apply to the selected bit
supplier's rational labels with binary scalar registers. It does apply to the binary-port/complex-query
geometries considered as replacements in this investigation.

## Proof by a nonconstant character matrix

Replace scalar entry `K_ij` by a block indexed by `x in E_i`, `y in E_j`:

```
L_(i,x),(j,y) = K_ij * [(-1)^B(x,y) - 1].
```

For `i!=j`, either K vanishes or the pairing is zero on the whole block.
Thus L is block diagonal. On its i-th diagonal block, nondegeneracy gives
the binary character table H of order `q=2^k`, minus the all-ones matrix J.
It has rank `q-1`. To see this exactly, order zero first. H has first row
and column all ones and `H H^T=q I`, so it is invertible. The Schur
complement of its top-left entry is the lower `(q-1)` square block of
`H-J`, and is invertible. The zero row and column of `H-J` give

```
rank_C(L) = V*(2^k-1).                                   (2)
```

Now lift one query in the same way. Remove the left and right kernels of
the pairing on `U x T`. The resulting quotient spaces both have dimension
`r_j` and pair nondegenerately. The kernel
`(-1)^B(x,y)-1` depends only on those quotient classes. Therefore the
query's lifted matrix is obtained from the order-`2^r_j` matrix `H-J` by
repeating or selecting rows and columns, then multiplying each row by
`u_j(i)` and each column by `v_j(j)`. Its rank is at most `2^r_j-1`.
Rank subadditivity and (2) prove (1). A rank-zero query lifts to zero.

Repeated ports cause no difficulty: they have separate index blocks,
their mutual nondegenerate pairing forces the original fitting matrix to
vanish off-diagonal between the copies, and (2) counts every copy.

## What low-rank cancellation can and cannot do

If a query is nonzero on the diagonal at port i, both complete support
spans contain `E_i`. Its tariff is then at least k. More generally, a query
of rank less than t vanishes at every ordered port pair whose cross-pairing
has rank at least t. This observation alone does not allow deletion of
low-rank queries: their off-diagonal contributions may be essential.

A checked example in `F2^6` uses

```
E_1=span(e_1,e_2,e_3),    E_2=span(e_3,e_4,e_5).
```

Both ports have rank three, and their cross-pairing has rank one. Their
fitting matrix is the two-by-two identity, with the asymmetric query
decomposition

```
I_2 = [1,1]^T*[1,1] - [1,0]^T*[0,1] - [0,1]^T*[1,0].
```

The tariffs are `5,1,1`. The two rank-one queries have zero diagonal but
cancel the forbidden off-diagonal entries. Deleting them destroys the
fitting property. The total charge is seven, exceeding the direct charge
six; this is a positive control for the cancellation mechanism, not a
successful cost repair. The verifier constructs all three lifted matrices,
checks their exact sum and ranks, and checks the full support tariffs.

## Native mass and target moment consequences

For positive integer r, both `r/(2^r-1)` and
`r^(8/9)/(2^r-1)` decrease strictly. Indeed
`(1+1/r)^(8/9) <= 1+1/r <= 2`, whereas
`(2^(r+1)-1)/(2^r-1)>2`. Thus a uniform query-rank cap R gives

```
C/V >= R*(2^k-1)/(2^R-1),
sum_j r_j^(8/9)/V >= (2^k-1)*R^(8/9)/(2^R-1).             (3)
```

The automatic cap is `R=h`. Within the three-stage coverage and separate
active-climb model of [PROOF.md](PROOF.md), put `m=3h-2k` and define G by

```
G = 3*((h-k)/m)^(8/9)
      + (3/2)*(2^k-1)/(2^R-1)*(R/m)^(8/9).               (4)
```

For two data banks, `W=2V`, this is the absolute moment lower bound
`M(1/9)>=G`. The coverage proof permits general W as well. Writing P for
pressure and D for deficit as in that proof gives

```
P-D >= 2*V*m*(G-1),
M(1/9) >= 1+(2V/W)*(G-1).
```

Thus `G>1` excludes the target for any W in that model; G itself is not a
uniform absolute moment bound when `W>2V`. The table and receipt use the
two-bank normalization for their displayed moment floors.

All other costs are granted free in G. Splitting a separately charged rank-r
query into smaller children cannot lower its `8/9` moment. Fusing different
queries or active climbs changes the hypotheses.

| h | k | cap R | Two-bank floor G, displayed downward | Consequence |
|---:|---:|---:|---:|---|
| 3 | 1 | 3 | 1.086059162874567 | All such binary-port scalar decoders fail |
| 4 | 2 | 4 | 1.036905740515933 | All such decoders fail |
| 5 | 2 | 5 | 1.017273567501908 | All such decoders fail |
| 6 | 2 | 6 | 1.018790703056608 | All such decoders fail |
| 6 | 3 | 5 | 1.030443929272086 | A viable decoder needs rank-six queries |
| 6 | 3 | 6 | 0.964901757923112 | Relaxation passes; no decoder supplied |
| 7 | 3 | 6 | 1.000366619854099 | A viable decoder needs rank-seven queries |
| 7 | 3 | 7 | 0.968547347614850 | Relaxation passes; no decoder supplied |
| 8 | 3 | 6 | 1.023562078533451 | A viable decoder needs rank-seven or eight queries |
| 8 | 3 | 7 | 0.996503379474117 | Relaxation passes narrowly |
| 8 | 3 | 8 | 0.980819865933461 | Relaxation passes; no decoder supplied |

The mass-only comparison is also decisive at the previously enumerated
small dimensions. For `(h,k)=(5,2)`, (3) gives `C/V>=15/31`, exceeding the
necessary allowance `C/V<0.367823...`. For `(6,2)`, it gives `C/V>=2/7`,
exceeding `0.126092...`. These conclusions cover arbitrary ports with
multiplicities and any qualifying binary bilinear form, without graph
enumeration. At `(8,3)`, the full-rank mass floor is only `56/255` per port,
below the allowance `0.429937...`; the result deliberately leaves that
higher-dimensional regime open.

The `(5,2)` and `(6,2)` exclusions extend to every allowed odd stage count
under the same coverage and active-climb hypotheses. For `(5,2)`, (3) gives
`sum r_j^(8/9)/V >= 3*5^(8/9)/31 > 2/5`; the last inequality has the integer
witness `62^9 < 15^9*5^8`. This supplies at least the query coefficient used
in the all-stage pressure proof in [PLANE_REPAIR.md](PLANE_REPAIR.md), so
that proof applies without its plane enumeration. For `(6,2)`, the
data-only obstruction in [PROOF.md](PROOF.md) already excludes every odd
stage count at least five; (4) supplies the remaining three-stage gate.

## Conditional corollary for rational bit labels

There is also a bit-side application with a separate arithmetic hypothesis.
For label geometry over a prime field `F_p`, replace `(-1)^B` by `zeta^B`,
where zeta is a primitive p-th root of unity in an extension of the scalar
coefficient field. Provided the scalar characteristic differs from p, the
character table is invertible: multiplication by the table of inverse
characters gives `p^r I`. The same proof yields

```
sum_j (p^r_j-1) >= V*(p^k-1).                            (5)
```

In particular, binary scalar coefficients can be extended to a finite
field containing p-th roots for any odd prime p.

Now fix a rational-label/binary-scalar instance with an integral
presentation: an integer ambient pairing matrix and integer basis columns
for each rank-k port. Suppose each port Gram determinant is nonzero modulo
the chosen odd prime p. Reduction modulo p preserves each port's rank and
nondegeneracy, and every originally orthogonal pair remains orthogonal.
Each query's full pairing matrix is integral; its reduced rank is at most
its rational rank. Applying (5) to the reduced geometry therefore proves
(5) with the original rational query tariffs. No claim is made that an
arbitrary rational port system has such a presentation for a specified p.

For `h=3,k=1`, a good reduction at p=3 implies `C/V>=3/13`; at p=5 it
implies `C/V>=3/31`. Both exceed the target allowance
`0.063046005269...`. Thus these good-reduction subclasses cannot repair
the rational bit geometry, including indefinite forms satisfying the
stated arithmetic condition. Merely removing positive definiteness is not
enough in these subclasses.

The argument can be applied just to ports whose Gram determinants are
units in the fixed integral presentation. If their fraction is f, the
same respective floors become `3f/13` and `3f/31`. The exact receipt
records the resulting upper bounds on f for a putative target repair.
This is a constraint on an explicit integral presentation, not a universal
claim about all rational labels or arbitrary bit circuits.

## Exact replay and remaining construction

```sh
python3 -I -O -B research/kappa01-bit-repair/walsh_charge.py
```

The verifier checks character orthogonality through rank eight, exact
small character-matrix ranks, the explicit asymmetric cancellation example,
and rational enclosures for all listed gates, including the two conditional
odd-prime bit gates. It compares its result with
`WALSH-RESULT.json`. The interval routines and pressure proofs are pinned
in `WALSH-SOURCES.json`; existing packages are not modified.

The next candidate must use high-rank queries efficiently enough to satisfy
(1), while its low-rank corrections and all other required work fit the
remaining moment budget. This character bound does not provide such a
factorization and does not establish kappa 0.1. It is a necessary condition
within the stated scalar-query model. Prepared with substantial OpenAI
Codex assistance and an independent AI review of the central rank argument.
Apache-2.0.
