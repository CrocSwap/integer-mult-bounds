# The weighted boundary for one z and one uz target

In the full formal model below, every fourteen-call word for
`diag([z],[uz],I_rest)` has counts `(n_a,n_b,n_c)=(4,6,4)`, for every finite
number of arbitrary restored dirty roles. In particular, five b calls require
at least ten outer calls. The direct word is therefore optimal at every
nonnegative uniform letter price satisfying `beta <= 2 min(alpha,gamma)`.

This is a written uniform argument plus complete finite quotient censuses.
It extends Nick Petalas's [PR2175](https://github.com/CrocSwap/integer-mult-bounds/pull/2175)
at `1d943bc9e0718c8a2f15e1d0a22b73ad528ef0ca`, whose unit optimum fourteen
and direct upper word are retained results. The new cases are its explicit
weighted handoff, `(5,5,4)` and `(4,5,5)`. The span, quotient and profile methods
retain the PR2027/1662/1680/1690 attribution; no new rank principle is claimed.

## Model and inherited algebra

Let `G=UT4(F2)`, `R=F2[G]`, and

```
a=I+E12, b=I+E23, c=I+E34,
u=I+E13, z=I+E14.
```

On any finite `r>=2` scalar roles, every paid call is
`D_N(g)=I+([g]+1)N`, with `g in {a,b,c}` and `N=xy^T` nonzero of rank one
over F2. Both idempotent and nilpotent couplings are allowed. Each factor is
an involution, since `([g]+1)^2=0`. Every occurrence, including restoration,
is charged. Arbitrary scalar GL mixing is optimistically free: conjugate it
into the couplings and normalize the final scalar map by augmentation.
The target and all paid factors augment to I, so that final map is I.

There are no free address maps, initialized extra roles, COPY, ERASE,
higher-rank unit calls or unpriced inverses. Every extra role starts arbitrary
dirty and must end as its own identity, without contaminating either target.
Equality is in `Mat_r(R)`, not a finite sample of input bits. The formal price
does not implement a physical recursive child.

Use the retained quotient

```
Q=F2<A,B,C>/(A^2,B^2,C^2, AC-CA, all monomials of degree >=4).
```

It has seventeen monomial basis elements. The retained checker verifies its
associativity on all `17^3=4913` triples and the map `a,b,c -> 1+A,1+B,1+C`
on all `64^2=4096` group products. The separate checker reconstructs the
quotient by commutation orbits of all forty words of degree at most three,
and the group by literal four-by-four binary matrices. A fixed ring map
extends entrywise to matrices of every finite role count.

The images are

```
u -> 1+AB+BA+ABA+BAB,
z -> 1+ABC+ACB+BAC+CBA.
```

Write `P=diag(1,1,0,...)` and `S=diag(0,1,0,...)`. Nonconstant products of
these root images have degree at least four, so the target has coefficient S
at `AB,BA,ABA,BAB`, P at `ABC,ACB,BAC,CBA`, and zero elsewhere except I.

For each label g, collect its coupling columns in X_g and rows in Y_g.
The zero first-degree coefficient gives `X_g Y_g=0`, and hence
`n_g >= rank X_g + rank Y_g`. All six spans contain the active two-coordinate
plane: use the first and last factors contributing to ABC and CBA for a,c,
and BAC and ACB for b. The commuting representatives BCA and CAB still start
or end with b, respectively; no scalar matrices are commuted.

For the b calls, set X=X_b, Y=Y_b. Let U have columns `A_j x_j`, where A_j is
the sum of earlier a couplings, and let V have rows `y_j^T C_j`, where C_j is
the sum of later c couplings. Chronological expansion gives

```
XY=0, UY=S, XV=0, UV=P.
```

Delete the second output coordinate with pi. Then `pi U` annihilates im Y
and V maps into ker X. Thus `pi P = (pi U)V`, of rank one, factors through
`ker X / im Y`. It follows that

```
n_b >= rank X_b + rank Y_b + 1.
```

This is PR2175's mixed-middle argument specialized to z/uz. In particular
`n_a>=4`, `n_b>=5`, `n_c>=4`, for every word length and every finite r.

## Compression at fourteen calls

Sum the three label inequalities. For a word of length L,

```
L >= 1 + sum_g(rank X_g + rank Y_g) >= 13.
```

If `L<=14`, the six integer ranks have total excess at most one above two.
Every span except possibly one equals the corresponding active plane by
containment. If the exceptional span is a column span, all row spans are
active; hence `NP=N` for every coupling. If it is a row span, `PN=N` for
every coupling. With no exception, both statements hold. This is ToikY's
PR1680 common-orientation argument applied to the mixed-middle inequality.

