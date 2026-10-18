# Independent charged-invoice review

Result: **PASS for the six specified L5 conditional complex boundaries.**
The proposed conservative/full-center formulas agree with the retained PR606
`encoder_conservative.py`, `full_centers.py`, and `banked.py`. This review
does not admit either encoder or a compensation construction.

## Independent replay

Run from the repository root:

```sh
python3 -B research/h6-independent-audit/review/charged/replay.py
python3 -B -O research/h6-independent-audit/review/charged/replay.py
```

`charged/replay.py` imports only the outward-rational logarithm/exponential
oracle from `invoice/verify.py`; it independently assembles all masses and
actual child ranks without importing `banked.py`, `costs.py`, or
`charged_screen.py`. Its `RESULT.json` pins the reviewed sources and records
the strict adjacent slack intervals at scale 10^24. The following decimals
are rounded displays of those certified intervals:

| Baseline | Target | Largest additional R | Slack at R | Slack at R+1 |
| --- | --- | ---: | ---: | ---: |
| H6 paper | selected frontier1094 | 88,765 | +0.2961431695 | -0.1269725825 |
| Conservative encoder | selected frontier1094 | 41,810 | +0.3894668303 | -0.0336489217 |
| Full-center fallback | selected frontier1094 | 66,313 | +0.1963782047 | -0.2267375473 |
| H6 paper | PR1424 title comparison | 88,409 | +0.0920755351 | -0.3321055559 |
| Conservative encoder | PR1424 title comparison | 41,454 | +0.1829300770 | -0.2412510140 |
| Full-center fallback | PR1424 title comparison | 65,990 | +0.0811201280 | -0.3430609630 |

Every comparison uses the exact selected rational or the exact stated
PR1424 decimal, with compensation path `[1,7,8,1]`. The root function is
strictly increasing in the count because per-helper pressure is positive.
These signs therefore establish the largest nonnegative strict integer
capacity for each fixed invoice, without a floating root or equality tie.

## Accounting comparison

At L5, m=81, q=4, pad rank=13, and the strict child cap is57. The direct
assembly charges paired-data idle ranks `[32,32,16]` with mass `2Nr` each.
Each ordinary helper role contributes stock5/4 and total path-plus-pad mass
405/4. The independent baseline and helper mass identities hold, and every
actual rank satisfies `m^2>2r^2`.

The conservative case uses both data paths `[1,15]`, center histogram
`{17:256,15:560}`, bill12,752, and precisely the five retained role groups:
28,800 `[1,8,8]`, 1,920 `[9,8]`, 13,440 `[9,6,2]`, 560 `[15,2]`, and
256 `[17]`. Their total44,976 adds stock56,220 to base123,840, producing
stock180,060. Their entire paths and pad pressure are charged while the
deficit remains60,080, exactly as in PR606.

The full-center case replaces the data terms with source `[16]` and target
`[1,7,8]`, retains all816 width17 center descents, and adds816 ordinary
width17 center roles. Its center bill13,872 reduces the deficit to54,480;
the role stock addition1,020 produces stock124,860. The slice replacement
in `charged_screen.make_row` is exactly the retained
`full_centers.built(17,816,5,[1,7,8])` formula. It charges both the private
center descent and the distinct stock-bearing center role; these have
different accounting purposes and are not an accidental double count.

The H6 paper row charges the base data, original center bill and retained
idle ranks, but none of these encoder helper groups. Its88,765 allowance
is therefore an optimistic compensation screen, not the allowance after
an emitted K encoder. The README states this limitation correctly.

## Restoration and construction scope

The README and receipt explicitly reserve scalar/frame legality,
arbitrary-dirt restoration, inverse-transpose orientation, data chronology,
compiler admission, extra private descents, and the bit-side envelope.
The full-center proposal also inherits PR606's need to retain fresh source
information needed by compensation before those sources reach FULL.
The helper README's exact-lemma requirements cover this through the common
frame, monotone climb, target chronology and emitted whole-word clauses.
No unpriced stage is described as an admitted construction in the reviewed
files. Passing these invoices does not establish a legal word.

## No-stockcopy inference

The stated restricted inference is correct. If the complete fresh flow
matrix is a sum of clean channel outer products `ab^T`, matrix rank bounds
the number of channels below by N. Charging at least one descent rank for
each gives C>=N. If no extra stock enters and no previously charged work
is removed, `D=(L-1)N-LC<=-N`; positive pressure cannot make this invoice
pass. For compensation alone the retained PR606 moment/spectrum argument
gives `rank(I-K)=N`, so adding that no-stock bill to existing K descents
only worsens D. This is a consequence of the explicit factorization and
no-stock assumptions, not a general DAG or physical-helper lower bound.

The ordinary restored-wire caveat is essential and correctly stated:
stock `LR/q` contributes mass `LmR/q`, which is exactly its path-plus-pad
mass, so such helpers leave D unchanged. They cannot be counted as unpaid
centers in this exclusion. The README also correctly observes that the
H6 paper allowance exceeds N and therefore rank alone does not reject it.

## Provenance wording adjustment

The reviewed `CHARGED-SCREEN.json` has hashes for `banked.py` and the
selected record, but the helper README says it records "all ... input
hashes." It does not itself hash the imported `costs.py`/`portable.py` or
the two encoder proposal files whose literal profiles it transcribes.
This is a provenance wording gap, not an arithmetic failure. Either add
those input hashes to the charged receipt, or change the helper README
to point explicitly to the parent `SOURCES.json` for source closure.
The independent receipt records hashes for the relevant arithmetic and
proposal sources reviewed here. Frozen predecessor files were unchanged.

## Open next question

Emit and check a complete dirty-restored compensation word with legal
common-frame chronology, then replace conditional profiles with that
word's actual source, target and helper paths and extra descent bill.
Only after this step can the screened helper allowance be treated as a
construction target attained by a supplier.

Prepared with OpenAI Codex assistance; predecessor mathematical and
accounting attribution remains DreamingOfClouds and Dominik Scholz/PR606.
