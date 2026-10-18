# Source-bound transfer checks for masked E8 decoders

Philippe Van Velzen's [padding reduction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18956000) says that the conjectural masked-line floor `C(L) >= |L|-48` for every E8 line subset is equivalent to `C(P120) >= 72`. This package independently checks that implication against retained decoder fixtures and supplies a reusable rational candidate/padding CLI. It does not claim to originate the reduction or prove either floor.

The predecessor is pinned at [4f448450adc0408be50d84e987f94391bbef069a](https://github.com/philippeVV/integer-mult-bounds/tree/4f448450adc0408be50d84e987f94391bbef069a/research/plane-port-decoder-screens/decoder-law). Its README SHA256 is `ba2d2b08b20b5ebe65a6fd125e5819c4120ba65ce6c7adae84f6448145593865`. The implementation here imports no predecessor executable.

## Fixed model

Fix a coefficient field F and a subset L of the 120 E8 root lines. Roots have squared norm two. The fixed binary pairing is `B_ij = (<r_i,r_j>+1) mod 2`, including `B_ii=1`.

A scalar decoder is any finite sum `N = sum_k v_k w_k^T`. Transpose is ordinary transpose. Require `N_ii=1` and `N_ij=0` for distinct i,j with `B_ij=1`. Other off-diagonal entries are free. Its cost is the sum, separately for every term, of `rank_F2 B[supp(v_k),supp(w_k)]`. Let `C_F(L)` be the minimum over these decoders. Identity terms give a finite integer-cost candidate, so this minimum exists.

The proof below works for every field with this same fixed mask and cost. The executable checks rational coefficients only. It does not identify a selected bit supplier with this scalar problem. Plane ports, changed pairings and operator-valued coefficients are different contracts.

## Transfer proof

For K contained in L:

1. Restrict every factor to K. Required entries remain valid. Every support-pairing matrix becomes a submatrix, so no term's rank increases. Thus `C_F(K) <= C_F(L)`.
2. Extend a decoder on K by zeros and add `e_a e_a^T` for every a in `L\K`. All new cross entries are zero, which is allowed on required and free pairs. Each singleton costs exactly one because `B_aa=1`. Thus `C_F(L) <= C_F(K)+|L\K|`.
3. More generally, zero-extended decoders on disjoint sets glue with exactly the sum of their occurrence costs. No orthogonality between the sets is needed.

Consequently `0 <= C_F(L)-C_F(K) <= |L\K|`. The gain `|L|-C_F(L)` is monotone under inclusion and superadditive on disjoint sets. In particular,

```
C_F(P120) >= 72
    implies C_F(L) >= 72 - (120-|L|) = |L|-48.
```

The converse follows by taking L=P120. Constructively, any candidate on L with cost at most `|L|-49` pads to a P120 candidate of cost at most 71. This is a reduction of the open problem, not a lower-bound proof.

Zero-cost terms cannot supply a nonzero diagonal. A term with both factors nonzero at a has the nonzero 1-by-1 pairing minor `B_aa=1`. This also proves `C_F({a})=1` without assuming coefficients are positive or that there are eight terms.

### Why the mask matters

Padding does not preserve an all-pairs Gram identity. The retained fixtures satisfy `D T^T=2G`. Dividing both factors by two gives `N=G/2`, which meets the masked conditions. After identity padding, nonzero free Gram entries across the old/new boundary become zero. The checker measures this difference explicitly:

| Fixture | Original cost | Padded cost / terms | Padded entries differing from G/2 |
| --- | ---: | ---: | ---: |
| P120 frame | 72 | 72 / 8 | 0 |
| P112 frame | 64 | 72 / 16 | 896 |
| PR717 P111 g0 | 63 | 72 / 17 | 1,000 |
| PR717 P111 g111 | 63 | 72 / 17 | 1,000 |
| PR717 P104 flip-3a | 56 | 72 / 24 | 1,728 |

All original entries match G/2. All padded entries satisfy the mask. The padded objects are not eight-term all-pairs decoders, so they do not contradict or extend PR968's floor. The finite checks also cover all 64 restrictions of one six-line domain and a disjoint two-block decoder with cost 136. Binary elimination and a separate explicit row-span cardinality oracle agree on every charged term.

## Reproduce and reuse

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py --package research/masked-e8-padding-transfer
python3.12 -Werror -I -O -B research/masked-e8-padding-transfer/verify.py
python3.12 -Werror -I -O -B research/masked-e8-padding-transfer/test_transfer.py -v
```

Registered replay, the optimized primary, eleven optimized CLI test groups, 70 research-workflow tests and a Git-free read-only export passed on Linux/WSL2, CPython 3.12.15. Scoped Ruff checks `E,F,I,B,UP,RUF,SIM` passed at line length 110. The primary replay prints its complete deterministic receipt and `PASS_MASKED_E8_PADDING_TRANSFER`. The tests exercise the actual CLI, including padding and reimport, non-symmetric rational factors, reordered IDs, legal free entries, forbidden entries, missing diagonals, occurrence pricing, malformed JSON/types, resource exhaustion, source corruption and exclusive output creation. Unit-test assertions remain active under `-O`.

For a candidate, IDs are zero-based in PR717/PR968 root-line order. The checker builds that order independently from the doubled-coordinate roots. Factors list coefficients in the order given by `live`. Integers and strings such as `"-1/2"` are accepted; floating-point JSON numbers, exponents and duplicate fields are not.

```json
{"live":[0],"terms":[{"left":[1],"right":[1]}]}
```

```sh
python3.12 -I -B research/masked-e8-padding-transfer/verify.py \
  --candidate candidate.json --pad-output padded.json
```

Output creation is exclusive. Rechecking `padded.json` reports 120 separate rank-one terms and cost 120, not the rank-nine pairing matrix's rank. The CLI reports each occurrence rank and its difference from the all-pairs Gram identity. These are candidate costs, not certified minima.

## Limits and engineering checks

This checks the transfer, not the general P120 floor, arbitrary-field fixtures, E8 hyperplane classification, native COPY implementation, physical routing, restoration, precision, a paid recursive moment or supplier admission. No full selected cold replay was run. The selected record and frozen sources are unchanged.

Input limits are 120 line IDs, 256 terms including padding, 16 MiB of JSON, 128 characters per coefficient, 256-bit reduced numerators and a 256-bit common denominator. The common-denominator check precedes dense arithmetic. Cleared coefficients have at most 512 bits, and each matrix entry sums at most 256 products of them. Matrix loops have at most `256*120*120` iterations. The second rank oracle enumerates at most 512 span elements because the complete fixed pairing has rank nine. All functions are below 60 lines.

Python and its JSON/Fraction libraries allocate dynamically. This is a managed-runtime exception to fixed-allocation rules, confined to this bounded offline checker. File size and coefficient bounds limit accepted input and arithmetic; this is not a hard heap or real-time guarantee. Subprocess tests have 60-second limits. There is no recursion in package code; the standard JSON decoder's recursion-limit failure rejects without creating output. A strict streaming parser would be needed before accepting large or service-facing inputs.

## Open next questions

Can an exact rational masked decoder on P120 cost at most 71, or can a proof exclude all such candidates? This settles the fixed-model gain-49 question for every puncture at once. A feasible first step is to submit a candidate in the documented schema and check its full masked matrix and separate occurrence costs, then pad any punctured candidate before comparing it. The blocker is algebraic feasibility or a general lower bound, not the transfer proved here. Full supplier pricing remains a separate obligation even if a cheaper decoder exists.

## Sources and credit

Philippe Van Velzen supplied the reduction and its original exact checks. DreamingOfClouds / PR717 supplied the decoder model and three retained hits. themilkman216 / PR968 supplied the exact pairing description, fixture indexing, and eight-term all-pairs scope. Their constructions and lower bounds are not claimed here. [SOURCES.json](SOURCES.json) pins the retained proof, indexing source and fixture bytes before any replay. [TASK.json](TASK.json) records the original card, changed audit scope, overlap coverage and exact sources. New work is Apache-2.0. No independent human or formal-kernel review is claimed.
