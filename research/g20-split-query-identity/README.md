# The new G20 input does not free a same-frame paid query

**Negative result. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).

On the emitted word of
[research/g20-helper-split](../g20-helper-split), field `684` is the
independent input born at frame `508`. Exactly four paid queries have a
same-frame `F2` witness that can use this field. Each is a rank-2 query.
The destination frame, through the next read, holds only one other field,
and that field's row is not the cancelled value. Zeroing field `27` by
`465 + 466 + 661 + 684` and moving it for free leaves its endpoint row at
`0` and changes `109` endpoint rows in all. [PROOF.md](PROOF.md) records
the witnesses.

## Task and overlap

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a` on canonical
`CrocSwap/integer-mult-bounds` main. Priority revision 8. Catalogue card
`bit-helper-contract`. Scope status: **refined**.

The card asks whether a changed G20 helper path improves the complete BIT
moment. This package does not build another path. It answers open question
2 of `research/g20-helper-split`: whether the emitted split enables another
paid-query removal, by pricing the same-frame identities that use the new
input.

Session r98, item 1 of the ordered eligible list. Open questions are read
from `TASK.json` in first-mention order of the PR numbers in revision-8
`docs/research/current-priorities.md`, skipping `#5599`. A question already
answered by a later merged package, or already delivered by this account,
is dropped. The remaining list is:

1. **This package.** `#5679`: another paid-query removal on the changed split word.
2. `#5679`: a stronger Gaussian caller for that BIT component.
3. `#5708`: a noncoordinate public input contract.
4. `#5708`: a stronger Gaussian caller for the conjugated word.
5. `#5718`: other legal boundary pairs.
6. `#5718`: one retained framework assumption.
7. `#5615`: a current source cut under the full dyadic criterion.
8. `#5717`: rebind the explicit-inventory audit to a changed ABI.
9. `#5717`: compiler, precision, storage and analytic premises.
10. `#5713`: metadata, generic replay selection and public rendering. The emitted-word question ahead of it was delivered in `#6636`.

Dropped before this list: `#5679`'s physical-role question, delivered in
`#6516`; `#5708`'s longer-identity question, answered by `#6290` and
`#6305`; `#5718`'s boundary-functional review, merged as
`research/p104-boundary-functional-review`; and `#5611`'s physical-target
question, answered by `#6297`. Structured `#1166` handoffs whose artifact
is an open pull request, including the H25 lanes and the `#6355`–`#6396`
chain, stay out of this list. No structured claim was unexpired at
`2026-11-08T13:15:27Z`.

The predecessor states that no additional query removal was established
and asks for a source-compatible identity on this word. The conjugation
package later keeps all `56,223` queries. Neither one checks this witness.

## Validation

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/g20-split-query-identity --check-only
python3 -I -B research/g20-split-query-identity/verify.py
python3 -I -O -B research/g20-split-query-identity/verify.py
python3 -B scripts/research_package.py --package research/g20-split-query-identity
```

The direct runs print `PASS_G20_SPLIT_QUERY_IDENTITY` with
`candidates=4`, `paid=2846` and `cancelled_endpoint_mismatches=109`.

Controls: the unmodified word meets the all-input endpoint; omitting
`684` from the field-`27` witness makes `ZERO_Q` illegal; the predecessor
witness is `{466}` and its window is also empty. Failures are exceptions,
so `-O` does not disable them.

Not run: native moduli, the eighteen-call invoice, ordinary admission,
Lean, Docker, and `make frontier6030-verify`.

## Credit

The emitted word, the split, and the open question are Ali Romman's
`research/g20-helper-split` (PR `#5679`). The predecessor word is the
pinned `prior/WORD.json.gz` in that package. Dugongue, ai-nanachi and the
notices retained there keep their credit. No predecessor file is modified.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Open next questions

1. Can one of these four rank-2 values reach its consumer on an
   already-paid route that this window does not contain? The windows hold
   only the consumer, and that row is different. First name a query that
   arrives with the cancelled value. No such field is in the window.
2. Does the later PR `#5708` conjugation word make one of these witnesses
   restorable? That word is a different program. First replay its image of
   field `684` and repeat the window test. This package does not load it.
