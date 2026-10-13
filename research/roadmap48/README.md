# Full-center frame promotions, U8 composition and cleanup retiming

This experiment rebuilds 48 frame promotions on the archived PR799/X4 word.
It reproduces 56 `(4,1) -> 5` merges and passes the independent exact scalar
audit on all 728 columns in both orientations, including frame chains,
entrances, helper cones and cleanup. The original arithmetic is unchanged.

It also composes the frame edits with NewBArch's existing U8 donation/restore
rewrite from the pinned PR869 package. Both edit orders produce the same
word. The measured U8 delta survives on the promoted base and improves its
direct conditional κ by `0.000000246914314083`. A bounded cleanup retiming
census finds no further profile improvement in the stated move class.

The final nine-dimensional-center word is evaluated as its own construction.
Compatibility with the earlier parent is reported separately and does not
accept or reject the cost calculation.

| Model | Local mass | Rank-48 idle count | Global mass | Deficit | Conditional κ |
|---|---:|---:|---:|---:|---:|
| PR799/X4 | 5634 | 2396 | 520704 | 2560 | 0.001661634653669567 |
| Credited PR869/U8 reproduction | 5634 | 2396 | 520704 | 2560 | 0.001661948695165034 |
| 48 promotions, same whole-helper placement | 5642 | 2396 | 521280 | 1984 | 0.001297089685005627 |
| U8 + 48 promotions, same whole-helper placement | 5642 | 2396 | 521280 | 1984 | 0.001297336599319710 |
| Alternative profile with 12 fewer idle children | 5642 | 2384 | 520704 | 2560 | 0.001672153593380162 |

The last row is exact profile arithmetic, not a generated alternative owner
map. A different construction may change capacity, calls, helper widths or
placement. Its own complete cost inventory must determine the resulting κ.

## Reproduction

From the repository root, using standard-library Python:

```sh
python -B research/roadmap48/verify.py --check-committed
```

This builds the word, checks every scalar column, recounts all 36,288 helper
roles and occupied cells, verifies pricing with two retained exact moment
engines and the 47 outer arithmetic constraints, rebuilds the U8 composition,
enumerates the cleanup retiming class, rejects 36 donation/restore controls,
runs 42 regression tests, and checks every retained source and artifact.
Results are written under `build/roadmap48`. No external experiment files
or unpublished scripts are needed. Normal Python is required because the
retained engines use assertions.

To evaluate the declared final recurrence directly, without a parent check:

```sh
python -B research/roadmap48/cost_model.py
python -B research/roadmap48/cost_model.py --field roadmap_hypothetical_global
python -B research/roadmap48/cost_model.py --m 74 --output build/roadmap48/M74-MODEL.json
```

Changes to `--m`, `--live` or the supplied profile are explicit model
hypotheses, not generated templates. The cost driver certifies a rational
root interval. Above the retained outer domain `b<1/32`, it reports the
nominal root but does not apply that outer formula.

The focused GitHub workflow runs this replay with Python 3.11 and 3.14.
Local finite verification does not establish that remote CI has completed.

## Direct accounting

The final edit changes `A[4235:4283]` to the full F₂⁹ frame. The eight center
declarations change accordingly. Each register's frame increments telescope;
their combined mass excluding center descents is `5570`. The helper width
sum remains `3778`. Center descent mass rises from `64` to `72`.

Recounting the unchanged physical helper cells yields
`idle = {1:1, 3:1, 44:1, 48:2396}` in both words. Therefore:

```text
local mass = 5570 + centerVolume
S = 72*(5570 + centerVolume) + idleMass
idleMass = 1 + 3 + 44 + 48*2396 = 115056
D = 73*7168 - S = 7168 - 72*centerVolume
```

For `centerVolume=72`, `S=521280` and `D=1984`. Reducing the rank-48 idle count
by 12 removes `576` mass and yields the alternative profile's `D=2560`. The
same owner cells do not produce that reduction. This is a distinction between
complete cost inventories, independent of earlier-interface compatibility.

The declared paid-child recurrence gives

```text
sum_r r*n_r*(73/r)^b = 73*7168
```

The final word with unchanged placement has the certified root interval
`[0.001298774311768572389856, 0.001298774311768572389857]`.
The alternative profile has interval
`[0.001674954374355989506780, 0.001674954374355989506781]`.
The supplied higher value `0.001674954374355989549644` is above this root;
both engines reject it as an acceptable lower endpoint. Correcting that
endpoint preserves the alternative profile's 18-digit κ.

## Implementation and outputs

`experiment.py` uses the retained `build_promotion.apply` for the frame edits
and then recounts center descents. The original builder excludes changed
center descents, so using it alone would preserve an obsolete `8:8` fee.
The report's `centre_ranks` and `cst` are also refreshed to `[9]*8` and `72`.
B, cut, cleanup, precondition, entrance and final-frame data are preserved.

