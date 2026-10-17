# Idle-remainder donors on PR3148's T740 fill: the complex side passes the bit side; conditional κ = 0.001733427039589844234749 − 10⁻⁴⁶ − 10⁻⁷⁰

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record on
`main` is still #1094. This package stacks on the open PR3148 (Jeremy Diviney) and extends
the idle-axis exchanges of PR3184. PR3133's words, the helper widths, and PR3148's fill rows,
order and dispatch are all unchanged.

| | complex root lower (10⁻²⁵) | binding | κ headline |
|---|---|---|---|
| PR3148 | 0.0017297774946785970118869 | complex | 0.001729777494678597011886 − … |
| PR3184 (stars on fully idle 48s) | 0.0017301890612338507600957 | complex | 0.001730189061233850760095 − … |
| **this** | **0.0017347705571115131604951** | **bit (#589)** | **0.001733427039589844234749 − 10⁻⁴⁶ − 10⁻⁷⁰** |

The gain is **+3.238e-6 (+0.187%) over PR3184** and +3.650e-6 over PR3148. The complex
supplier now exceeds the bit supplier's 0.001733427039589844234749, the constant pinned in the
T74 outer ledger. **The bit side binds, so κ is capped there.**

## Changed hypothesis

PR3184 moved axes only among *completely* idle capacity-48 children. But every bin that
helpers use only partially leaves an idle **remainder child**, whose axes are the recipe axes
`[used, cap)`. That holds for every hosted #1094 child: the hosted `IDLE-REMAINDER-FRAMES` equal
`orthogonal_axes[hosted:]`. PR3148's idle bill is `{1: 173160, 3: 48951, 5: 13875, 48: 282569}`.

Removing a small child is far more valuable than reshaping 48s. Moving one axis from a rank-1
remainder into a 48 removes `1·ln 73` of moment weight, against `0.18` for a whole
`48+48 → 45+51` pair.

Here any remainder, hosted or not, may **donate** axes to a **fully idle (unhosted) receiver**
in the same replica and port. Each moved axis follows PR1252's rule:

- it commutes with all of the receiver's axes at the time it moves;
- it commutes with every stage entry/exit X and Y translation and the terminal Y translation;
- it commutes with both children's terminal translations.

Receivers stay at or below rank 51, so `73² = 5329 > 2·51² = 5202`. Moved axes come from the
donor's idle remainder, so they are orthogonal to its hosted prefix axes; the recipe sets are
orthonormal. Each group's axis multiset is unchanged.

The construction runs in two phases:

1. **Drain remainders.** Remainders are drained smallest first, one axis at a time, into the
   largest legal receiver.
2. **Stars.** PR3184's exact star optimum runs on the untouched fully idle 48s.

This produces 391,964 axis moves, from 138,369 donor children into 167,112 receivers. The idle
bill becomes:

`{1:149514, 2:15880, 3:14951, 5:13855, 42:32303, 45:34720, 48:48434, 49:47026, 50:15320, 51:104766}`

The rank mass is unchanged at `65088·740`.

## Reproduce

```sh
# PR3148's deterministic materializer (head f2927a4b) -> /tmp/t740
python3 -B research/rank7-idle-remainder-donors-t740/build.py  --t740 /tmp/t740   # ~20 s
python3 -B research/rank7-idle-remainder-donors-t740/verify.py --t740 /tmp/t740   # ~1 min
```

**Pinned inputs:**

- DATA-PHASES (`c5916ff3…`)
- the decoded fill payload (`8f4d6965…`)
- ORDER (`927226d7…`) and DISPATCH (`90edc935…`)
- PR3148's provider widths (`PR3148-PROVIDERS.json`, `52eb0d85…`)

The build reproduces PR3148's idle bill exactly.

**`verify.py` does not import `build.py`.** It re-derives:

- that donor axes lie in the donor's own remainder;
- that receivers are unhosted, and no child both donates and receives;
- the unit and orthogonal-at-receipt checks, and the commuting rule;
- the rank cap;
- the profile and rank mass;
- the complex root bracket, using its own interval arithmetic at 10⁻⁷²;
- `κ = min(floor₂₄(complex_lower), bit) − 10⁻⁴⁶ − 10⁻⁷⁰`, with gates against PR3148 and PR3184.

It also rebinds BINS to the fill. Eight mutation controls are rejected:

- a hosted receiver;
- an axis taken from the hosted prefix;
- a foreign axis;
- an axis moved twice;
- a receiver that also donates;
- a dropped move;
- the next root grid point;
- κ above the bit cap.

## Scope and remaining obligations

- **New hypothesis beyond PR1252/PR3184:** hosted remainders may donate. The moved axes are
  orthogonal to the hosted prefix and obey the full commuting rule, but no hosted-controller
  argument is given here. PR1252's admitted audit covered only unhosted pairs.
- **Not rerun:** PR3148/PR3133's native admission, the controller/owner audit (`audit_mixed.py`
  must read the axis overlay) and the outer release. The outer ledger asserts
  `complex < bit`, so a bit-binding release needs its ledger branch, and the halving pin
  `[5329,4608]` must become `[5329,5202]`.
- Because the bit side now binds, further complex-side packing gains do not raise κ until the
  bit supplier improves. All inherited all-size/compiler, realization, precision/tape, recovery
  and analytic obligations remain. PR3148 itself is unreviewed.

## Credit

- Gonzalo-Mier (PR1252): the move, the rule and the pricing.
- Guéorgui Maissouradze: the star class.
- Jeremy Diviney (PR3148): the fill.
- dcharb78 (PR3133, PR3042).
- Marius-Paul Dumitrean (PR2979).
- Jeremy Kothe (PR3015).
- Nick Petalas (PR3024).
- DreamingOfClouds and eumemic: the #589/#555 bit supplier.
- The data-phase and T37-envelope lineage.

Prepared by Rohan Arun. Done with help from **OpenCode (Space bunny free)**, whose
partially-used-bin centre idea this package generalizes, and with Anthropic Claude assistance.
Apache-2.0.
