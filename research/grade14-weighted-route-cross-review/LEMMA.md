# Complete-cover weighted matching lemma

This source-neutral correctness lemma isolates the implication reviewed in
[PROOF.md](PROOF.md). A different caller must establish the hypotheses below.
The route-invariant weight refinement weakens a sufficient algebraic
condition; it does not change #7837's ancestor-only source theorem or supply
a new descriptor, tariff or full runtime.

## Contract

Fix N>=1, an odd prime q, w>=1 and R=Z/q^w. Let G=GL_N(R), with standard
entrywise representatives of GL_N(F_q). Let each S_i be a fixed rational
invertible N-by-N matrix with q-integral entries and q-integral inverse.
The finite matcher list does not depend on w or payloads.

Each productive role has a distinct supplied owner carrying an arbitrary
binary payload function `x_i(a,g,z)`. The coordinate a contains exposed
ancestors, g ranges over the **complete** fresh G cover, and z contains the
complete body and all spectators. Equal or correlated payloads are allowed.
Private owners, suspension and retirement have their separate supplied
ownership contract.

Let the common head weight be a unit array `A(a,g,j)` at atom index j. Assume
the exact route-invariance condition

```
A(a,g S_i,j) = A(a,g,j)        for every current matcher i and all a,g,j.  (RI)
```

The array is common to all current roles and does not read their head/tail
address values. Ancestor-only weights `A(a,j)` satisfy (RI) automatically.
More general fresh dependence is permitted for this **algebraic** lemma only
when (RI) is established for the complete matcher inventory.

Let Q_i,P_i be fixed rational split projectors, admissible at q, with

```
S_i Q_i S_i^-1 = P_i.
```

At positive multiplicity f, put `P_f=P tensor I_f`, `C=C_N tensor C_f`, and

```
D_f(P) = [[I-P_f, P_f C], [C P_f, I-C P_f C]],
W_A = diag(A,I).
```

These matrices act on addresses over R. Their induced operators permute
binary payloads; payload addition is XOR, not address addition in R.

## Conclusions

**Complete route and inverse.** Write `g=g_0+qX` and set
`h_0=(g_0 S mod q)` in the fixed representatives. Then right multiplication
is exactly

```
rho_S(g_0,X) = (h_0, XS+C_S(g_0) mod q^(w-1)),
C_S(g_0) = (g_0 S-h_0)/q.
```

It is a bijection of the full low/high header set. For every S,T,

```
C_(ST)(g_0) = C_S(g_0) T + C_T(h_0),
rho_T after rho_S = rho_(ST),
rho_(S^-1) = rho_S^-1.
```

At w=1 the high domain is a singleton, requiring no zero-width operation.
The routes fix every ancestor and body/spectator coordinate.

**Independent endpoint matching.** Route role i from g to `h=gS_i`.
Suppose the completed ideal child acts independently on that role by the
payload permutation of

```
W_(A(a,h,.)) D_f(h Q_i h^-1) W_(A(a,h,.))^-1.
```

Full inverse return gives exactly

```
W_(A(a,g,.)) D_f(g P_i g^-1) W_(A(a,g,.))^-1
```

on the original parent row. This holds for every positive f, every ancestor
and spectator assignment, and arbitrary independent or correlated payloads.
Internal role mixing is allowed because the completed independent endpoint
cancels all unwanted dependencies before return.

**Exact row-local endpoint criterion.** A nonzero off-diagonal completed
block from role i to role j reads, on return to role j's parent row g, its
donor from

```
g S_j S_i^-1.
```

For a same-parent-row target and arbitrary independent payloads, this forces
`S_i=S_j` as constant right actions over R on the coupled roles. Otherwise
the intended target must explicitly include that displaced donor row.
Here equality means equality of their reductions in GL_N(R); a statement
for every w forces equality of the fixed q-integral rational matrices.
Indeed, distinct donor rows carry independent functions, so a nonzero block
cannot turn one into the other for all payloads. A sparse payload witness
separates them. Independent productive endpoints have no off-diagonal
restriction.

**Common-weight commutation.** Condition (RI) is precisely the commutation
condition between the common head scaling W_A and each fresh right route.
It also gives invariance under the inverse route. Pointwise XORs commute
with applying the same W_A to every role at one header. Thus weighted
conjugation can be applied to the completed finite program, without creating
private role-dependent weights inside a shared invocation.