`FINAL-CONSTRUCTION.json` binds the final word, dimensions, helper widths,
calls, idle and capacity. `PAID-EVENTS.json.gz` lists positive register-frame
increments and center descent charges. `END-MERGES.json.gz` checks the literal
`490 -> 434` END-increment map and the 56 removed increments. This is not
an exhaustive search or an optimality claim.

`CUT-COLLISIONS.json` supplies eight exact inverse-column certificates.
On unrestricted 728-dimensional rational inputs, A is a product of invertible
elementary gates, so each center row is independent of the other cut rows.
This avoids dense elimination. Restricted clean-input subspaces and other
specified future-output requirements are separate questions.

`MOMENT-ANALYSIS.json` records numerical first/second-order approximations,
errors, mean, variance, capacity price and mass elasticity. Numerical
diagnostics are distinct from the exact rational root signs.
`CARRY-COST-TABLE.json` gives the direct prices for promoting 0–8 blocks.
`PARAMETER-SCENARIOS.json` identifies changed-geometry hypotheses explicitly.
`RESULT.json` retains source pins, exact moments, the PR589 bit blob and four
outer negative controls. `VERIFICATION.json` binds code and generated outputs.

## U8 composition and bounded retiming

`optimizations.py` retains the PR869 source at
`73e86f69bf9a391e3c334999f7bbe3825dc42759`, checks all four vendored source
blobs before executing the builder, and reproduces its pinned U8 output.
The A edits and U8 B/tail edits act on separate fields; the independently
recounted result agrees exactly in both edit orders. Its local profile is
`{1:2492,2:338,3:446,4:106,5:128,9:8}`. Relative to the promoted base the
delta is `{3:+16,4:-32,5:+16}`, preserving mass and helper widths.
Recounting all physical roles preserves the same idle inventory. The combined
root interval is
`[0.001299021867932295987709,0.001299021867932295987710]`.
`U8-A48-AUDIT.json` records the exact audit and `OPTIMIZATIONS.json` records
prices and the 36 rejected controls, including their rejection stage.

`retiming.py` defines a finite move class: move one ordinary full-frame
cleanup gate into the early tail after B, keep scalar gates unchanged, raise
tail frames only as needed by their existing frames and register states, and
retain all final frame caps. A pool gate's operands must be untouched by
earlier ordinary cleanup gates; gates already in the early tail are excluded
from both the pool and that prefix. This permits crossing the ordinary
cleanup prefix by disjointness. Every tail position that commutes with the
crossed suffix is then enumerated.

For nonzero ADD coefficients and distinct source/target registers, two ADDs
commute precisely when neither target is the other's source. A nonidentity
SCALE commutes with an ADD precisely when its register is absent from that
ADD. SCALEs commute with each other; identity primitives are handled
separately. These criteria follow by multiplying the elementary matrices.
The tests independently compare every matrix column for 1,764 rational
primitive pairs. Raising a frame by joins is the minimal permitted repair;
a failed final cap therefore excludes that candidate in this move class.

| Word | Pool gates | Registers | Candidates | Cap failures | Valid | Improved profiles |
|---|---:|---:|---:|---:|---:|---:|
| X4 | 124 | 219 | 17399 | 521 | 16878 | 0 |
| 48 promotions | 124 | 219 | 17399 | 521 | 16878 | 0 |
| U8 + 48 promotions | 129 | 229 | 19082 | 637 | 18445 | 0 |

Each word has just one valid paid profile in this census, equal to its
baseline. Every distinct valid profile has a retained representative word
that passes the full independent all-column audit and exact pricing.
The compressed `*-RETIMING-CENSUS.json.gz` files list every enumerated
candidate and classification. This excludes only the stated one-gate,
monotone-repair class; multi-gate moves, alternative frame choices and new
global placements remain outside it.

Compressed artifact equality uses decompressed bytes; text/source bindings
use LF-normalized bytes. Gzip headers and verification timestamps are
diagnostic. Immutable archive hashes remain byte-exact.

## Scope and attribution

These checks establish the finite scalar/frame construction and the cost of
its explicitly declared recurrence. The conditional exponent transfer retains
the cited bit supplier and all-size, realization, hosting, precision/tape and
analytic hypotheses. This is not a full multiplication theorem or a Lean
formalization. No change is made to the repository's selected construction or
to `upstream/`.

The full-center word changes the recursive center interface. Its direct price
uses the explicitly stated all72 recurrence; a complete alternative global
generation still needs compatible suppliers, placements, phase scheduling,
and the retained all-size and analytic transfer arguments. Finite local
success alone does not provide those obligations. The hypothetical reduction
of 12 idle children is not asserted as a construction.

The base is Jeremy Kothe's PR799/X4, retaining icekylinx's source gauge,
Chafik Boukhalfa's PR741 frames and DreamingOfClouds' PR589 bit supplier with
their predecessor work. The existing source credits and Apache-2.0 notices
are preserved, including the U8 proof note and notice. Liamia supplied
theoretical guidance and corrections; OpenAI Codex performed the concrete
implementation and verification. See [NOTICE.md](NOTICE.md).
