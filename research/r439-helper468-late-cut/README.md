# R439 helper 468: rank-eight suffix bound begins at B gate 88

**Scoped negative result with a written footprint proof and complete exact ledger.
No new circuit, supplier or kappa.**

PR1256 excludes an eager restore/isolate block at the original PR589 post-scatter
cut and leaves later target-read cuts open. This contribution checks one helper,
**468**, at every original B/C MOVE and individual ADD boundary. A later cut may
have already delivered a needed target input; its inverse rows and dirty column
must be recomputed rather than reusing the original-cut obstruction.

All **4,874 cuts** are excluded for an arbitrary restore-and-isolate block at
one common rational frame of rank at most seven:

| Exclusion | Cuts |
|---|---:|
| Target 208 would be promoted into an incompatible frame | 177 |
| The restoration/isolation footprint has rank eight | 1,557 |
| Helper 468 itself has already reached rank eight | 3,140 |

The starting cut and all **1,310 MOVEs plus 3,563 ADDs** are included. The
block may have arbitrary length, scalar mixing, target feedback and independent
dirty auxiliaries at its common frame. The [proof](PROOF.md) gives the exact
output/frame contract and the necessary-condition argument. It excludes any
permitted completion after such a block, not merely the original remaining C.

The single-frame result does not rule out earlier lower-frame preparation, a block using multiple
frames, new COPY transport, descent/reset, a changed prefix/output basis, or
restoration with delayed isolation. Donor ADDs are taken in their original listed
order. Other source/helper outputs and target output roles remain fixed; helper
468 is the proposed smaller endpoint. No general bit-supplier impossibility is claimed.

The same ledger gives a stronger later-cut result by applying PR1128's
two-sided lemma. **After B gate 88 moves target 208 from frame 0 to frame 152
(cut 177), every permitted reversible linear suffix must end helper 468 at rank
eight**, even if it uses several frames and extra restored dirty auxiliaries.
All 4,697 later cuts have that rank-eight obstruction. The first 177 cuts still
pass the two-sided rank-seven test; their single-frame blocks are excluded,
but staged suffixes there remain undecided. This identifies the precise original
MOVE before which a changed width-seven mechanism must begin.

The critical source gate is `B[88] = [152, 208, [19]]`. The obstruction begins
at its target MOVE, before the ADD: the restoration row and dirty column are
unchanged across the transition, while their required frame join grows from
seven to eight. The first 177 cuts are not proofs of feasible staged suffixes.

## Reproduce

From the repository root, standard-library Python:

```sh
python3 -I -O -B research/r439-helper468-late-cut/verify.py
python3 -I -O -B research/r439-helper468-late-cut/independent.py
```

Expected markers:

```text
PASS_R439_HELPER468_LATE_CUT cuts=4874 excluded=4874 joins=9 arbitrary_suffix_from=177 new_kappa=false
PASS_INDEPENDENT_R439_HELPER468 cuts=4874 excluded=4874 integer_geometry_cases=9 arbitrary_suffix_from=177
```

`generated/EVENTS.json` is the complete ordered suffix event stream. A MOVE is
`[section, gate_index, "MOVE", register, previous_frame, new_frame]`; an ADD is
`[section, gate_index, "ADD", target, source, donor_offset]`. Before a multi-donor
gate, all operands climb in target/listed-donor order; each donor ADD gets its
own cut. Cut 0 is the original post-scatter boundary; cut k is after event k-1.

`generated/CUTS.jsonl` stores every cut, the helper's current frame/rank and its
exclusion. For current rank at most seven it also stores restoration, dirty and
participant masks in original register coordinates, and the contributing frames.
For rank-seven footprints it includes all illegal target promotions and all
missing target-dependency masks. Rank-eight helper cuts need no further footprint
test. `generated/GEOMETRY.json` supplies the nine independent minor/normal
witnesses and a full-frame witness. `generated/CERTIFICATE.json` records all
counts and hashes. The writer refuses existing receipt directories.

