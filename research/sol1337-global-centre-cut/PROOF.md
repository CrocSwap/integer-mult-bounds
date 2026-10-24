# Exact conditional-leaf cut

Fix a nonzero ambient axis a, and let x_v choose between L_v and T_a L_v.
Every internal map is identity. Simultaneously transforming both charts preserves
their distance, so an internal edge of old rank r has ranks

```
r00=r11=r,  r10=r01=r+d,  d in {-1,0,1}.
```

The r10=r01 equality also follows by applying the symplectic involution T_a to
both sides. The imported local rank-change formula computes d; each of the 419
retained complete rank configurations is independently checked by binary row
elimination, including both one-endpoint ranks and the two-endpoint invariant.
External mapped neighbours are pulled back to the variable's chart coordinates;
their actual changed ranks are also checked by row elimination.

For any tariff h with h(0)=0, the changed invoice is

```
E(x) = sum_v D_v x_v + sum_internal uv w_uv |x_u-x_v|,
w_uv = h(r+d)-h(r).
```

D_v is the sum of every incident external changed-edge charge. Fixed-fixed
edges cancel. Exact graph checks find 256 internal rank-zero edges among 176
empty-chart contacts and eight rank-eight edges. Each rank-eight edge joins
one empty-chart contact u to a distinct nonempty-chart contact v, and each such
v has internal degree 1. There are no other nonempty-chart contacts.

For h_j(r)=min(r,j), rank-zero edge weights are 0 or1. A rank-eight weight may
be negative; no direct submodularity assumption is made. Eliminate its leaf v
conditionally on x_u. Its exact contribution is

```
A=min(0,D_v+w)                  if x_u=0,
B=min(w,D_v)                    if x_u=1.
```

Thus add A to the offset and B-A to D_u. This removes every potentially
negative internal edge, preserving the exact optimum. It is equivalent to
flipping a singleton bit on each antiferromagnetic edge; leaf topology prevents
any frustrated signed cycle. The remaining 176-variable energy has nonnegative
pair weights and arbitrary integer unaries, and therefore is an ordinary s-t
cut. For each cut, the implementation lifts the original leaf choices and
recounts the complete 184-variable rank histogram; its integer tariff agrees
exactly with the computed optimum. Feasible conserved flow and an equal-capacity
attaining cut prove optimality without a numerical solver tolerance.

Every nonzero18-bit axis is enumerated literally. A configuration signature
retains the changed rank of every external incident edge and the one-endpoint
rank of every internal edge. These data fully determine E, since internal00
and11 ranks remain old and 01 equals 10. Equal signatures therefore permit exact
reuse of all tariff optima; they do not equate charts. The complete 262143-axis
domain yields 419 such configurations. All 419*9 integer prefix minima are 0.
The unchanged choice directly attains 0.

For any candidate rank change d_r, let q_j=j^theta-(j-1)^theta. Finite summation
by parts gives

```
sum_r d_r r^theta
 = sum_(j=1)^8 S_j(d) (q_j-q_(j+1)) + S_9(d) q_9.
```

For 0<theta<1, every displayed coefficient is nonnegative. Every S_j is
nonnegative by the exact cut certificates. Hence the complete changed paid
moment is nonnegative throughout 0<theta<1. Strict loss and uniqueness of the
unchanged chart assignment are not claimed.

This is a scoped finite paid-invoice result. It is not a theorem about every
Clifford assignment, independent axes, changed operations, physical realization,
owned centre supply or outer multiplication.
