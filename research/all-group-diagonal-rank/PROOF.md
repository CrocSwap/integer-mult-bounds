# Diagonal group targets have exact scalar-rank cost

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written algebraic proof with exact finite corroboration.

## Model and statement

Let K be any field and G any group, finite or infinite, with identity e.
Work coefficientwise in the full formal group algebra K[G]. Every matrix
has finite support. A free operation is a fixed scalar K-linear map, with
address action [e]. Free maps may be rectangular or singular and may copy,
reset or discard scalar registers. The schedule is finite and fixed.

A paid gate on r registers is

```text
D(N,g) = I_r[e] + N([g]-[e]),  N in M_r(K), N^2=N.
```

Its scalar-rank charge is rank_K N. Rank-one call count is the same charge
when every paid projector has rank one. Initial scalar embeddings of data
and clean helpers, and final selections of retained outputs, are free maps.
Arbitrary dirty inputs may also be supplied. Retained data outputs must be
correct for every such input. Restoration of additional outputs is optional
for the lower bound; the attaining construction restores them.

**Theorem.** Suppose the retained independent data outputs implement
diag([t_1],...,[t_m]) on their m independent data inputs. Let
d = |{i : t_i != e}|, counting repetitions by position. Then every such
circuit has total paid scalar rank at least d. If every nonidentity target
label t_i is in the paid alphabet, its exact minimum scalar-rank charge
and exact minimum rank-one call count are both d.

The lower bound holds for an arbitrary paid alphabet and does not use
idempotence. The equality statement requires the target-label availability
just specified. It is not a word-length theorem for a restricted generating
alphabet.

This answers the four-or-more-target question in Ali Romman's
[#5394](https://github.com/CrocSwap/integer-mult-bounds/pull/5394) for every
group and field in its formal model. That package's arbitrary-rank,
unit-price invocation optimum remains its ordered-subproduct cover number.
Consequently rank-one count exceeds that invocation optimum exactly when
the cover number is less than d. We cite the cover theorem; we do not
re-prove or replay it.

## One common scalar image space

For a rectangular formal matrix M = sum_g M_g[g], define

```text
U(M) = sum_{g != e} col_K(M_g),
c(M) = dim_K U(M).
```

All coefficient images are subspaces of the same scalar output space.
This is a sum of subspaces, rather than a sum of the individual ranks.
Its dimension counts repeated output directions correctly even when many
targets have the same group label.

Write epsilon(M) = sum_g M_g for augmentation. The coefficient images of
M-epsilon(M)[e] span exactly U(M): its nonidentity coefficients are M_g,
and its identity coefficient is -sum_{g != e} M_g.

**Lemma.** For compatible rectangular formal matrices A and B,

```text
U(AB) is contained in U(A) + epsilon(A) U(B),
c(AB) <= c(A) + c(B).
```

**Proof.** Augmentation is multiplicative, since summing every ordered
coefficient product gives epsilon(A) epsilon(B). Thus

```text
AB-epsilon(A)epsilon(B)[e]
  = (A-epsilon(A)[e]) B
    + epsilon(A)[e] (B-epsilon(B)[e]).
```

Every coefficient of the first summand is a sum of scalar matrix products
A'_g B_h, with col(A'_g) contained in U(A). Its columns therefore lie in
U(A). Every coefficient of the second summand has columns in
epsilon(A) U(B). Taking the sum of coefficient images proves containment.
The image of a linear map cannot increase dimension, proving the rank
inequality. No commutation of group labels, inverse of a free map or
restriction on the group order was used. QED.

A free scalar map has c=0. For g != e, the gate coefficients at e and g
are I-N and N. After subtracting augmentation I, they are -N and N, so
c(D(N,g))=rank N. For g=e the gate is identity and has c=0, which is at
most its declared rank charge. Iterating the lemma through the entire
rectangular circuit gives c(M) <= sum_j rank N_j.

Equivalently, in matrix order write the retained data block as
C_0 D_1 C_1 ... D_k C_k. Expand by the leftmost paid perturbation.
The scalar image of each resulting term lies in
col(C_0 C_1 ... C_(j-1) N_j). The sum of these k scalar spaces has dimension
at most sum_j rank N_j and contains every nonidentity output coefficient.
This equivalent expansion explains the transported-image test in verify.py.

## Apply the bound and attain it

Select the retained data-output rows and the independent data-input columns
of the circuit. The endpoint maps in that selection are scalar, so the
same bound applies to the resulting m-by-m matrix T. This argument allows
arbitrary dirty workspace and arbitrary discarded garbage without assigning
them zero cost or assuming their input values vanish.

For each g != e, the coefficient T_g is diagonal, with a one in position i
exactly when t_i=g. Its column space is the span of the corresponding
coordinate axes. Summing over g != e gives precisely the d active axes.
Thus c(T)=d, proving the lower bound.

For the upper bound, apply one gate D(E_ii,t_i) to each active position i.
The projectors have rank one and commute because they act on separate
scalar registers. Their product is the required diagonal target. They
touch no helper and restore all dirty spectators. There are exactly d
gates and d total rank units. This also covers d=0 by the empty word. QED.

## Scope and predecessor credit

Ali Romman's #5394 supplies the model, cover theorem, three-label result
and open question. The scalar coefficient-image method has precedent in
Arham Tahir's #1919 and in the image-span reduction retained in
research/bit-clean-workspace-compression. We claim the arbitrary-group
application, the rectangular common-image proof and the complete answer
to #5394's rank-one question, not invention of coefficient-span methods.

Nick Petalas's older #6008 gives a representation-rank cut and proves the
same d value for prime-exponent groups, with a coprime cyclic-character
remark. Krzysztof Wojt's #5242 gives the mixed-target binary semilinear
case. Those restricted consequences are prior work. No predecessor
scientific verifier is run here. SOURCES.json pins the retained sources
used for the argument and context.

Formal coefficientwise equality is essential. A representation faithful on
group elements can still kill nonzero linear combinations. Free
address-dependent maps and data-dependent control are outside this model.
The theorem prices scalar projector rank, not physical address action,
native realization, frame conversion, precision, tape movement, hosting,
restoration overhead or a complete supplier invoice. No new kappa or
selected-frontier change follows. Independent human and formal proof-kernel
review are unclaimed.
