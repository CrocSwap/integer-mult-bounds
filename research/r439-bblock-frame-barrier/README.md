# R439: a dependency-span obstruction to lower-frame B-block resynthesis

**Scoped structural result; no new kappa or supplier adoption.** Eight of the
ten phase-B blocks in PR1062 cannot improve their local paid-frame bill by
arbitrary exact resynthesis on their original wires using nested operation
frames contained in the block's original rank-four frame. This covers arbitrary
program lengths and intermediate proper subframes, rather than a bounded
shortest-program search. The original single climbs attain the lower bound.

The two other blocks have one exceptional source each. The same dependency
argument does not settle those sources. An exact additional calculation excludes
the simple source-star-prefix escape for both. More general circuits on those
two blocks remain open.

This resolves a restricted version of the catalogue's `scalar-to-moment`
question: shortening these blocks cannot improve the moment through this
frame mechanism. It does not exclude changing the surrounding interface,
adding wires, using frames outside the block frame, or crossing block boundaries.

## Result and finite evidence

All block frames have rational dimension four. The exact binary block map is
computed on arbitrary dirty block-entry variables. Its output dependencies,
together with monotone entry labels, force the following exit ranks:

| Block frame | Wires | Forced rank-four exits | Lower-frame conclusion |
|---|---:|---:|---|
| 506 | 10 | 10 | Paid bill cannot decrease |
| 507 | 10 | 10 | Paid bill cannot decrease |
| 519 | 12 | 12 | Paid bill cannot decrease |
| 508 | 11 | 10 | Source 19 only forces rank two |
| 520 | 12 | 12 | Paid bill cannot decrease |
| 509 | 11 | 10 | Source 22 only forces rank two |
| 521, 522, 523, 524 | 12 each | 12 each | Paid bill cannot decrease |

The eight blocked blocks contain 92 wire incidences. Their current nonzero
climbs inside the blocks are **80 rank-two and six rank-three children**;
six other wires already enter at rank four. The ten blocks have disjoint wire
sets. Thus the eight conclusions also hold for simultaneous replacements.
Across all ten blocks, 112 of 114 exits are forced to rank four.

For **same-frame** resynthesis, all ten blocks have a stronger equality result:
every original wire is essential to its block map (nonidentity row or column),
so every exact replacement on that wire alphabet must touch every wire. Every
wire then visits the same single block frame, giving the identical itinerary
regardless of the replacement's length or gate order.

The independently implemented checker reproduces four actual fixtures:

| Complete word | ADDs | Paid rank mass |
|---|---:|---:|
| PR589 | 24,305 | 5,129 |
| PR967 helper stars | 11,783 | 5,129 |
| PR1062 composition | 11,515 | 5,129 |
| PR1062 candidate | 11,500 | 5,129 |

All four have identical 661 ordered frame paths and the profile
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, including nine
rank-seven COPY charges. Their ten binary block maps agree. The checker also
replays all 661 arbitrary dirty columns, with literal COPY/ERASE and a clean
private temporary, in both full orientations. These are fresh finite checks;
they do not import the predecessor verifier or rerun its discovery searches.

