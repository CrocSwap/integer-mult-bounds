# Exact search argument and certificate scope

## Reversible expanded alphabet

Let `G = GL3(F2)` and let `g` be one of the six coordinate transvections, so `g^2=e`. Work in the full group algebra `F2[G]`. Put `a=[g]+[e]`. Then

```text
a^2 = [g^2] + [g] + [g] + [e] = [e]+[e] = 0.
```

For every matrix `N` (in particular every rank-one idempotent or nilpotent),

```text
(I+aN)^2 = I + a(N+N) + a^2 N^2 = I.
```

Thus all nine nonzero rank-one matrices in `M2(F2)` give legal reversible factors for these labels. The six idempotents are exactly those `N=uv^T` with `v^T u=1`; the three other rank-one matrices have `v^T u=0` and are nilpotent.

## Complete coefficient-state recurrence

Represent a transfer matrix `P` by its four entries `P_ri in F2[G]`. For an entry, write its coefficient support as a subset `S_ri` of the 168 group elements. Addition is symmetric difference. On appending `D_N(g)` on the right,

```text
P' = P(I+([g]+[e])N)
   = P + (P[g]+P)N.
```

For output column `j`, form `V_rj = symmetric_difference_i S_ri` over exactly those `i` with `N_ij=1`. Its added support is `(V_rj g) symmetric_difference V_rj`, where every `h` in `V_rj` maps to `hg`. The new entry support is the old support symmetric-differenced with that set. The search implementation packs each support into a 168-bit integer; the independent verifier stores explicit sets of 3-by-3 binary matrices and recomputes the group products.

The address group is constructed by closure from the identity under right multiplication by the six transvections. The resulting Cayley distances give 31 endpoints at distance at most two. Their 961 ordered pairs have direct-cost histogram `1,12,84,288,576` for costs zero through four.

## Exhaustion and minimum claim

There are nine rank-one couplings and six labels, hence 54 factors. Breadth-first expansion from the identity transfer yields the exact distinct-state counts

```text
depth 0:      1
depth 1:     54
depth 2:   2,295
depth 3:  89,358
```

The implementation evaluates 126,900 distinct-state transitions. The raw word count through length three is `1+54+54^2+54^3 = 160,435`. Equal full coefficient states can be deduplicated: any suffix applied to equal states produces equal states, and breadth-first order retains a shortest representative. For every endpoint pair with direct bill `d<=4`, any strict improvement has length at most `d-1<=3`. The exhaustive radius-three state set therefore covers every possible improvement in the declared endpoint domain. It contains no such target below its direct bill.

For the upper bound, each CNOT letter in a shortest word for `p` is applied with register projector `E11`, and each letter in a shortest word for `q` with `E22`. These factors act on the two roles independently and produce `diag([p],[q])`. The independent verifier checks this construction for all 961 pairs. Consequently the exact minimum in the stated finite model is `d(p)+d(q)` for every pair in this domain.

## Independent controls and limits

The set-coefficient verifier independently rebuilds `GL3(F2)`, the 54 factor types and every state through depth three. It checks all 36,288 applications of the 54 factors to the 672 single-coefficient basis transfers; each factor squares to the identity on every basis element. Its direct-word positive controls cover all 961 targets. A noncommuting-label control rejects reversed chronology, and a changed-coupling control rejects an altered register map.

This is an exact finite enumeration, not a proof-assistant theorem and not a universal no-sharing result. The conclusion ends at two roles, six GL3 coordinate-CNOT labels, all nine rank-one 2-by-2 F2 couplings, and target radius two per role. It assumes the new nilpotent coupling has the same one-call price as an idempotent coupling. Native implementation, supplier translation, and any effect on the selected multiplication bound remain open.
