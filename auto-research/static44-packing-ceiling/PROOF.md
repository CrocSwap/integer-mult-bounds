# Exact dual exclusion

Let m=73, W=7168 and delta=2560. The unchanged local paid profile is multiplied
by 72 calls; write the resulting multiplicities as H. Let N_r be the number of
original idle children of rank r, as derived from the pinned owner-plan windows.
Every call requires 56 width-five, 156 width-eight and 292 width-nine helpers.
Thus the total demand is D_w=72 times this inventory.

A relaxed pattern for a rank-r idle child is any nonnegative integer tuple
(n5,n8,n9) satisfying 5n5+8n8+9n9<=r. Its remainder is
u=r-5n5-8n8-9n9. Permit a nonnegative real number x_r,n of copies of each
pattern, subject only to

```
sum_n x_r,n = N_r,
sum_r,n n_w x_r,n = D_w.
```

Every actual whole-helper assignment induces such counts. Chronology, ownership,
per-call exclusion, charts and integrality impose extra restrictions, so deleting
them can only lower the optimal cost. The rank-mass identity is checked exactly:

```
sum_j j H_j + sum_r r N_r - sum_w w D_w = m W - delta.
```

For the proposed endpoint b=0.001593251957517, define phi_b(0)=0 and, for r>0,

```
phi_b(r) = [r((m/r)^b-1) + 32 m^2 m^b / 10^16] / b.
```

The second term is the unchanged per-child bad-class fallback used by PR544.
For any resulting profile P, the exact normalized moment satisfies

```
m W (Moment(P,b)-1)
 = b [sum_j H_j phi_b(j) + sum_r,n x_r,n phi_b(u) - delta/b].
```

The verifier recomputes rational lower and upper enclosures for phi with two
independent engines. It does not use a floating logarithm or the discovery LP.
The zero remainder is explicitly cost-free and has no child fallback charge.

Let theta_r and mu_w be the seven frozen rational dual weights. For every
regenerated pattern, each engine independently proves

```
theta_r + sum_w mu_w n_w <= lower_phi_b(u).
```

Multiply by x_r,n>=0 and sum, then apply the stock and demand equalities. This
gives the lower bound

```
sum_j H_j lower_phi_b(j) + sum_r N_r theta_r + sum_w D_w mu_w - delta/b.
```

Both engines certify that this number is strictly positive. Consequently every
packing in the relaxation has Moment(P,b)>1. Each actual packing does as well.
The moment is strictly increasing with b because every nonzero child rank is
smaller than m and the fallback term is increasing. Therefore no admissible
rate for this fixed class reaches the excluded endpoint.

Allowing a single merged remainder is optimistic even for implementations that
split it: for 0<b<1, `(u+v)^(1-b) <= u^(1-b)+v^(1-b)`, and merging removes a
positive per-child fallback charge. The argument does not cover additional
banks or modifications that change the rank-mass identity, local profile,
helper inventory, stage chain or bad-envelope contract.

Finally the retained balanced family has q<a<b and
kappa<epsilon*q with epsilon=(1-eta)/(1+q), eta>0. Hence

```
kappa < q/(1+q) < b/(1+b)
      < b_excluded/(1+b_excluded).
```

This is a supremum bound, not a newly achieved kappa. Subtracting the pinned
PR547 `079c86c` value gives a strict headroom below 6.344e-9, or below 0.000399% relative.
The all-size and analytic assumptions behind the finite suppliers remain
conditional. The distinct 1/33 and Gaussian 1/4 assembly-domain restrictions
are already documented in the repository's assembly-domain audit; they are not
new results of this package.