Split roles into the active plane and the dirty complement. All factors are
simultaneously block lower triangular or simultaneously block upper triangular.
Projection to the active corner is multiplicative over the full noncommutative
ring R: the discarded cross-block product is zero. The projected product is
therefore `diag([z],[uz])`. A projected coupling is an outer product and has
rank one or zero. Delete zero identity factors; each letter count can only
decrease. This proves compression uniformly in r and arbitrary dirty inputs.
Opposite orientations on different factors would invalidate the projection;
an explicit rejected feedback pair is checked in `controls.py`.

The only possible thirteen-call split is `(4,5,4)`. Its complete quotient
exclusion is replayed byte for byte from PR2175's receipt. Thus no projected
fourteen-call word can lose a factor: that would give a word of at most thirteen
calls. The only remaining fourteen-call splits are `(4,6,4)`, `(5,5,4)` and
`(4,5,5)`, with their exact counts preserved by compression.

## Complete new two-role censuses

There are nine nonzero binary rank-one couplings on two roles. Each legal
endpoint has zero first-degree sum for each label. Enumerate all `9^5` middle
sequences and retain their 3600 zero-sum sequences. For each outer count four
or five, enumerate every zero-sum coupling sequence and every nondecreasing
assignment of its calls to the six gaps around those five middle calls.

| Outer calls | Zero-sum sequences | Gap assignments each | Realizations | Distinct profiles |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 441 | 126 | 55,566 | 9,721 |
| 5 | 3,600 | 252 | 907,200 | 47,521 |

The profile stores each outer prefix sum at the five b calls; all concrete
realizations are retained. The predecessor's AB/BA/ABA/BAB equations for a,
and CB/BC/CBC/BCB equations for c, hold for either outer length. Their target
values are S and zero respectively. Zero total outer sum identifies the
suffix sums needed by the c screen. Transported column/row keys impose
`ABC=CBA=P` by exact parity equations; every compatible profile pair remains.

For each pair, expand every retained realization and every A/C interleaving
within each gap, then evaluate all seventeen quotient coefficients. Every
concrete word has a unique middle sequence, two outer sequences, gap assignments
and within-gap interleaving. The enumeration covers these without symmetry or
heuristic pruning. All prior screens impose necessary equations only.

| Split (a,b,c) | A / C profile passes | Key pairs | Profile pairs | Expanded words | Q survivors |
| --- | ---: | ---: | ---: | ---: | ---: |
| (4,5,4), retained control | 89,052 / 1,201,320 | 68 | 152 | 5,536 | 0 |
| (5,5,4), new | 236,224 / 1,201,320 | 144 | 944 | 211,968 | 0 |
| (4,5,5), new | 89,052 / 2,899,368 | 136 | 912 | 209,920 | 0 |

For the new domains, 125,636 / 117,308 words first fail AC and 86,332 / 92,612
first fail ACB. Full expansion digests are in RESULT.json. Quotient rejection
is sufficient to reject a formal identity; no construction is accepted from
this nonfaithful image. Independent subsequence expansion checks all 20,440
short words and the planted long-word fixtures. The five-call catalogue is
separately checked for complete, duplicate-free gap coverage.

Consequently every fourteen-call full formal word on any finite dirty workspace
has counts `(4,6,4)`. The credited coordinate word `abcbabcb` on the z role
and `acbabc` on the uz role attains these counts. The full group-algebra check,
192 faithful regular columns including a dirty spectator, fourteen one-call
omissions and a wrong-letter control are retained/replayed.

## Weighted implication for arbitrary word lengths

Every word has `n_a,n_c>=4` and `n_b>=5`. If `n_b=5` and `n_a+n_c<=9`, its
length is at most fourteen, and the preceding exclusions apply. Therefore
every five-b word has `n_a+n_c>=10`, with no bound on r or total length.

For arbitrary nonnegative real letter prices alpha,beta,gamma, every complete
word costs at least

```
min(4 alpha + 6 beta + 4 gamma,
    4 alpha + 5 beta + 4 gamma + 2 min(alpha,gamma)).
```

The first branch covers `n_b>=6`. For `n_b=5`, the outer calls beyond the
four-per-label floor number at least two and each costs at least
`min(alpha,gamma)`, giving the second branch. This is a necessary lower
envelope; it asserts no five-b construction attaining its second branch.

When `beta<=2 min(alpha,gamma)`, the direct `(4,6,4)` bill is the smaller
branch and is attained. Thus it is the exact optimum on that entire price
cone, including its boundary and zero prices. At `(alpha,beta,gamma)=(1,2,1)`
the exact price is twenty. Outside the cone, for example `(1,3,1)`, the lower
envelope is twenty-five and the direct price is twenty-six; sharpness is open.

No claim is made for all weighted prices, larger-slack workspace compression,
native/compiler realization, rational-frame transfer, physical hosting,
precision/reserves, or a multiplication exponent. The result is exact within
the stated formal alphabet, with substantial OpenAI Codex assistance and no
proof-kernel or independent human review.