[CERTIFICATE.json](CERTIFICATE.json) supplies each block matrix, the actual
entry labels, every output dependency, and rational-span basis witnesses.
[SOURCES.json](SOURCES.json) pins the four input words by Git blob and SHA256
at main `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The selected record and
catalogue are historical provenance; all four live inputs are declared for CI
invalidation. No predecessor package is copied or modified.

## Why the obstruction applies to arbitrary programs

Use the retained frame model: a register starts on its prescribed subspace;
frames grow by inclusion; an XOR ADD puts its destination and all sources on
a common frame containing their current frames. There are no extra registers,
new COPY/ERASE operations, or changes of the block's scalar map.

Let the entry frame of wire j be S_j and the exact block matrix be M. At every
point, a register's current frame contains S_j for every initial variable j
with a nonzero coefficient in its current value. This follows by induction:
an ADD's output support lies in the union of its operands' supports, and the
common frame contains both operand frames. Cancellations only remove
dependencies. Monotonicity also retains the register's own entry frame.

Consequently the exit frame of wire i contains

`S_i + sum(S_j : M_ij = 1)`.

For every row of the eight blocked blocks, the certificate exhibits four
independent rational roots in this sum, all lying in the block frame F.
Since F has dimension four and all operation frames are contained in F,
the exit frame must equal F. This conclusion permits subspaces outside the
existing catalogue as long as they lie in F.

If wire i enters at dimension e_i, the current program makes one climb of
rank `4-e_i` to F. Any alternative makes nonnegative rank increments d_k
whose sum is `4-e_i`. For `q=1-a` with **0 < a < 1**,

`sum(d_k^q) >= (sum(d_k))^q = (4-e_i)^q`.

To see this, divide by the positive total: every fraction t in [0,1]
satisfies t^q >= t. The inequality is strict when two increments are positive.
The common `(1/64)^q / W` price factor preserves the comparison. Zero climbs
are omitted. Thus splitting a forced climb cannot reduce the paid moment.
This is an analytic inequality, not a floating-point moment comparison.

The exit labels equal the old labels, so all untouched subsequent frame
visits are unchanged. Literal inverse cleanup may be regenerated: all block
wires are source/helper wires, every wire is essential, and every inverse
block touches it at the full cleanup frame. Repetition at that frame creates
no additional climb. This preserves the external path boundary. No physical
hosting or narrower precision charge is inferred from the argument.

## The two exceptions and the source-prefix test

In block 508, row 19 is the identity row and its retained entry frame is 152
(rank two). In block 509, the corresponding source is 22, entry frame 182
(rank two). Both columns are nonidentity, so the sources must participate,
but participation alone does not prove they must climb to rank four.

Consider the narrower proposal to first apply a source star
`donor += source` and then use a residual circuit which never touches that
source. Write the star as `P = I + t e_s^T`, with `t_s=0`. It is self-inverse.
For `H=M P` to fix the source column, the donor mask must be uniquely

`t = e_s + M^(-1) e_s`.

The identity source row then ensures H fixes that row as well. The exact
inverse gives donors `[35,66,89,97,466]` for source 19 and
`[17,33,38,77,87,468]` for source 22. The span of the source and required
donor entry labels has rank four in both cases. A nested source must contain
all those labels after the prefix, so it still reaches F. In fact the first
list includes a donor already on F (466), and the second includes 17 and 468
already on F. Repeated star edges do not escape the unique odd donor mask.
This excludes this prefix form only, not arbitrary lower-frame resynthesis
of the two exceptional blocks.

## Reproduce and controls

Python 3.10+ and the standard library suffice for direct replay:

```sh
python3 -I -B research/r439-bblock-frame-barrier/verify.py
python3 -I -O -B research/r439-bblock-frame-barrier/test_verify.py
```

Expected: `PASS_R439_BBLOCK_FRAME_BARRIER`, then **13 passing tests**.
The registered Python 3.12 replay runs the optimized verifier and tests:

```sh
python3.12 scripts/research_package.py --package research/r439-bblock-frame-barrier
```

The controls check altered block maps, missing dirty cleanup, frame descent,
an extra wire, an omittable identity wire, erased output dependencies, an entry
outside F, source-byte corruption and every omitted required prefix donor.
An integer Gram-determinant calculation independently checks the span witnesses.
A canceling same-frame pair is a positive non-shortest-program fixture.
A synthetic exact two-wire XOR shows the full-span premise is necessary:
when both wires enter on the same rank-one label, replacing an unnecessary
rank-four gate by a rank-one gate really lowers the moment at a=1/2.
Its strict comparison is certified by integer squaring.

Local checks pass on Windows with Python 3.12.14 and 3.14.6, including isolated
optimized execution. The selected-source baseline also passes. The research
workflow fixtures pass 19 tests with one Windows skip for the unchanged Unix
timeout helper, using workspace-local temporary fixtures and disabling Git
line-ending conversion for those fixtures. Native multistage emission, hosted invoice, a replacement
bit-interface lemma, all-size realization, precision/tape and analytic-transfer
obligations, and proof-assistant formalization were not run or discharged.
The PR1062 helper-star words retain their documented H2/K adoption gap; this
package does not adopt the pending semantic-D proof or change the frontier.

## Open next questions

Can block 508 or 509 keep its exceptional source below F using a more general
proper-frame circuit than the excluded source-star prefix? A feasible first
step is to enumerate circuits on the actual 11 wires in which that source
visits a specified rank-three subspace of F, and check the full binary map
and all other wire climbs. The blocker is the complete paid bill: saving one
source climb can introduce extra carrier climbs. A found circuit needs exact
frame, cleanup and interface checks before any supplier claim.

Can a circuit spanning neighboring B operations escape the eight block-local
lower bounds? First choose one concrete seam, recompute its actual entry and
output dependency spans, and compare every changed climb. The blocker is the
fixed outside-boundary premise of this result; it does not imply an obstruction
for an enlarged seam. Structured questions are in [TASK.json](TASK.json).

## Task, overlap and credit

The revision-2 chooser selected `incumbent-optimization`, nonce
`b047764aa77377e0ddc259818ad38530`; this refines `scalar-to-moment` to the
named ten blocks. The initial public overlap snapshot included all 831 open
PRs and drafts. The board and discussions 1163/1166/1167 were read manually;
complete discussion pagination and posting were unavailable through the
available GitHub connector, so the claim is recorded locally in TASK.json.
The final 2026-10-13 23:28 UTC snapshot covered all 837 open PRs and drafts;
exact nearby heads and search limits are recorded there as well. PR1344/1359
concern the smaller PR1221 frame-509 scalar endpoint, not this whole-block
lower-frame obstruction.
No absence-of-overlap or novelty certificate is claimed.

PR1015/1062 construct shorter programs; PR1127/1188/1208 change scalar words
with unchanged paths; PR886 fixes gate order while optimizing frames; PR933
tests particular transports and reframing; PR1048's broader exact-exhaustion
claim has the review limitations recorded in batch1099. The present argument
allows arbitrary program lengths, operands and proper subframes within eight
fixed block interfaces. PR1194/1311 address semantic D, a separate obligation.

Credit Aaron Wang (PR1015), Ross Richardson (PR923), Sagar Thakrar (PR1062),
Sricharan Vagvala (PR967), Gareth Davidson (PR915/926 and related R439 work),
DreamingOfClouds (PR589), eumemic (PR555/543), Seth Burkart (PR886), Ian Libanio
(PR933), and the retained frame/scalar-checker lineage. The original words and
predecessor notices remain unchanged. Prepared by Arham Tahir with substantial
OpenAI Codex assistance; no subagents or independent human review. Apache-2.0.
