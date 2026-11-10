# The emitted PR5713 word matches its credited scalar edit

**No new κ.** Selected κ stays `781451/250000000` from
`certificates/selected-result.json`. This package does not change the selected
frontier.

## Result

The emitted program in `research/p104-temporal-updates/WORD.json.gz` is exactly
the credited edit of the pinned PR5684 word: delete `MOVE 715,3,598` and
`ADD 715,747,1`, rewrite `MOVE 715,598,396` as `MOVE 715,3,396`, and insert the
four witness ADDs. The scalar source functional of the removed ADD equals those
four reads, with 105 coefficients. Frame supports of dimensions 0, 1 and 3 form
an `F_2^9` chain, and the local query profile changes by one H1 and one H2
removed and one H3 added.

The native and physical-caller objects in the same package are 377-byte and
595-byte summaries. Their payload hashes are not stored files. Complete native
and caller contract equality is not established.

[PROOF.md](PROOF.md) gives the replay and the rank count.
[TASK.json](TASK.json) records the refined supplier-boundary question.

## Task and overlap

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. Catalogue card
`supplier-boundary-audit`. Scope status: **refined**.

The card asks whether one changed supplier has complete native, caller,
ordinary and outer coverage. This package answers one named obligation from
that row: open question 1 of
`research/p104-temporal-fixed-independent-audit`, whether the emitted PR5713
artifact is the credited edit. The scalar word matches. The native and caller
receipts do not exhibit the contract.

Session r96, item 9 of the ordered eligible list. The 19 October handoff index
(discussion comments 19030045, 19030047, 19030049 and 19030053) is closed.
Later structured handoffs are excluded when the post is a released result, a
later pull request answers the request, or the canonical artifact is an open
pull request. That excludes the H25 lanes and the 2 November review artifacts
through #6396, the compressed-word drop request answered by open #6475, and
the absolute-phase join answered by open #6508. Unexpired claims posted on
3 November were followed by DONE notes for the same scopes. Work already
delivered by this account is excluded, including the G20 frame round trip.

The remaining list is the revision-8 first-mention open questions of #5679,
#5708, #5718, #5615, #5717 and #5719, after those delivered items:

1. #5679: another paid-query removal on the changed split word.
2. #5679: a stronger Gaussian caller for that BIT component.
3. #5708: a noncoordinate public input contract.
4. #5718: other legal boundary pairs.
5. #5718: one retained framework assumption.
6. #5615: a current source cut under the full dyadic criterion.
7. #5717: rebind the explicit-inventory audit to a changed ABI.
8. #5717: compiler, precision, storage and analytic premises.
9. This package. #5719: whether the emitted #5713 artifact is the credited edit under native and caller contracts.

`research/p104-temporal-fixed-independent-audit` checks the predecessor causal
ledger and says it does not establish emitted equality. This package checks
that equality and stops at the summary receipts. It does not rerun the author
constructor, the native engine, or the selected cold replay.

## Reproduce

CPython 3.12 and the standard library. From the repository root:

```sh
python3 -B scripts/research_selected_baseline.py
python3 -W error -B research/pr5713-emitted-edit-match/verify.py
python3 -W error -O -B research/pr5713-emitted-edit-match/verify.py
python3 -B scripts/research_package.py --package research/pr5713-emitted-edit-match
```

Expected markers are `PASS_PR5713_EMITTED_EDIT_MATCHES`,
`PASS_PR5713_NATIVE_CALLER_RECEIPTS_ARE_SUMMARIES`, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The baseline command is orientation only.

## Limits

The global factor of 18 forward calls is the author's recorded `full_calls`,
not a replay. Native maps, absolute phase, the physical caller, ordinary and
outer admission, compiler closure, precision, tape and the five framework
assumptions remain open. No new saving is calculated. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

1. Can the recorded native recipe hash and caller route hash be recomputed from
   a named retained engine on this exact emitted word? The summaries do not
   contain those payloads. The first step is to bind one engine file and one
   canonical encoding, then hash its output. No such encoding is fixed here.
2. Does the local H1/H2 to H3 replacement survive a named caller as
   `-18 H1 -18 H2 +18 H3` with every outside cost charged? The factor 18 is
   not re-derived. The first step is one caller trace that counts forward uses
   of this word. Unknown caller costs are not zero.

## Credit

The word, the witness and the temporal lemma are Ali Romman's PR5713. The
predecessor word is Joel Pulikkan / GamingPuzzled, PR5684. The fixed causal
audit that left emitted equality open is PR5719. Frame vectors in `F_2^9` and
absolute dimension-gap query rank are the retained native-frame convention.
Gaussian elimination over `F_2` is classical.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
