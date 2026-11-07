# The exact defect in merging same-image hub idle jobs

Prepared for @CubeJerry with substantial OpenAI ChatGPT/Codex assistance.
Apache-2.0. This complementary audit concerns the parent package's proposed
four-arm extension of DreamingOfClouds's CrocSwap/integer-mult-bounds#6833.
The common-idle/native lineage retains thu-nmrc, Cinna Davis, zxv, Ali Romman
and the parent package's predecessor credits. **No new κ.**

The counterexample below rules out the naive isolated fusion; the transport
argument is scoped to the specified pure-hub projectors. It does not establish
a global impossibility of changed supports or new native mechanisms.

## Exact candidate

Let `A=e0`, `B=e1`. The chronological full-query arms are `L0,R0,L1,R1`.
Their hub data are

```text
u = (A, B, B, -A)
v = (A*-B*, A*-B*, A*+B*, A*+B*)
sigma = (1,-1,1,-1), with v(u)=sigma.
```

An L arm has `x_i=u+f_i+2 sum_(j<i) f_j`, `y_i=v-f_i*`.
An R arm has `x_i=u+h_i+2 sum_(j>i) h_j`, `y_i=v+h_i*`.
The candidate stage support contains both hubs and its own chain prefix/suffix.
Its extra hub idle projector is `E=I_hub-u v/sigma`.

At lengths `(4,4,5,5)`, the companion standard-library checker verifies all
324 full-query sign-Gram entries and constructs all eighteen actual active
planes by subtracting the chain and hub idle projectors from those supports.
Each is an idempotent of rank two containing its query. The hub image AND dual
annihilate that plane and its query. These exact finite checks corroborate the
following formulas, which hold for any positive arm lengths.

The two proposed hub merges are

```text
E0 = (A+B) B*        E1 = (A+B) A*
E2 = (A-B) A*        E3 = (A-B) (-B*).
```

Each pair shares its image but has distinct duals. Every ordinary chain idle
in either member of a pair commutes with both of that pair's hub projectors.

## 1. No transport through the unmodified pair of arms

Let `E` be the left hub projector and `F` the right one. Every normalized native
kernel of the left arm commutes with `E`; every kernel of the right arm commutes
with `F`. In fact the active part fixes each corresponding hub on both sides.
The same statements hold for a partial suffix or prefix of either arm, and the
chain idles preserve them.

Write a transport interval as `H=H_R H_L`, where `H_L` is a completed left suffix
and `H_R` a completed right prefix. Both are invertible. If it transported the
left projector to the right one, then

```text
F = H E H^-1 = H_R E H_R^-1.
```

Conjugating back by `H_R`, which commutes with `F`, gives `E=F`, a contradiction.
Thus the existing arm transport cannot justify replacing the two distinct-dual
hub jobs by one common-carrier job. This excludes this specific sliding proof,
not arbitrary changes to the root or its active supports.

## 2. Normalized thin bridges alone do not repair the uniform obstruction

Every proposed normalized thin query has the form `T(S)=I+(S-1)R`. In the
`S=+1` sector it is identity, independent of where it is placed or how many
such thins are used. That sector is a valid part of the all-column complex
contract (`Q=1` or `Q=i`). The fresh stage Gaussians can still vary independently
there.

The preceding no-transport contradiction therefore survives every bridge made
only of these normalized thins, as long as the fixed pure-hub projectors and
their native active planes are retained. A truly ordinary bridge, S-dependent
carrier projectors, a changed support family, or an additional operation can
change this conclusion. Each is a new construction requiring its own complete
endpoint proof. This statement does not assume that a failure in the `S=-1`
sector alone rules out a construction; one valid sector already disproves the
required uniform conjugacy of the fixed projectors.

## 3. The exact discarded operator in a naive same-image fusion

Let `E=phi gamma`, `F=phi delta`, with `gamma(phi)=delta(phi)=1` and `E!=F`.
Put `H=F-E`. Then

```text
EF=F, FE=E, H^2=0, HE=0, EH=H.
```

For an address operator `U`, write `J_E(U)=I+(U-I)E`, and let `U,V` be commuting
Gaussian products on disjoint fresh stage sets. Direct multiplication gives

