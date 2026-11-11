# Adjacent swaps of the #7041 block word miss mask (4)

**Exhaustive finite census, with a coordinate proof for the named boundary. No new κ.** On the length-42 block word

```text
350122222224444444000000111111333333555555
```

no pair reads as the weight-1 mask `(4)`. The same is true after every adjacent transposition. In particular it is true after exchanging string indices 17 and 18, the last `4` and the following `0`, which is the word

```text
350122222224444440400000111111333333555555
```

The selected conditional κ remains `363005817/100000000000`. This package does not change it.

## Interface, unchanged

A floor word on six sources in characteristic 7 has length 42 and calls each source seven times. `q_t` counts the first `t` letters. A pair `0 ≤ s ≤ t ≤ 41` reads as a mask when every coordinate of `q_s + q_t` lies in `{0, 1, 7, 8, 14}` and that reading agrees with reduction modulo 7. Mask `(4)` has its only 1 on source 4. This is the predicate of PR #7041 and of the unswapped inventory PR #7226. The argument is in [PROOF.md](PROOF.md).

## What is proved

An adjacent exchange of indices `i` and `i+1` moves only the prefix `q_{i+1}`. Pairs that avoid that endpoint keep the sums of the original word, and the original 903 pairs miss mask `(4)`. The 42 pairs that use the moved endpoint are evaluated directly.

Nine indices have unequal letters: `0, 1, 2, 3, 10, 17, 23, 29, 35`. The other 32 adjacent swaps are the original word. None of the nine realizes mask `(4)`.

For index 17 the moved prefix is `q'_18 = (2, 1, 7, 1, 6, 1)`. A sum `q'_18 + r` reads as mask `(4)` only for

```text
r = (5, 6, 0, 6, 2, 6)    or    r = (5, 6, 7, 6, 2, 6),
```

whose coordinate sums are 25 and 32. Neither vector is `q_25` or `q_32`. Both target sums do read as mask `(4)`, so the predicate is not what rejects them. Exactly two readings change, and both become non-readings: `(0, 18)` leaves `(0, 1, 3, 5)`, and `(18, 41)` leaves `(0, 1, 3)`.

## Task and overlap

Session r280, item 3 of the ordered eligible list rebuilt on 2026-11-11 against `e54523517d0f03e58352e647c403a5af3e525a57`.

Open handoffs were dropped when a later post completed them, a merged result answered them, the canonical artifact is an open pull request, the post says no target was taken, or the exclusion list already delivers that request. That removes the delivered 19 October index, the H25 chain, the V02 handoffs whose artifacts are open PRs #7136 and #7137 (with #7284 and #7288 already recording the receipt and assumption gaps), the 10 November CI-document handoff claimed through 2026-11-11T16:35:00Z, and the 7 November caller handoffs whose artifacts are open PRs #6837, #6862 and #6863. Three prose handoffs remain. Today's search-failure notes update the second and third and do not close them. The revision-8 next-decision rows follow, then unnamed catalogue cards:

1. Three signed added frames at seven calls (discussion comment 19377832).
2. Eight-source singleton connector at length 30 (comment 19377982, updated by comment 19537798).
3. **This package.** Six-source depth-two block at `c = 7` (comment 19384981, updated by comment 19537594).
4. Complex helpers (`p104-side-correction`, `coverage-law-change`).
5. BIT (`bit-helper-contract`).
6. New decoders and interfaces.
7. Supplier audit (`supplier-boundary-audit`).
8. All-size audit (`uniform-transfer-audit`).
9. Verification tooling (`replay-runtime`).
10. `bit-new-register-model`.

Card `connector-alphabet-change`, scope **changed**. The card asks for one new connector operation. The alphabet stays the unsigned dirty connector. The piece taken is open question 1 of PR #7226: the index-17 boundary swap, which that inventory states and does not evaluate. The other eight block boundaries are the same one-prefix census, not a second question. PR #7041 supplies the word and the two masks it was built to realize. PR #7037, PR #7016, PR #7032 and PR #7045 are different claims and are not redone.

Overlap refresh at 2026-11-11T15:22:29Z covered 589 open PR bodies and 7,253 discussion records, with complete reported pagination, plus local notes at this base. No open PR body, discussion record, or local note contains the swapped literal `350122222224444440400000111111333333555555`. Closed PR bodies were not fetched beyond local notes and the ledger.

## Reproduce

Python 3.12, standard library only, from the repository root. The census is 42 words times 903 pairs and finishes in well under a second.

```sh
python3 -B research/six-source-c7-boundary-swap-mask4/verify.py
python3 -O -B research/six-source-c7-boundary-swap-mask4/verify.py
python3 -B scripts/research_package.py --package research/six-source-c7-boundary-swap-mask4 --check-only
python3 -B scripts/research_package.py --package research/six-source-c7-boundary-swap-mask4
```

The direct marker is

```text
PASS_SIX_SOURCE_C7_BOUNDARY_SWAP_MASK4 pairs=903 boundaries=9 identities=32 named_index=17 mask4_pairs=0 adjacent_mask4_pairs=0 changed_readings=2 positive_targets=2 controls=4 no_new_kappa=true
```

Failures raise `SystemExit`, so `-O` does not disable them. The four controls are the floor-word literal, the named coordinate obstruction, the nine-boundary census, and the predicate controls. The predicate controls accept the two absent target sums as mask `(4)`, reject coordinate 2, and reject coordinate 15 because the allowed-set and modulo-7 readings split.

Not run: `make frontier7000-verify`, any SAT search, a census of non-adjacent transpositions, and the seventeen weight-3 masks on the index-10 swap.

## Open next questions

1. Which of the 17 weight-3 masks missed by the unswapped word appear after exchanging indices 10 and 11, the last `2` and the first `4`? *Why:* that is open question 2 of PR #7226. This package only tracks mask `(4)`, including at that boundary. *First step:* evaluate those 17 masks on that one swapped word. *Blocked by:* nothing algebraic; the weight-3 predicate is not implemented here.
2. Does a non-adjacent transposition of this word realize mask `(4)`? *Why:* the one-prefix reduction uses adjacency. Two moved prefixes can cooperate. *First step:* one pair of indices at distance 2 whose letters are `4` and `0`. *Blocked by:* nothing external; the domain is the `C(42, 2) = 861` transpositions, which this census does not enter.

## Credit

The depth-two interface and the weight identity are Nick Petalas's (PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943 lineage. JosieElliston's PR #6141 leaves characteristic 7 open. The diagonal equality case is `research/six-source-c7-diagonal-obstruction` (upstream PR #6941). The block word is upstream PR #7041. The question answered here is open question 1 of upstream PR #7226; that inventory is not recomputed.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
