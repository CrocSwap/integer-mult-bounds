# An interleaved g=31, q=26 word misses the endpoint

**Proof, for one call order and one legal frame. No new kappa.**

Selected frontier, unchanged:
`781451/250000000`
in `certificates/selected-result.json` at base
`17469fff78c22941280f04d39dc5a1faee09c840`.

On the paired-star contract, run every first half in stage order, then five
thin maps, then every second half in the same order. Use the legal frame
`A = diag(I_q, 0)` and the rank-one off-diagonal block `B e_q = e_0` on
every stage, at `g = 31`, `q = 26`. The stage projectors do not commute.
The pure product is not `product_j (I + x_j E_j)`. Thin maps do not change
the pure factor, so no thin maps of any rank meet the endpoint on this
order and frame.

The same projectors meet the pure target when each stage's halves stay
adjacent. The obstruction is this interleaving. It is not the consecutive
rank bound and not the adjacent-halves map count.

The five maps forced by setting every `D_j = 1` are written down. Each has
rank `q = 26`, and their sum is the unique matrix that specialization
requires. They meet the normalized coefficient at that point. At the two
field points `(2, 4, 1, ..., 1)` and `(3, 5, 1, ..., 1)` the pure product
and the normalized coefficient both miss the endpoint. The argument, the
rank count, and the limits are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`, scope refined. The assigned
question is the interleaved `g = 31`, `q = 26` profile left open by PR
#7010. The result is one explicit order, not a classification of every
interleaved word.

This package does not redo the adjacent-halves count in PR #7010 or the
consecutive rank bound in PR #7005. A thin map sitting between two halves
with no other full call there, and nested or crossing orders other than
the order above, stay outside the argument. The `g = 3` censuses are not
used and do not lift. `current-priorities.md` at this base still prints the
older decimal `0.00310045`. The live selected record is
`781451/250000000`. This package uses that record and edits neither file.

Evidence class: a proof for the stated order and frame. The 6-by-6
difference is the exact product in `GF(2)[x_0, x_1]`, not a sample of
field points. The two GF(16) points are evaluations of that identity,
together with the normalized-coefficient check of the forced maps. Failing
at one legal point is enough to reject the endpoint identity. No call-order
census and no frame census was run.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-g31-q26-interleaved-five
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_PAIRED_STAR_G31_Q26_INTERLEAVED`. The checks raise, so `-O` does not
strip them. Directly:

```sh
python3 -B research/paired-star-g31-q26-interleaved-five/verify.py
```

Not run: a proof assistant, a native or supplier replay, and
`scripts/research_selected_baseline.py`. The selected record is provenance
only.

## Open next questions

- Does this same all-first-then-all-second order meet the endpoint for some
  other legal frame whose two stage eigenbases differ? The frame above
  fails for every thin map. A commuting frame is already covered by the
  map-count in `COMMUTING.md`, which is a different hypothesis. The first
  step is the two-stage cross product for one pair of legal frames that
  are not conjugate to the same `(A, B)`. Nothing external blocks that
  calculation, and this package does not do it.
- A word that puts only thin maps between a stage's halves keeps the pure
  factor `product_j (I + x_j E_j)`. Section 3 does not apply. That schedule
  is the internal-gap question left by PR #7005, not this order.

## Credit

The paired-star contract, the rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617.
PR #7010 recorded that an interleaved `g = 31`, `q = 26` word is not the
adjacent-halves case. PR #7005 recorded the consecutive rank bound and left
other schedules open.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.
