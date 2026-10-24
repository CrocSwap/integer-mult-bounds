# Paid phase changes cannot improve the frozen word's concave moment

**Scoped cost theorem; no higher K.** On Cao Yifan's PR4610 word, changing
symmetric phase forms cannot improve any complete recursive moment
`T_t-P_t`, for every `0 <= t <= 1`, under the fixed-graph contracts below.
This includes paid rank increases, new rank-zero-to-positive corrections,
and compatible phases on the owned-center contacts. It does not require
all phase forms to vanish.

For each helper, the added endpoint rank `g` is bounded by the sum of its
own added paid ranks. Every original paid contact block has rank at most
that helper's endpoint rank `h`. Concavity then forces

```
paid moment increase >= (h+g)^t-h^t.
```

[PROOF.md](PROOF.md) proves the all-assignment, all-exponent statement.
[RESULT.json](RESULT.json) records exact checks of its source-specific
hypotheses on both orientations, all 632 persistent paths and 408 helpers.
The eight owned rank-eight center jobs remain paid and uncredited.

This extends the question left open by
[PR4665](https://github.com/CrocSwap/integer-mult-bounds/pull/4665): that
certificate froze owned contacts and required unchanged paid ranks. Here
paid phase corrections are permitted and priced, and the obstruction is a
moment inequality rather than a homogeneous zero-solution certificate.
The rank formulas come from
[PR4654](https://github.com/CrocSwap/integer-mult-bounds/pull/4654)'s phase
chart grammar. Their native and absolute-phase theorem is a premise.

Keep the subspaces, scalar graph/order/coefficients, main operator and
explicit adapter boundaries fixed. Each scalar contact uses one common
chart. Phase corrections can be absorbed into a contact block's whole-job
normalizers; a correction is not charged separately when such absorption
is available. Each helper block has at most one original paid call, checked
from the actual word. Shared multi-owner paid operations, fusion across a
scalar contact, changed endpoints and new center protocols are outside scope.
This does not rule out higher K from a different construction.

## Reproduce

```
python3.12 -B scripts/research_package.py --package research/phase-rank-debt
```

The standard-library verifier authenticates original PR4610 bytes (retained
by PR4665), checks all path/rank/warp hypotheses, exhausts 512 small symmetric
form triangles, certifies strict concavity examples with rational intervals,
rejects four source mutations and checks independent changes to every frame
basis. It uses explicit checks that remain enabled under `-O`.
Direct exported replay is `python3.12 -I -B verify.py` from this directory.
No native all-column, outer, selected cold replay or formal kernel run is
claimed. The selected conditional K at the pinned base is still .00302015.

## Open next questions

A useful phase construction must change at least one hypothesis of this
cost theorem. One concrete option is a shared multi-owner correction across
a scalar contact: freeze the smallest actual contact, write its complete
arbitrary-input operator and compare its paid rank with the sum of separate
corrections. A formal shared rank or relaxed output flag is insufficient;
the field owners, return contract and physical bill are the missing work.
The structured questions and stopping rule are in [TASK.json](TASK.json).

Prepared by Cinna Davis with substantial OpenAI Codex assistance; Apache-2.0.
Credit Dugongue/PR4654 for the phase grammar; Cao Yifan/PR4610 for the word;
Cinna Davis/PR4665 for its previous rigidity question; Cinna Davis/PR4470,
zxv, Jacob Alan Sussman and the retained native/helper/compiler contributors.
Original bytes, Git blob and commit/path provenance are in SOURCES.json.
