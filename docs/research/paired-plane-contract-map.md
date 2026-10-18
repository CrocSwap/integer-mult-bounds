# Which paired-plane quantity is being optimized?

For the fixed 56 matched planes on 112 selected ports, **126, 112, 49 and
224 measure different things**. A scalar fitting rank of 49 does not replace
the 224 native copy mass of an independent-block implementation. Use this map
when leaving the [all-pairs decoder bounds](complex-decoder-scope-map.md) for
a masked paired-plane decoder.

## Fix the endpoint first

Write `E_i` for the plane of port `i`. For source `E_j -> FULL` and target
`0 -> E_i^perp`, a normalized scalar decoder must satisfy

```text
K_ii = 1;
K_ij = 0 when i != j and E_i is not orthogonal to E_j.
```

The diagonal block on the two ports of each plane is therefore `I_2`, not an
all-ones block. Entries on orthogonal-plane pairs are free. The permission
relation is symmetric; the values of the free entries need not be symmetric.
These are ordinary scalar equations, even when the planes are labelled over
`F_2`. PR1889's [two-port obstruction](../../research/paired-plane-scalar-mask-obstruction/README.md)
explains why a binary label identity does not supply this endpoint.

## Contract map

| Result and credit | Exact object and quantity | What must still be supplied |
| --- | --- | --- |
| [PR1825](../../research/paired-plane-port-matching-seed6c563a/README.md), Cinna Davis / 1337isnot1337 | Binary factorization of the selected label-pairing matrix, with 56 matched planes and 16 nonzero query matrices. Its B14 support-pairing invoice is **126**. | This binary identity is not the displayed scalar fitting identity. PR1889 rules out its parity-preserving integral lifts, including free endpoint corrections; a new scalar construction is needed before using the optimistic moment. |
| [PR2126](https://github.com/CrocSwap/integer-mult-bounds/blob/06be72298adf84f3eef0e36f54ac31c357956417/research/paired-plane-identity-fit-seed21ef98/README.md), Cinna Davis / 1337isnot1337 | `K=I_112`, factored into 56 rank-two coefficient blocks. The exact B14 support-pairing invoice is **112**. The scalar endpoint is valid. | The coefficient-block bill does not account for native payload multiplicity. It is neither scalar rank 49 nor a complete physical copy invoice. |
| [PR2203](https://github.com/CrocSwap/integer-mult-bounds/blob/c3c85ea8c226640334b1d2246071f230d81cc137/research/paired-plane-native-payload/README.md), Jeremy Diviney | Under the independent matched-block / one-array-per-copy contract, each plane needs two independent payload arrays. There are **112 rank-two copy occurrences**, copy mass **224**, and full native profile `{7:224, 2:112}` of rank mass **1792**. | This is a bill for that implementation contract. Separate block floors do not automatically add for a jointly mixed multi-plane realization. Low simultaneous storage does not reduce the number of copy lifetimes. |
| [PR2484](https://github.com/CrocSwap/integer-mult-bounds/blob/4823273c8163e4c72472bdf7d42202e2c12d2e46/research/paired-plane-minrank-bracket-audit/README.md), thakrarsagar | Minimum ordinary scalar fitting rank is **49 over every field**, for this exact mask. A partition gives the upper bound; an isolated `I_44` plus a ten-port C5 core gives the lower bound. | Algebraic query dimension is not the sum of binary support-pairing ranks or legal native COPY charges. A realization must price its supports, payloads, transports and restoration. |
| [PR2541](https://github.com/CrocSwap/integer-mult-bounds/blob/cfe0f7f450cca3b8490ea8073a0e585bdf174e22/research/paired-plane-block-rank/README.md), ywz65 | For `d` coordinates per port, diagonal `I_d`, and the same forbidden blocks, minimum rank is **49d**, allowing arbitrary nonsymmetric, noncommuting free blocks. Thus linear queries of capacity `d` need at least 49 channels. | This is a linear query-dimension theorem. It does not impose a native bill of49 or224. Changed masks, side information, unequal port dimensions or nonlinear mechanisms need their own statements. |

For PR2203 the distinction is already visible on one plane: broadcasting one
payload produces the all-ones `2 x 2` matrix, of rank one; two independent
outputs require `I_2`, of rank two. Its positive broadcast example is legal
for the broadcast contract and fails the identity contract. Conversely,
PR2484's rank 49 construction mixes the fixed mask globally; PR2203 does not
exclude that construction by summing independent-block floors.

For vector queries, the C5 block bound in PR2541 is `ceil(5L/2)` for block
dimension `L`. Substituting `L=2d` in the isolated core yields `5d`, then adding
`44d` gives `49d`. The argument is not the invalid rule that every scalar
minrank bound tensorizes: PR2541 includes a scalar-C5 rank3 versus block-size2
rank5 control.

## Choose the next check

For a proposed binary decoder, check the scalar endpoint before pricing it.
For a scalar or vector fitting matrix, give its factors and specify whether
the quoted number is query dimension, support-pairing rank, or native copy
mass. For a native realization, enumerate independent payload arrays and
every COPY lifetime, then include legal level transitions and restoration.
Only a complete charged implementation can be compared with the selected
supplier's budget. None of the rows above establishes a new selected kappa.

The unresolved joint implementation question is concrete: can a realization
of the rank 49 fitting matrix share work across planes while meeting the
physical endpoint and paying a favorable complete invoice? First expand one
global factor into actual payloads and legal native operations. PR2203's
independent-block bill is a baseline, not a theorem for every such expansion.
Check [live overlap](../../autoresearch.md#1-orient-briefly-then-choose-a-distinct-task)
before taking this handoff; this map does not certify that a question is unclaimed.

## Sources, validation and scope

This is a navigation contribution, not a new proof or maintainer disposition.
At canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, PR1825 and PR1889
are merged; PR2126, PR2203, PR2484 and PR2541 remain open. Their linked full
commit IDs pin the inspected versions, regardless of later PR updates.
The merged source heads are respectively
`d16fb8936795ff101e4d2f63cfdc6a25066ebabf` and
`5f05652c7dc7f51555ddb59b716000199a72c0ff`.

Validation checks the source heads, quoted contracts and local link targets,
plus `scripts/research_baseline.py` for selected-record bindings. It does not
independently rerun all six research packages or the selected supplier's full
cold replay. Follow each pinned README for its exact proof, checker and limits.
PR1889 credits ctoth and collaborators in Discussion 1587 for the plane
endpoint; PR2203 credits that thread for the earlier 224 baseline and
PhilippeVV's stronger integral floor. Those attributions are preserved here.

Task `scope-navigation`, priority revision 4, nonce
`4843ad9aee96bd899b94e4d5e09c9359`, scope key `fff26335d457e528d9c4`.
The card is refined to this fixed-mask family because the existing all-pairs
map does not distinguish these pending masked endpoint and cost results.
Coordination: [PR2484](https://github.com/CrocSwap/integer-mult-bounds/pull/2484).
Prepared for ywz65 with substantial OpenAI Codex assistance and separate AI
review; no independent human review is claimed. Apache-2.0.

## Open next questions

Can the rank 49 factors be compiled to a fully charged native implementation
that improves on the independent-block baseline? Which query-factor supports
permit sharing without changing the fitting mask or losing independent
payloads? These questions require explicit operators and costs, not merely a
smaller scalar matrix rank. Source interpretation, owner/hosting obligations
and the all-size supplier interface remain separate checks.
