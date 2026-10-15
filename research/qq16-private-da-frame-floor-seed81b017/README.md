# QQ16 private-register retention frame floor

This package tests one proposed way to realize the post-`B_1_2` observation
`d_A = Y_A` used by the conditional two-query kernel in PR #2174: copy its eight
A-port coordinates into the existing owned private fields `C0..C7` and expose
them at that cut.

The exact pinned `B_1_2` word ends with the retained backward stage-one core.
That core returns all eight owned fields in frame I. At the same cut, the eight
`Y_A` data fields have frames
`f117, f124, f137, f144, f153, f163, f174, f228`. Each is the stage-one
completed frame (the first 17 basis terms) minus its actual A-port label, so
each differs from I in exactly 18 one-term Z4 entries. A matching-phase scalar
ADD from `Y_A` into `C_i` is therefore not legal as written.

The bounded normalization check enumerates all 3,650 registered cover maps
for a one-map conversion of any of those eight frames to I. There are no such
maps. In the deliberately favorable native line model, one rank-one line can
change only one frame term. Aligning the eight private fields to their source
frames therefore needs at least 8 × 18 = 144 line calls. The existing wrapper
contract associates two full-cover maps with each added line call, giving 288
cover-map operations. Eight coefficient-one scalar copies cost 32 real scalar
primitives under the pinned scalar allowance. If the cut is terminal, eight
private clears add another eight scalar primitives; if the existing next core
is invoked, its clear events can perform that cleanup and the extra clear
charge is zero.

This is already over the generous budget comparison recorded in the active
pre-F0 `B2 X_U` claim, Discussion #2074: its rank-eight output envelope leaves
at most two additional rank-one-equivalent calls above the selected ceiling.
The 144-call phase floor exceeds that slack before charging observation
handling, any multi-map route, physical address/stream costs, global hosting,
or recursive precision. This comparison is a planning screen against that
live claim, not an independently reviewed frontier theorem. The local exact
result does not rule out multi-map normalization, a different state layout,
or another controller; it rules out the cheap one-map / one-term-line private
bank relay tested here as a favorable repair.

## Reproduction

From the repository root:

```sh
python3 -I -B research/qq16-private-da-frame-floor-seed81b017/verify.py
python3 -I -O -B research/qq16-private-da-frame-floor-seed81b017/test_package.py
python3 -B scripts/research_package.py --package research/qq16-private-da-frame-floor-seed81b017 --check-only
```

Expected verifier output:

```text
PASS_QQ16_PRIVATE_DA_FRAME_FLOOR ports=8 frame_terms=18 single_map_hits=0 rank1_line_floor=144 cover_maps=288 scalar_add=32 no_kappa
```

The verifier pins the main-branch source certificate and checks the exact
program endpoint, the final clear of every `C` field, all eight frame IDs,
every registered single-map action, and the termwise line lower bound. Its
positive controls include the identity map and a one-term line cancellation;
its negative controls include wrong-stage and wrong-port frames and a mutated
source certificate. Exact Z4 arithmetic is used throughout. The 144-line
figure grants the new mechanism arbitrary legal one-term line operations on
all private fields, even though the retained wrapper currently exposes a
native-line path only for C0; it is therefore a favorable lower bound in this
restricted model.

The package does not implement a new full controller, prove that every
multi-map route is expensive, or change the selected bound. PR #1969 supplies
the retained QQ16 words and native wrapper conventions. PR #2174 supplies the
conditional decoder whose `d_A` observation motivates this experiment. This
work was produced with substantial OpenAI Codex assistance; it has no
independent human review.

The scoped claim is [Discussion #2192](https://github.com/CrocSwap/integer-mult-bounds/discussions/2192).
Its entry overlap refresh at 2026-10-14 23:05 UTC completed pagination over
435 open PRs and 877 Discussions with no warnings and no exact-scope match.
The pre-submission refresh at 23:21 UTC completed pagination over 439 open PRs
and 882 Discussions, also with no warnings or matches. At that check, PR #2174
remained open at `f79470a7931f3943360c10d15b428e0e4e479c22`, and Discussion #2074
remained open as the separate `B2 X_U` observation claim.

## Open next questions

- Can a bounded two-map or three-map route normalize the eight output frames
  while preserving the selected values, and does its complete charged profile
  stay within the same favorable envelope? A next attempt should search the
  exact pinned map action graph to depth three and stop on first discovery or
  exhaustive frontier completion. It is blocked here because the scoped
  experiment only tested one-map normalization and one-term line conversion.
- Can another state layout expose `d_A` without using a private field in frame
  I? This would change the mechanism, so it needs a new exact interface and a
  fresh full-cost screen.
