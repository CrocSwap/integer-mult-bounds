# Relay-hub normal form for the P104 native word (no new κ)

**No new κ.** This package proves four structure statements about legal native words and checks each exactly on the literal
native word of #6824 (`retained/pr6824/WORD.json.gz`).

## Results

1. **Hub normal form** (`PROOF.md` section 3). Events at the zero frame on registers that start at `{0}` (`K`) commute to the start, events at the
   full frame on registers that end full (`R`) commute to the end. With `T` the invertible map of the rest, a gauge `G0` on `K` and `G9` on `R`
   with `G9 T G0 = A = I + E` exists **iff** `T[R̄,K̄] = A[R̄,K̄]`, `T[R,Hnn] = 0`, `T[Hnn,K] = 0` and `rank T[R,K] = |H09|` (the last is
   equivalent to `≤`). The first and the dual `T^{-1}[K̄,R̄] = A^{-1}[K̄,R̄]` alone are not sufficient when `Hnn ≠ ∅` (explicit
   two-register control). **No dyadic obstruction:** over `Z[1/2]` a dyadic gauge exists iff the same conditions hold and `T ∈ GL(Z[1/2])`;
   the completion is explicit. *Feed-forward corollary:* if every helper starts at `{0}` and ends full, the mid map never writes `X` or reads `Y`,
   and `T[Y,X] = E`, a dyadic gauge exists whenever `T[H,H] ∈ GL(Z[1/2])`.
   On the literal word: the four conditions hold exactly, `T^{-1}` is dyadic (denominators up to 64), the gauge re-solved from `T` alone gives a legal word with
   identical `MOVE` events and exact endpoint on all 772 rows.
2. **Crossing bound for up-sets** (section 2). For an up-set `U` of frames, the number of private descents from `U` to outside `U` is at least
   `rank A[final ∉ U, init ∈ U]`; for pairwise odd ports it is at least the clique size. On the literal word the odd-clique number is 8 and each of the 759
   maximum cliques is crossed by exactly 8 of the 24 descents.
3. **Scheduling invariance** (section 4). All linear extensions of the per-register order are legal with the same endpoint, chains and invoice; only the
   number of live private registers changes (14 to 29 over ten random schedules; the word has 14).
4. **Pair-exchange law** (section 5). If the two outputs of an exchange at frame `G` reach sinks `s1`, `s2` without a private descent, then `G ⊆ final(s1) ∩ final(s2)`.
   Literal exchange of registers 679 and 686: `G` has dimension 7 and equals the intersection of the two 8-dimensional sink frames. Without the descent hypothesis the inclusion fails.

## Hypotheses and scope

Legal words as defined in `PROOF.md` section 0 (climbing public moves, descending private moves, co-rest); endpoint `I + E` with `E` on `(K∖R) × (R∖K)`.
Exact rational arithmetic only (no modular ranks or inverses). The rewritten word has 37,819 events (the original 18,622), is a witness of the gauge
freedom, exceeds the 26,000-event bound of the default profile (this package declares no event bound) and is not re-priced; the native chart checks and the five framework assumptions of #6824 are not re-run (its `MOVE` events and chart pairs are identical).
The unit-pivot completion is a greedy rule that succeeded here; existence in general is Theorem 3.2. The pair-exchange law says nothing about the cost of alternatives.

## Overlap

The wall (`P = 0` on odd pairs) and the E8 structure are #6831 section 6; the up-set bound extends that argument. The dyadic helper-basis completion of Ali Romman and the
dual-pair criterion of #6827 concern bases at interior cuts, not the zero-frame and full-frame events. #6345 shows that the price depends on the rank histograms only;
section 4 states the invariance under schedules. Repository text search found no other statement of these items (prose may be missed).

## Open next questions

* Is a unimodular completion of the hub gauge always reachable with dyadic unit pivots?
* Can a hub gauge at an intermediate frame re-gauge more of the mid map?
* Does re-gauging the hubs change which pure dual pairs exist at interior cuts?

## Reproduce

```sh
python3 -B research/p104-relay-hub-normal-form/verify.py        # also with -O
```
Expected marker `PASS_RELAY_HUB_NORMAL_FORM` (about 15 s). `retained/` holds the #6824 native word rebuilt by that pull request's own construction;
see `retained/SOURCE-PINS.json` for the digests. Apache-2.0.
