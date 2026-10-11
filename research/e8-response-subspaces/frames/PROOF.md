# Explicit response kernels and two-sided entrance charts

The finite change starts from the frozen signed-prefix candidate with SHA256
`a4e42aa1663f5ad0da48cee6fe8514b205e43cf6e791b80674dbc7506a098a32`.
It synthesizes 26 F2 subspaces not registered in that candidate, with ranks 1, 2,
4 and 5. Their exact bases and rational circuits are in `selection.json`.
The resulting candidate has SHA256
`3b78069c4ce032e95f757a2f79fa5557af923c947430b638b0eb6859be659866`.
This is a concrete extension of the inherited response-kernel construction;
no claim of global novelty or optimality follows from the bounded search.

## 1. A sufficient response-kernel identity

Let M be the complete rational raw main operator, including its retained-centre
snapshot, over immutable sources X, arbitrary initial targets Y, and helpers H.
Let K be its final Y-by-H response block. For a pivot helper p choose donor
helpers d and explicit rationals c_pd satisfying

    K_p + sum_d c_pd K_d = 0.

Apply the literal entrance shears `h_d += c_pd*h_p`. Let S be their helper-space
matrix. All pivots are distinct, no pivot is a donor, and the complete helper
role sets of the 26 selected groups are disjoint. Within one group, sharing a
donor is allowed. Thus S=I+N with N^2=0, the elementary factors commute, and
S^-1=I-N is an explicit finite inverse. No inverse oracle is assumed.

The new full raw operator is

    M' = M * diag(I_X, I_Y, S).

Therefore its clean-source and initial-target columns equal the old ones. Its
pivot response column is exactly the displayed zero combination. This proves
zero response for arbitrary initial helper values, not merely clean inputs.
The portable reconstruction independently checks this identity in all 1021
initial columns, exports the changed K, and rejects omission of an entrance gate.

There are 119 pivots and 143 donors. The pivots have total entrance dimension265:
15 rank5 entrances,26 rank4,8 rank2 and70 rank1. Unit-numerator expansion gives
240 literal entrance additions using denominators1 or2. Every entrance subspace
is contained in the first required frame of each of its pivots and donors;
the complete new register paths, including endpoint climbs, are checked nested.
The actual local paid histogram changes by

    {1:+169, 2:+91, 3:-43, 4:+15, 5:+10, 6:-96, 7:-3}.

Its rank-mass change is -265. This local histogram alone is not a global invoice.

## 2. The additional endpoint premise

Zero K by itself does not justify arbitrary helper chart changes. One also needs
the completely compensated main and cleanup to restore each normalized helper
independently, with no remaining helper-to-data influence, data-to-helper
displacement, or helper-to-helper off-diagonal endpoint block.

The independently checked local scalar program supplies this stronger premise:
for both orientations it replays all1021 initial columns and retains26 distinct
formal entrance-inverse tokens, restores each helper's own token, and erases
private work. Its receipt is separately bound to the frozen candidate hash.
The response, main, endpoint adapters and cleanup are kept in their literal
checked order. Adapters are not commuted through intermediate scalar gates.

## 3. Two-sided normalization for arbitrary entrance subspaces

For an entrance subspace E of dimension e, let T_E be its actual phase-sensitive
canonical Clifford chart, and let F be the final chart. The exposed helper
endpoint is the exact unitary

    J_E = F * T_E^-1.

The separately checked Clifford decomposition, including its Gaussian phase,
gives explicit rank-zero monomial unitaries L and R0 with

    J_E = L * C_(h-e) * R0.

This does not require E or its orthogonal complement to be nondegenerate.
Preapply P=R0^-1 on that helper before the complete old-response phase, and
postapply Q=L^-1 after the complete cleanup. With the endpoint premise of
section2, the helper block becomes

    Q * J_E * P = C_(h-e),

while the data block is unchanged. This is a wrapper identity on the complete
operator, not a claim that P or Q commutes with its internal gates. Both literal
boundary adapters must appear in the finite primitive and workspace invoice.
All Gaussian address columns are checked independently by the phase lane.

For the backward convention, define phi(A)=A^(-dagger). It is a homomorphism:
phi(AB)=phi(A)phi(B). Address adapters are unitary, so phi(P)=P and phi(Q)=Q.
A real scalar shear t+=q*s becomes s-=q*t. Consequently

    phi(Q*W*P) = Q * phi(W) * P.

The same chronological boundary adapters are therefore correct in the checked
inverse-adjoint orientation; no unverified reuse of an ordinary transpose is
being made. The coordinate Clifford C_(h-e) is itself unitary and fixed by phi.

## 4. Scope of the sufficient implication

The explicit response identities, complete local scalar endpoint premise,
phase-sensitive two-sided decompositions, actual heterogeneous bank placement,
charged boundary adapters and full global invoice together suffice for the
changed finite supplier. The separate exact moment and strict outer assembly
checks, under the inherited all-size supplier/workspace/precision/analytic
contracts, are what yield a conditional exponent. The portable reconstruction
here verifies the response and frame portion only; it does not independently
claim the final exponent, an unconditional multiplication algorithm, a Lean
certificate, or universal optimality. Existing supplier and upstream notices
must accompany the complete publication package.