## Proof

Multiply `(g_0+qX)S` and extract the fixed low representative. The numerator
of C_S is divisible by q in the localization at q. The cocycle follows from

```
g_0 ST-k_0=(g_0 S-h_0)T+(h_0 T-k_0).
```

Taking T=S^-1 returns the low representative to g_0 and makes the total
carry zero, proving inverse return on every high lift. Right multiplication
preserves invertibility and the decomposition is unique.

At a parent row g, the routed child header is h=gS_i, and

```
(gS_i) Q_i (gS_i)^-1 = g P_i g^-1.
```

Condition (RI) makes the head weights at g and h identical. These facts
prove the independent endpoint. For output j at h=gS_j, donor ingress
inverse gives `h S_i^-1=g S_j S_i^-1`, proving the coupled criterion.
All equalities remain valid with P tensor I_f and the complete reversal
C_N tensor C_f.

More explicitly, in pushforward convention a right route satisfies
`(R_i x)(a,h,z)=x(a,hS_i^-1,z)`. W_A acts only on z with coefficient
A at its current header. Equality of `R_i W_A` and `W_A R_i` for all
payloads is therefore exactly equality of the diagonal unit arrays at
`hS_i^-1` and h. This is (RI). The unit array is determined by its address
scaling, so the condition is necessary as well as sufficient for this
commutation. The common array also commutes with pointwise role XORs.

## Nonconstant invariant weights and their boundary

The two independent test matchers have determinant one. The positive control
uses

```
A_0(a,g,j)=u_0(a,j) det(g),
A_1(a,g,j)=u_1(a,j) det(g)^2.
```

These are nonconstant functions of the fresh cover and satisfy (RI). The
verifier checks their nonconstancy and another 109,536 weighted column
cancellations and parent endpoints. A separate non-invariant fresh function
fails: fresh dependence itself is not the obstruction.

Each actual grade-14 port swaps seven body directions, so its determinant
is `(-1)^7=-1`. All 222 exact factorizations confirm this determinant.
Consequently functions of `det(g)^2` are invariant under those port routes.
They need not be invariant under later compiler matchers. Over Z/9,
`g=I` and `S=diag(2,1)` change `det(g)^2` from 1 to 4. The complete current
matcher list must be considered; invariance on ports alone is insufficient.

These observations are algebraic. They do not assert a new evaluation cost,
descriptor grammar, fresh-coordinate runtime contract, or improved supplier.
#7837's stronger ancestor-only theorem is left unchanged.

## Complete cylinders and source-specific reuse

The retained batch map writes, with H the high-matrix cardinality and L the
fixed productive/low-type count,

```
b=U H^j+A_old,
U=U'(LH)+lH+h,
b_child=(U'H+h)H^j+A_old.
```

Inverse divisions recover all fields. Current routing permutes the complete
current `(l,h)` cover and fixes old ancestors, unused U', and body fields.
Every old-ancestor assignment retains a complete next fresh cylinder. The
child volume divisor is L, while the row stock factor is LH. In the source's
ancestor-only discipline a parent's current header becomes an exposed
ancestor for the child; its next cover comes from disjoint unused stock.
No independence of payload data or invocation histories is assumed.

A reuse corollary must bind the actual formal target support, every coupled
pair's compatible routes, complete image/kernel bases, admissible prime,
ownership/fresh-cylinder entry contract, and the charged full right routes
and ordinary backend. This lemma supplies a correctness implication, not an
allocator, free high-field permutation, literal dispatcher or multiplier
bound. The route-invariant generalization does not automatically inherit
the source's descriptor or time/storage proofs.

Finite ideal-job substitution and physical recursion are separate: first
prove the compiled word's denotation with ideal D_f jobs; then implement
them by a well-founded width induction using an already completed ordinary
backend. The lemma does not authorize assuming the parent runtime endpoint.
A selected #7000 corollary needs its own exact source binding.

Credit Ali Romman's #7837 and the retained complete-cover and recursive-closure
sources. This refinement and independent cross-review were prepared for
Jerry Chen with substantial OpenAI assistance. No human or proof-kernel
acceptance is claimed. Apache-2.0.
