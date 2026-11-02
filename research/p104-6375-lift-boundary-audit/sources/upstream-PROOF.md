# Shared-carrier input lifts

The source is the PR6372 word. The consumer is the unchanged PR6348 binary
query tree. The construction uses the native input-lift move class of PR6349
for six helpers, with a carrier shared by each pair. `construct.py` and
`LIFTS.json` give the exact event edits; the verifier regenerates the word.

## 1. One lift

Let `Z` be frame 3 and `Omega` frame 127. A helper `q` is a public input born
at `Z` and ending at `Omega`, never written by the preparation after its own
departure except by postponed ADDs. Let `A` be the scalar preparation at `Z`
and `G` the first-destination frame of `q`. Let `F` be an entrance frame whose
span lies inside `G`.

Start `q` at `F` instead of `Z`. For a lift coordinate set `h` (here `h = e_q`,
or `e_q - e_k` for the second helper of each pair), the response of every other
register `r` is `a_r = (A h)_r`. Then:

* rows whose first destination is `G` receive `a_r q` by an ADD at `G`
  immediately after they arrive;
* a carrier row `c` makes the detour `Z -> F`, receives `a_c q` at `F` and
  moves on to its old destination. The detour is hoisted before the first
  departure of any helper of the cluster, so both helpers of a pair use the
  same trip;
* any `Z`-time ADD into `q` is postponed to `G`, where its source has arrived;
* at `Omega`, `c += -h_c q` restores each coordinate.

Every response, restore and carrier trip is an ordinary ADD or MOVE and is
charged by the unchanged checkers. `construct.py` asserts the side conditions:
the entrance lies inside the first destination, each response row has a place
(a carrier or a row of the same first-destination group), postponed sources
are unchanged and arrive in the same group, dependents are unused at `Z` after
the hoist, and the departure events have the expected shape. All arithmetic is
exact.

Because the prepared value of each register when it first leaves `Z` is
unchanged and every lifted helper reaches its first destination with the same
value, the word computes the same endpoint map. The common-frame induction
and the native checker supply the relation at each tensor width, with every
local chart map and absolute phase verified.

## 2. The three clusters

Two rounds are applied in order (`LIFTS.json`): the pairs (520,655) with
carrier 171 and (544,671) with carrier 208, then the pair (472,624) with
carrier 130. The final output frames, public inputs and interface are
unchanged; only six initial frames change.

## 3. Complete signed change

Per full caller copy the paid ranks change by `{1:+6, 3:-3, 4:+3, 5:-3}` and
the target ranks by `{8:+6, 9:-6}`. The verifier recounts these from the
replay. There are no new owned fields or lifetimes: PR6372's word already has
43 lifetimes and peak storage 13. The scalar allowance rises by 52 to
129,670; the retained ordinary-work reserve funds it. Paid calls are 70,713.
Recounting the emitted caller agrees with the separate tree formula.

The complete rational crossing lies in
`(0.00315120852329, 0.0031512085233)`. Use tested saving `0.003151205` and
claim `0.00315120`. Two interval engines agree. The PR6372 word with the same
caller fails at the new claim.

## 4. Tariff scope

With `H_r = r^s`, the margin change per copy is
`g(s) = 6(H8-H9) - 6H1 + 3(H3-H4+H5)`. At `s = 1` it is exactly zero, so the
gain is a curvature effect. It is positive for `s` of about 0.873 to 1 and
+0.0044 per copy (+0.0839 over 19 copies) at `s = 1 - 0.00315`. It is
negative for smaller `s` and for tariffs such as the square root. The claim
holds at the stated exponent only, not for every concave tariff, and there is
no uniform-improvement statement as in PR6372's two-sided concavity argument.

## 5. Scope

This is a source-bound conditional improvement under the five inherited
assumptions. It is not a proof of a global optimum, a new selected frontier, a
materialized rounded multiplier or a practical speedup. The gain is about
0.0105 percent.