The primary checker uses rational frame elimination and packed binary rows.
The separate checker uses set-valued rows, a descending-column inverse and
integer Bareiss determinants/normal equations. It imports no primary or
predecessor executable. Both agree on every event, cut and final dirty column;
both belong to this AI-assisted contribution, not independent human review.

The credited card's working example also passes:
`python3 -I -B research/r439-bsection-stars-seed01/verify.py`. This confirms the
historical finite word and its documented H2/K pattern; it does not adopt a new
supplier. This package uses the original PR589 word, rather than composing those
ADD savings or changing selected artifacts.

The full registered replay passes on Python 3.12.15, and all ten tests also
pass on Python 3.14.7. Regressions check all 168 invertible binary 3-by-3
matrices, 1,008 inverse updates and 10,080 outside-frame span cases. Controls
reject changed sources, omitted cuts/MOVEs, false minors/normals and receipt
overwriting; an isolated export passes both engines under `-I -O -S -B` without
writing files. Four frozen inputs match their exact source Git blobs.
`VALIDATION.json` records the environment and the unrun physical obligations.

## Accounting and limits

The ideal width-seven two-slot relocation has favorable complete child deltas
even before constructing a suffix. It retains all nine COPY/ERASE pairs, returns
all eight old host coordinates, consumes an idle rank-seven slot and accounts
for the changed helper path. For old remainder r in {2,4,6}, the rank-four-cut
delta is `e3-e2-2e1-e7+e_(r+8)-e_r`; at rank six/seven it is
`-e1-e7+e_(r+8)-e_r`. Both preserve rank mass and reduce child count. Subadditivity
proves a strict favorable moment for every exponent between zero and one.

This is an optimistic planning scenario with every other child retained and
added preparation/storage/source/restoration/frame/scalar charges set to zero.
It is not a realized invoice or physical owner assignment. The exact geometry
still prevents the one-common-frame block even when all that work is free.
Packed precision/tape, native compiler, hosting, analytic transfer and a complete
outer multiplication theorem are not verified or supplied by this audit.

## Open next questions

Can a staged mechanism clear helper 468's dirt from target 208 at a compatible
lower frame before isolating the helper at rank seven? A feasible first step is
one explicitly priced two-frame block with a full 661-column replay and legal
continuation. It must also preserve the source/target dependencies identified
by PR1256 and replace any later reads of the changed helper. It must begin before
the original target 208 MOVE at B gate 88; every later original cut has a general
rank-eight terminal bound. The initial-cut theorem
excludes a single common-frame block at an original cut; it does not decide this
changed mechanism. Physical hosting and all preparation/restoration work must
be paid if a finite construction is found.

## Provenance and credit

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. OS assignment seed **17**,
bit supplier track, selects helper 468 from the five initially blocked helpers
at index `17 mod 5`. The within-helper cut domain is exhaustive and deterministic.
Coordination: [discussion1362](https://github.com/CrocSwap/integer-mult-bounds/discussions/1362).

Ross Richardson's PR1256, head `d6d5a994fcdcd8d04ec439ff988daa8f37b17ece`,
supplies the initial-cut footprint argument, exact helper468 fixture, helper470
exception and stated later-cut question. Ali Romman's PR1128, head
`df29b159239b79d7e451d6ddda826a73e0e50a67`, supplies the two-sided boundary model;
his PR1043, head `e309e17f83f5759b1ea1fa24a76f24838784cb4d`, deletes helper470 by
changing an earlier source boundary. Those constructions are not combined here.
DreamingOfClouds' PR589 on eumemic's PR555/543 supplies the selected bit word and
interface lineage. Sagar Thakrar's PR1023 motivates rank-seven hosting. The
original NOTICE is retained, along with the exact compressed word bytes.

New work by **Cinna Davis (@1337isnot1337)** with substantial **OpenAI Codex
assistance** in mathematics, code, experiments, verification and writing.
Apache-2.0. Exact Git blobs, hashes, source heads and scope metadata are retained.
