# Measured targets for reducing local helper cost

The strongest concrete design target from this sensitivity screen is a local
redesign that saves six expensive helper paths per invocation. In the
optimistic dimension-73 packing model, that saving reaches a 1% increase over
PR564's `kappa = 0.001593134158181640`. This is a target for a new scalar word;
the current helpers cannot simply be deleted.

[helper_sensitivity.py](helper_sensitivity.py) reads the actual four-cold
zero-, four- and eight-pivot words and retains their SHA256 values in
[HELPER-SENSITIVITY.json](HELPER-SENSITIVITY.json). It identifies 280 common
width-nine noncenter helpers and reconstructs each helper's paid frame path
from the word. Eight center carriers are excluded. The most expensive four
paths pay seven rank-one children and one rank-two child; the next 54 pay
six rank-one children and one rank-three child.

The first experiment subtracts these actual paid paths and the corresponding
width-nine demand, starting with the most expensive paths. It assumes the
endpoint can be restored without replacement recursive work. Both sides of
the local paid-minus-residual mass invariant decrease by nine per helper, so
the global deficit remains unchanged. All other local costs, pending bins,
bank stock and padding remain in the fractional LP.

| Dimension | Target relative gain | Hypothetical helpers saved per call | Remaining helpers | Local paid children saved | Relaxed banks |
| --- | ---: | ---: | ---: | --- | ---: |
| 73 | 1% | 6 | 498 | `40 H1 + 4 H2 + 2 H3` | 0 |
| 73 | 5% | 32 | 472 | `196 H1 + 4 H2 + 28 H3` | 0 |
| 57 | 1% | 17 | 487 | `106 H1 + 4 H2 + 13 H3` | 588 |
| 57 | 5% | 39 | 465 | `238 H1 + 4 H2 + 35 H3` | `1148/3` |

For each row, an exact relaxed primal reaches the target rate and an exact
dual excludes that target with one fewer saved helper, using both rational
engines. Earlier integer counts were screened numerically; the receipt's
exact certificates concern the adjacent pair. The result is conditional on
this particular sequence of measured path savings, not a universal minimum
number of helpers for every possible redesign. Actual owner windows and
whole-call conflicts remain to be checked, and replacement computation may
erase the predicted gain.

A second experiment repeats the observed cold-relation change
`H1 + 2 H2 - 2 H3` and changes one width-nine residual to width eight for each
additional relation. In dimension 73, 57 extra relations reach the 1% target,
with exact rejection at 56. No 5% target was reached through 220 relations.
Dimension 57 reached neither target through 220. Thus reducing expensive
helper paths is a more promising arithmetic target than repeating this
particular entrance optimization. Additional cold relations are not supplied
by this experiment.

These numbers use the three original four-cold providers, before the later
width-seven promotions. They remain useful source-bound sensitivity values;
they do not claim optimal target counts for the expanded provider alphabet.
The 5% target also exceeds the currently cited PR543 bit-side limit. The
fetched PR555 `research/e8-bit-p111/README.md` already claims
`c = 0.001733052823330162099157`, enough bit-side headroom for this target.
Thus a new bit invention may not be needed, but replacing PR543 requires
source-bound PR555 replay and complete composition with the new complex
supplier. PR555 was inspected and was not replayed in this screen.

## Why forty more width-four promotions were redundant

Before width-seven promotions, a single width-five to width-four promotion
changes the paid profile by `2 H1 - 2 H2 - H3 + H4` and the inventory by
`+e4 - e5`. The fractional program sees only their total number `P` across
calls. The four-cold optimum has `P=448`, obtainable with 56 eight-pivot and
16 zero-pivot calls. Extending the same affine formula to 48 promoted helpers
merely provides another way to obtain that total: `28/3` such calls and
`188/3` zero-pivot calls still give 72 calls and `P=448`.

The new provider can beat this bound only if its measured cost or available
packing patterns depart from that affine continuation. Width-seven
promotions do depart from it: they introduce a new residual width and change
which exact capacity patterns are possible. The expanded source-bound stage
screen is recorded separately in [README.md](README.md).
