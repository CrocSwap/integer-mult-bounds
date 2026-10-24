# Exact copied-input correction: a losing full-rank test

The no-idle controller in [DISCOVERY.md](DISCOVERY.md) has X-block

```
X' = Q^-1 U x,
U = (I-S) D + S,
D = diag(d_0,...,d_(p-1)),
S_ij = (-1)^(j-i-1) for i<j, and zero otherwise.
```

Let J have ones immediately above its diagonal and zeros elsewhere. Since
J^p=0,

```
S = J(I+J)^-1,       I-S = (I+J)^-1.
```

The following copied-input correction is exact for every p and every input:

```
z = (I+J) X' - Q^-1 J x = Q^-1 D x.
```

Coordinatewise, `z_i = X'_i + X'_(i+1) - Q^-1 x_(i+1)` for i<p-1,
and `z_(p-1)=X'_(p-1)`. It needs the original input values; using the updated
outputs in their place is invalid.

## Rank is forced in this explicit correction model

Fix one port and consider only corrections of the form

```
z = M X' + Q^-1 N x,
```

where M,N are constant rational matrices, independent of the separate formal
variables d_j, and require the exact endpoint `z=Q^-1 D x` for arbitrary x.
Comparison of each independent coefficient d_j forces

```
M(I-S) = I.
```

Thus M is uniquely `(I-S)^-1=I+J`. The constant coefficient then forces

```
N = -MS = -J.
```

Consequently `rank(N)=p-1`. The statement also holds over F2 with signs
reduced, although it supplies no physical scalar-extension theorem.

If each fresh Q query accepts one scalar linear combination of the copied
inputs and returns its Q transform, while constant scalar maps prepare and
combine queries, q such queries produce a correction matrix of rank at most q.
Therefore q>=p-1 in this specified model. Querying each `x_(i+1)` achieves the
bound. This is a lower bound for fresh rank-one Q-query corrections with a
constant output map; it does not cover reuse of retained internal queries,
changes to the original word, more general operator-valued adapters or all
possible physical decoders. Multiplying the count by 112 or 111 below assumes
the correction is performed separately on each port. The lower bound does
not exclude a joint cross-port native operation or sharing between ports.

## Complete logical correction bill and p16 rejection

A literal forward implementation can copy the p-1 raw inputs to owned scratch
before running the controller, apply one Q^-1 job to each saved field, and
update the outputs in increasing i. Increasing order preserves each still-needed
`X'_(i+1)`. It then erases the scratch. Per port the added correction ledger is:

| Item | Count | Status and scope |
|---|---:|---|
| Extra recursive rank-one Q jobs | p-1 | Exact in the stated fresh-query model |
| Copies of raw fields into owned storage | p-1 | Explicit logical COPY; physical movement requires its native contract |
| Scalar additions/subtractions | 2(p-1) | Explicit above; coefficient sizes are one |
| Simultaneously retained owned fields | p-1 | No productive input credit |
| Final scratch erasures | p-1 | Explicit; owned-erasure premise retained |
| Physical routes, entry/exit matching, precision | Unknown | Not assigned zero |
| Y-block exactification | Unknown | Additional to this X-only bill |

With 112 complex ports and p=16, the X correction alone adds **1,680** paid
rank-one jobs to a formal rank-one surplus of **752**, producing surplus
**-928** before any Y correction or other new charge. This is already
unfavorable at exponent one. The cumulative certificate below strengthens
this to every concave moment in this specific correction model.

More generally, the complex X-corrected rank-one surplus in this model is

```
48(p+2)-112 -112(p-1) = 96-64p,
```

which is negative for every p>=2. The BIT analogue is `96-63p`, also negative
for p>=2. A claimed complete construction using this fresh-query correction
must therefore address the failed rank-one criterion rather than inherit the
uncorrected border's surplus. This test prices actual eliminated idle work and
an actual replacement, and rejects that replacement in the stated source
compiler's positive-surplus admission route.

## All concave moments fail in this correction model

Let T_r be the actual formal border targets and let P_r include the p-1 fresh
X-correction queries per port. Define

```
A_r(p) = sum(k<=r) k(P_k-T_k).
```

All counts are affine in p for p>=2. The following exact values give
`A_r(p)=base+slope*(p-2)` at every support threshold:

| Complex rank r | Base at p=2 | Slope |
|---|---:|---:|
| 1 | 9172 | 2461 |
| 2 | 12276 | 3237 |
| 3 | 18204 | 4719 |
| 4 | 20108 | 5195 |
| 5 | 20828 | 5375 |
| 7 | 20632 | 5326 |
| 8 | 19384 | 5014 |
| 9 | 7648 | 64 |
| 17 | 32 | 64 |

| BIT rank r | Base at p=2 | Slope |
|---|---:|---:|
| 1 | 5514 | 1545 |
| 2 | 16250 | 4229 |
| 3 | 17198 | 4466 |
| 4 | 17902 | 4642 |
| 5 | 19942 | 5152 |
| 6 | 20206 | 5218 |
| 7 | 20738 | 5351 |
| 8 | 6690 | 63 |
| 15 | 30 | 63 |

Every base and slope is positive. For 0<t<=1 the function f(r)=r^(t-1) is
positive and nonincreasing. Discrete summation by parts, with R the maximum
rank, gives

```
P_t-T_t = A_R(p) f(R)
          + sum(r=1..R-1) A_r(p) [f(r)-f(r+1)] > 0.
```

Missing thresholds have the same cumulative value as the preceding listed
one. Thus this exact fresh-query X correction alone destroys every favorable
concave moment, on both suppliers, for every p>=2. Additional Y corrections
and physical charges cannot repair that inequality unless the construction or
the target interface also changes. This conclusion remains restricted to the
specified fresh-query correction model.

`border_algebra.py` checks the geometric-series identities and exact ranks
for p=1,...,8, rejects deletion of a required query, and reconstructs every
base and slope in the all-moment certificate from the pinned source profiles. These finite checks
support the stated symbolic proof; they are not a general native-query lower
bound or an independently reviewed multiplication theorem.

## Open next questions

Do the p-1 already-paid thin queries expose the required raw `Q^-1 x_(i+1)`
values at a usable chronological cut, with legal retention and restoration?
The current source interfaces do not grant those values. An explicit reused
query/consumer contract would change the lower-bound hypothesis and is the
smallest concrete route to reopening this exact correction strategy.