```text
J_F(V) J_E(U)
  = (I-F) + V(F-E) + UV E
  = [I+(V-I)H] J_E(UV).                    (1)
```

Thus replacing the two jobs by the single merged job discards a genuine
`(V-I)` shear on the difference between the two duals. It is zero only when
`E=F` or on a specially restricted input/operator sector. Neither restriction
is allowed by the candidate's arbitrary-input interface.

There is an explicit valid character counterexample: set `U=1,V=-1`.
The true map is `I-2F`, while the proposed merged map is `I-2E`; their
difference is `-2H`, nonzero for both candidate pairs. Disjoint positive
Gaussian blocks of eight or more fresh axes realize these phases independently.
This disproves naive fusion on arbitrary inputs; it is not a failed search.

For the isolated two-job subcircuit, one call to the specific merged operator
`UV`, surrounded by scalar field-space linear maps independent of `U,V`, has
only the operator monomials `1` and `UV`. The actual product in (1) has nonzero
coefficient `H` on the monomial `V`. Hence such a replacement is impossible.
This is exact in the group algebra of two independent order-four variables:
`1,V,UV` are distinct characters, and the two disjoint fresh axis sets realize
all four phases independently. Fixed central-Q scalar coefficients can be
included by fixing a Q character.

This monomial obstruction is deliberately scoped to these field-space
wrappers and this isolated two-job replacement. It is not a circuit lower
bound allowing arbitrary new native channels, general address-dependent
couplings, or reuse of other stage transforms already executed in the caller.

## 4. A complete elementary repair pays more than the original jobs

The residual in (1) can be implemented using the retained copied-query
procedure. The functional `delta-gamma` annihilates `phi`. Form its current
value in an explicitly initialized, uncredited owned field; apply `V`; subtract
the unchanged source functional; add the result along `phi`; erase the owned
field under the retained owned-erasure contract. All scalar copies, additions,
restoration and erasure are ordinary paid work. This uses one additional
rank-`rank(V)` Gaussian and no productive output credit.

The source functional remains available after the merged job because
`(delta-gamma)E=0`. It is also unchanged when a multiple of `phi` is added.
Thus the copied-query procedure computes exactly the residual on the actual
current fields without crediting a copied or correlated input as productive.

The explicitly proved repair for the stated ordered product has paid moment

```text
(rank(U)+rank(V))^t + rank(V)^t,
```

which is strictly larger than

```text
rank(U)^t + rank(V)^t
```

for every `t>0`, because the merged rank exceeds rank(U). The repair therefore
cannot improve the candidate's original unmerged hub invoice. This is a rigorous cost comparison for the specified
repair, not a lower bound on every conceivable way to supply the residual.
At the candidate lengths the original hub pairs have ranks `(32,32)` and
`(40,40)`; the optimistic single-job replacements had ranks 64 and 80.

## Verification and limitations

Run from the repository root:

```sh
python3 -B research/p104-coupling-root-obstructions/hub-carrier/verify.py
```

Expected marker: `PASS_HUB_CARRIER_DEFECT`. The standard-library checker
independently constructs all 18 active planes, checks 324 full-query pairings,
checks the two exact nonzero-V residual coefficient tables, and runs five
failure controls. These reject naive fusion on the valid character U=1,V=-1,
a residual missing its minus-I term, reversed residual order, different-image
projectors, and a non-idempotent purported carrier. Equal duals give a positive
fusion control. The whole proof is algebraic; finite cases corroborate its
binding to the exact candidate. No assertion can be disabled by Python -O.

For the SAME ordered product, choosing the other merged carrier is a different
factorization involving a U^-1 pre-shear. No claim that simply reversing the
two jobs preserves their operator is made here. The explicit V repair already
proves the stated unfavorable complete bill without any additional inverse
implementation premise.

An ordinary hub swap really aligns each candidate pair, but it changes the
caller and requires a fresh full endpoint proof. The parent shortest-root
obstruction handles actual ordinary transport in a common gauge. No static
projector equality is inferred merely from existence of an abstract conjugator.

This finite carrier audit does not prove the native all-column realization,
owned erasure, uniform compiler, physical precision/tape rates or analytic
recovery. Its copy/erase repair retains those source contracts, prices its
extra Gaussian and ordinary operations, and earns no extra productive field.
