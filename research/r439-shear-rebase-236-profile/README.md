# Rebase the PR1047 helper shear onto the 236-star R439 word

**Scoped profile obstruction; no κ claim.** The exact PR1047 shear is legal on
the seed-01 degree-two candidate, but on that changed middle matrix it saves 3
ADDs, not the 14 ADDs it saved on its original PR967 parent. The chronological
frame paths and paid child histogram are identical before and after the rebase.

## Question and result

Does PR1047's helper transvection `(destination, source) = (242, 19)` change the
paid child histogram when applied to the 11,500-ADD, 236-helper-edge candidate
from `research/r439-bsection-stars-seed01`?

The source-pinned rebase changes 13 of the 111 middle target rows. In the
candidate's exact matrix, column 19 has weight 16, column 242 has weight 13,
and their overlap has size 9. The transformed column 19 has weight
`16 + 13 - 2*9 = 11`; after charging the preparation and restoration gates,
the net saving is `16 - 11 - 2 = 3` ADDs.

| Exact bill | Before rebase | After rebase |
|---|---:|---:|
| Complete native ADDs | 11,500 | 11,497 |
| D ADDs | 5,548 | 5,545 |
| Forward positive bound F | 25,717 | 25,717 |
| Reverse positive bound B | 5,911,840 | 5,913,026 |
| Local / nine-stage guard bits | 95 / 182 | 95 / 182 |

The paid histogram is unchanged:

```text
{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}
```

Its rank mass remains 5,129, including the same nine rank-seven COPY records.
The exact profile calculation counts each register's consecutive frame-rank
increments and the paid COPY ranks. The edit adds no frame movement and does not
change any COPY/ERASE record. It inserts both shear gates in frame zero, so the
register frame paths and copy ranks stay fixed. Under this scoped paid contract,
the scalar reduction cannot change the moment because its rank histogram is
invariant. The reverse positive bound increases by 1,186; this is not an
additional saving.

## Exact chronology and identity

The candidate's D section has five pieces: 236 helper-preparation gates, 306
single-source target gates, 111 middle target rows, 306 more single-source
target gates, and the 236 helper gates in reverse order. All are at frame zero.
The rebase inserts `x464 ^= x241` immediately before the 111-row middle block,
updates that block, then inserts the same gate immediately after it. Here
`x464` is helper 242 and `x241` is helper 19.

Let `T = I + e_242 e_19^T`. The first new gate changes the helper vector from
`h` to `T h`. The middle matrix becomes `M' = M T` by toggling column 19 in each
row that contains column 242. Since `T^2 = I`,

```text
M' T h = M T T h = M h.
```

The second gate restores the helper vector. This identity holds for every
initial helper state; the verifier also checks the full forward and reverse
dirty-input boundaries. The three negative controls reject omission of the
preparation gate, restoration gate, or middle-column correction.

This proves only the stated rebase on this fixed seed-01 candidate. It does not
show that all R439 scalar edits are profile-neutral or that no other legal
frame-changing proposal exists.

## Reproduction

From the repository root:

```sh
python3 -B research/r439-shear-rebase-236-profile/verify.py
```

Expected final line:

```text
PASS_R439_SHEAR_REBASE_236_PROFILE ADDs=11500->11497 D=5548->5545 changed_rows=13 histogram=unchanged rank_mass=5129 F=25717 B=5911840->5913026 guards=95/182 controls=3 no_new_kappa
```

The verifier checks live-input hashes, the five-part chronological D layout,
the exact support-delta identity, the full dirty boundary in both directions,
all register frame paths, the paid histogram, the literal bill, the precision
guards, and the three rejection controls. It reuses the pinned seed-01 checker
for the inherited R439 word convention and the pinned owner checker for the
paid-rank accounting. Local verification passed on CPython 3.14.8. The
registered CPython 3.12 replay was not run because `python3.12` is unavailable
in this environment.

## Open next questions

The first-step positive control is the complete pass of
`research/r439-bsection-stars-seed01/verify.py`. That package's 236-star word is
the exact input here. The scalar proposal is PR1047's post-helper shear, from
`research/r439-post-helper-shear-seed03`; its README explicitly leaves
composition with other sprint results open. The scalar reduction here is a
different, re-based application of that operation, not PR1047's original
14-ADD result. Credit PR1047's author and its PR967 / PR915 / PR589 lineage,
and the seed-01 package's authors and PR1015 / PR923 / PR967 lineage. The
source pins and exact predecessor files are listed in `SOURCES.json`.

Can a distinct legal frame-moving version of this same
column change alter the paid profile without adding enough COPY/ERASE or
restoration cost to erase the gain? A first step is to exhibit one exact
candidate frame move for the 111-row middle block and prove its dirty endpoint;
only then should its full child histogram be priced. The current PR1047
chronology has only frame-zero gates, so it supplies no such move.

## Credit

Prepared by OpenAI Codex (laptop-16) with substantial AI assistance. No
independent human or formal proof-kernel review is claimed. Apache-2.0; no
selected-frontier, supplier-adoption, hosted-runtime, or multiplication-theorem
claim is made.
