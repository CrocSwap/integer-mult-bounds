# P104 full-frame end-cut correction

This package gives one exact finite `I-G/2` correction word for the 104 source
and 104 target endpoints in PR #2981's 208-flag collection. It uses the
source-bound PR #1972 channel already retained by `p104-native-channel`.

The cut is immediately after that 4,058-event channel. Every source `X_s` is
then in the common full frame `F9`; every target `Y_t` is in its prescribed
eight-dimensional output frame; and the 72 arbitrary dirty helpers have been
restored. For each target, the word is:

1. transport `Y_t` from its output hyperplane frame to `F9` (one `H1`);
2. for every nonzero entry of `I-G/2`, apply `Y_t += (I-G/2)[t,s] X_s` in
   `F9`;
3. transport `Y_t` back to its exact original output frame (one `H1`).

The coefficient matrix is reconstructed from the exact channel event list.
Each of its 104 rows and columns has 48 nonzero entries. The exact coefficient
histogram is 3,376 copies of `-1/2` and 1,616 copies of `+1/2`, for 4,992
scalar additions. The checker composes the full rational register map and
verifies `Y_t = y_t + x_t`, with every `X`, `G`, `D`, and `Q` input restored.
It also verifies that each target returns to its original frame.

## Finite invoice

The inherited channel has 4,058 events, 2,624 scalar additions, 1,410 frame
transports, and rank mass 2,368. This end-cut suffix adds 4,992 scalar
additions and 208 rank-one transports. The combined finite word therefore has
9,258 events, 7,616 scalar additions, 1,618 transports, and rank mass 2,576.
The paid transport profile changes only by `+208 H1`; no new dirty or private
register is introduced.

Under the explicit frame-coordinate occupancy convention used by the checker,
the correction has peak endpoint width `104*9 + 104*8 + 1 = 1,769`: all source
frames, all target output frames, and one currently promoted target dimension.
The suffix has 5,200 scalar/transport events, for 9,198,800 endpoint
frame-coordinate event-holds. This is a finite scheduling count, not a claim
that the repository's recursive owner/idle tariff charges this quantity in
that way. The sources remain live through the suffix, so their global owner
and idle charge is still an admission obligation.

## Scope and limits

This is a finite chronological identity at the pinned endpoint cut. It changes
the target-frame contract used by the fixed-cover support cut: targets are
raised to `F9`, corrected there, and lowered back. Thus it does not contradict
or re-run the fixed-cover, monotone equal-frame obstruction in PR #3259. It
also does not use the 208 internal flag bases or establish their 1,872-step
screen as an executable word; it uses their shared 104-source/104-target
endpoint set.

PR #3618 already gives a flag-9 row-23 end-cut correction (`T48`) with 48 ADDs
and a `+2` rank-mass change at event 3489. This result does not claim that row
or cut as new. It extends the entrywise end-cut word to all 104 target rows at
the later post-channel cut, where each target starts in its actual output
hyperplane frame. The full word has 4,992 ADDs and `+208 H1` transports. The
fresh #3810 review separately closes the fixed-cover support contract; this
word changes that contract by paying target-frame lifts and descents.

The word is exact for the retained finite P104 channel. It does not supply a
global recursive owner schedule, a selected-supplier idle tariff, precision
or all-size lifting, the complete consumer composition, or a new kappa. No
claim of supplier admission follows from the finite invoice.

## Reproduce

From the repository root:

```sh
python3 -B research/p104-fullframe-endcut-correction/audit.py
python3 -B research/p104-fullframe-endcut-correction/audit.py --emit-word > research/p104-fullframe-endcut-correction/CORRECTION.json
python3 -B research/p104-fullframe-endcut-correction/audit.py
flock /home/cinna/int-bounds-pass/20261018-luna-xhigh/compute.lock python3 -B research/p104-fullframe-endcut-correction/compile_transports.py --emit-transports > research/p104-fullframe-endcut-correction/TRANSPORTS.json
flock /home/cinna/int-bounds-pass/20261018-luna-xhigh/compute.lock python3 -B research/p104-fullframe-endcut-correction/compile_transports.py
```

The first command reconstructs and checks the rational channel map and the
correction composition. The second emits 104 target rows, each with its exact
48 `[source, coefficient]` updates. The final command compares that grouped
word to the retained `CORRECTION.json`.

The last two commands compile and independently interpret both native
transports for every target. Each one must have rank one and match the exact
signed Pauli action and global phase of its frame change.
The compiler can choose among equivalent monomial factorizations, so a fresh
lowering need not be byte-identical; the retained recipes are checked against
the exact frame-change operators. Each retained target recipe is one compact
line, keeping the review diff readable.

## Open next questions

- Can the 4,992 exact scalar updates be fused into a smaller legal word while
  retaining the same source and target frames?
- What is the exact selected recursive owner/idle charge for keeping the 104
  full-frame sources alive through this suffix?
- Does the finite end-cut word compose with the required consumer and precision
  contract at all sizes?

## Credit

The scalar/frame channel and its dirty-helper cancellation come from Rohan
Arun's PR #1972. The concrete native channel realization and verifier lineage
are retained by Chafik Boukhalfa's PR #1991 package. The joint endpoint flag
collection is Nick Petalas's PR #2981, building on the credited PR #2920
endpoint geometry. PRs #3614 and #3618 supply the earlier flag-9 lower bound
and attaining single-row word; PRs #3601 and #3610 supply related flag-specific
corrections. This end-cut audit is a separate Codex-assisted finite
composition; it does not claim independent human or formal-kernel review.
