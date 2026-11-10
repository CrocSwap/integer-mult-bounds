# Helper-462 swap-free word under the inherited P2 ordinary tariff

**Negative comparison. No new κ.** The selected record stays
`781451/250000000`.

The zero-swap helper-462 word does not beat the published five-swap pair on
the completed ordinary bill. With the oracle multiplier read from
`add_high`, the pair totals are **208 f²** ordinary calls for the published
word and **320 f²** for the zero-swap word. At the published ledger point
`f = 1` those totals are 208 and 320. The value 320 does not beat 80.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status: **refined**.

Discussion #1166 comment 19137812 asks for one literal fixed invocation of
the N-dimensional generator left by `research/bit-completed-backend-api`.
The letter count of that package's matcher was already separated from the
tariff question. This package answers only the tariff comparison for the
recorded 0-swap, 7-scale, 27-shear word against the published 5-swap,
5-scale, 14-shear word. It does not rebuild the generator, search a shorter
shear word, or install either word in a caller.

The ordinary-call rule is taken from the pinned sources, not assumed:

- `generator.py` emits `ordered_shift(target=j, source=i)` and leaves
  `physical_tape_cost_closed` false. Coefficient preparation stays a charged
  obligation without a number.
- `add_high` runs `completed_swap_oracle` twice when the fields are reversed,
  and not at all for the forward order. The `high == 1` return comes first.
- The oracle records one ordinary call and is charged as `T_old`. Its text
  has no transition count. The earlier-target proof says the same, and
  anchors the published split at 4 earlier shears and 10 later shears
  (`64 f²` and `160 f²` sites).
- Signed-dyadic scaling prices `{2, 1/2, -1, -2, -1/2}` at `2048 V_s`
  transitions, `V_s = P Q S`. The forward affine kernels price a supplied
  residue at `1024 V_h` transitions, `V_h = P Q² G S`. Preparing a residue
  other than the linked half `(Q+1)/2` remains a caller cost.

Recomputing both words from the pinned matcher reproduces the products `S`
and `S^-1`. The published word has 4 earlier shears. The zero-swap word has
10. Every scale coefficient, in both directions, stays inside the
signed-dyadic family. Every shear coefficient has absolute value `1`, `2` or
`1/2`.

The published ledger line of 80 ordinary chunk interchanges counts swap
sites only. The inherited rule also charges the earlier-target sites. That
charge applies to both words. A reading that prices earlier shears at zero
ordinary calls would report a swap-free bill of 0 and would beat 80. The
source text is the opposite reading, and under it the swap-free bill is 320
at `f = 1`.

`T_old` still has no numeric transition tariff. The affine quantities above
use different volumes, and they are sufficient bounds rather than exact
invoices. They are not added to the ordinary-call totals. At `f = 1` the
sufficient scale charges are `163840 V_s` and `229376 V_s`, and the
sufficient forward-shear charges are `229376 V_h` and `442368 V_h`. The
ordinary-call gap does not depend on those bounds: it is 112 f² calls of
the same positive ordinary primitive.

The argument and the borrowed-branch note are in [PROOF.md](PROOF.md).
Pins are in [SOURCES.json](SOURCES.json).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/helper462-p2-ordinary-bill/verify.py
python3 -B scripts/research_package.py --package research/helper462-p2-ordinary-bill
```

Expected token: `PASS_HELPER462_P2_ORDINARY_BILL`.

## Open next questions

1. Give one `completed_swap_oracle` a fixed-tape transition and visited-cell
   bill at the helper-462 stream shape. The ordinary-call comparison is
   already decided, and that bill would only put `T_old` on the same tape
   invoice as the `1024 V_h` and `2048 V_s` bounds. The blocker is the
   random-access oracle body, already recorded as unpriced.
2. Whether a different legal factorization, still not a one-scale or
   fewer-than-27-shear search, has fewer than four earlier-target letters
   and therefore an ordinary-call total below `208 f²`. This comparison
   prices one recorded word. The blocker is that a new factorization is a
   separate search, and the reserved shorter-word question is not this one.

## Credit

Matcher, five-swap elimination and the pair ledger 80/80/224: Chris R /
Clear1nsight, PR #4957 and `research/bit-completed-backend-api`. Addressed
schedule: PR #4989 and `research/bit-row-route-generator`. Stream oracle:
Jose Manuel, `research/selected-bit-stream-routes`. Signed-dyadic and affine
bounds: JoyboyBrian. Published earlier/later anchor:
`research/earlier-target-shift-gap`. The zero-swap elimination priced here
is the schedule recorded on the unpaidmoon fork draft PR 150; this package
recomputes it from the pinned matcher and does not extend that existence
result. Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
