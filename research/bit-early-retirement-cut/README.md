# Early retirement in the fixed PR589 bit prefix

**Finite construction and scoped negative result; no new kappa.** After the
unchanged PR589 `D/A/scatter` prefix, five of PR1128's six width-seven candidates
cannot even be restored by a first single-frame block without losing a required
target input. Helper **470** is the exception: restore it at rank two, clear its
dirt at rank seven, and change two cleanup instructions. The complete finite
word preserves all 661 input columns and reduces that helper's terminal width
from eight to seven.

This fills a concrete early-cut opening in Ali Romman's
[PR1128](https://github.com/CrocSwap/integer-mult-bounds/pull/1128), pinned at
`df29b159239b79d7e451d6ddda826a73e0e50a67`. It does **not** improve on his
[PR1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043), pinned at
`e309e17f83f5759b1ea1fa24a76f24838784cb4d`, which already deletes helper470 by
changing the earlier source boundary and supplies a complete hosted invoice.
Here `D`, `A`, retained copies, scatter, and the original `B` are byte-for-byte
unchanged; a three-gate block is inserted between scatter and B. No savings
from the two constructions are combined.

The base is `49b3157d1d89adcef16df8be98445451672be5ba`. Its selected conditional
kappa is `836330098538459/500000000000000000` (PR1094), with the complex side
binding. The selected record and `upstream/` are unchanged. Assignment seed 8
selected the bit-supplier track and rotated the six-case inspection order to
start at helper468. This is a complete six-case calculation, not a randomized
optimization or a universal bit-supplier obstruction.

## Exact finite construction

Use the original register/frame identifiers in the pinned PR589 word. Insert:

| Frame | Operation | Purpose |
|---:|---|---|
| 186 (rank 2) | `470 ^= 77` | Restore helper470 to its original dirty input |
| 513 (rank 7) | `444 ^= 470` | Remove that dirty input from register444 |
| 513 (rank 7) | `475 ^= 470` | Remove it from the retained-total register475 |

The earlier scatter already consumed the unchanged snapshots; it is not rerun.
After these three gates, helper470 holds its initial input and no other register
contains its dirty column. The original B does not touch register470.
In C, replace zero-based gate 580, `444 ^= 470`, by `444 ^= 77` at the same
full frame. Omit zero-based gate 2343, `470 ^= 77`. End helper470 at frame513;
all other final frames remain unchanged. These indices are checked against the
pinned operands, not accepted as unverified positions.

The complete patch is recorded in [CERTIFICATE.json](CERTIFICATE.json).
`patched_sections` in [verify.py](verify.py) reconstructs its literal stream
without copying or editing the frozen source word. Both checkers replay the
whole stream and its literal scalar inverse, including every dirty column.
Forward frame legality is checked over Q. The inverse replay is scalar only;
it does not claim that reversed frame climbs are a legal physical program.

| Complete local quantity | PR589 | Early retirement |
|---|---:|---:|
| ADDs, including 527 scatter ADDs | 24,305 | 24,307 |
| MOVEs | 2,911 | 2,912 |
| COPY / ERASE | 9 / 9 | 9 / 9 |
| COPY ranks | nine rank-seven copies | unchanged |
| Records | 27,234 | 27,237 |
| Paid children, including COPY charges | 2,920 | 2,921 |
| Paid rank mass | 5,129 | 5,128 |
| Helper470 frame dimensions | `0 -> 1 -> 8` | `0 -> 1 -> 2 -> 7` |
| Other 660 frame itineraries | baseline | identical |

The exact local histogram changes by `+H1 + H5 - H7`. Both words have scalar
positive-majorant row-sum peak 49,347 (16 bits), calculated by replacing every
XOR by addition on initial unit row sums. This is a finite scalar coefficient
bound, **not** the packed/native precision invoice or the nine-stage prefix
bound. All nine existing COPY/ERASE charges are retained; this package does not
recompile their native implementations.

## Why the other eager restorations fail

The cut is the finite 661-register scalar contract of PR1128: `w = M u` just
after D/A/scatter, with its original current frames. Retained scatter-copy
channels are unavailable for new suffix reads. M is invertible over F2.
Allowed suffix operations are invertible scalar operations at a common rational
frame and monotone frame enlargements, with no new COPY, descent, reset or other
high-to-low transport. Extra workspace starts with independent dirty inputs.

For a helper h, let `a_h = e_h^T M^-1` be its restoration row and `d_h` the
support of its dirty column in M. A **first single-frame restoration block**
performs all scalar work at one frame F, with no earlier lower-frame preparation.
It returns h to its original input. Every boundary coordinate in `support(a_h)`
must participate: otherwise the block cannot distinguish two independent
boundary states differing only in that coordinate. Participating registers
must reach F. This argument allows arbitrary block length, register mixing,
target feedback and any number of independent dirty auxiliaries at F.

If the block also isolates h's dirty input from every other register, every
member of `d_h` must participate too. Hence its forced footprint contains
`P_h = support(a_h) union d_h union {h}`. A rational-span computation gives a
unique rank-seven join U for these six footprints, reproducing the specific
necessary-condition survivors named in PR1128. We do not rerun that PR's
separate exclusion of the other 433 helpers.

For target t the desired final value is `y_t + x_(t-111)`, whose row in boundary
coordinates is `b_t = (e_t + e_(t-111))^T M^-1`. Suppose F is not contained in
that target's final frame V_t. No dependency path from a register at F can ever
reach t, even through later scalar mixing: every subsequent frame contains F.
If `b_t` has a nonzero coefficient on a boundary coordinate forced into the
block, then two inputs differing only in that coordinate have identical
remaining accessible information but different required target values. No
allowed completion exists. Moving additional registers to F cannot repair it.

This is an information-access obstruction, even if the block, all remaining
scalar work, and every permitted frame change are optimistically priced at
zero. An improved invoice cannot fix this failed identity. It does not exclude
lower-frame preprocessing, additional transported information, delayed
restoration after target reads, different copies, or a changed prefix.

| Helper | Full-isolation U | Lost target obligations at U | First restoration frame J | Rank J | Lost targets already at J |
|---:|---:|---:|---:|---:|---:|
| 465 | 512 | 10 | 507 | 4 | 1 (target122) |
| 466 | 514 | 10 | 508 | 4 | 1 (target208) |
| 468 | 513 | 10 | 509 | 4 | 1 (target144) |
| 469 | 517 | 10 | 517 | 7 | 10 |
| 470 | 513 | 10 | 186 | 2 | 0 |
| 476 | 514 | 9 | 514 | 7 | 9 |

J is the rational span of the restoration donors' current frames. Thus the
five exclusions at J also exclude every larger first restoration frame,
including unlisted rational frames. Helper470 instead uses J before U; its
source77 stays available at frame186. This is the evidence-driven refinement
of the initially tested one-common-frame mechanism, not a rerun with another
random seed.

The certificate contains all 666 target checks, the 59 nonzero U-cut rows,
exact rational separating normals, and six pairs of original inputs witnessing
failure. The ranks of the six restricted missing-dependency matrices are
`2,2,2,1,1,2`. These are scalar dependency ranks, not recursive COPY prices.
The common-frame restore/clear stars have 4,4,4,3,3,4 ADDs respectively and do
isolate their dirty inputs; their failure is geometric, not a scalar mismatch.
For helpers465/466/468 they would additionally force targets163/198/208 into
frames that cannot reach those targets' required final frames.

## Favorable complete slot relaxation, and its limit

A local rank reduction alone is not a supplier improvement. As a planning test,
move the width-seven residual from its old width-eight allocation into one
formerly idle rank-seven slot. In the old host, return the full eight freed
coordinates to an existing idle remainder r. For the incumbent occupied-slot
remainders `r in {2,4,6}`, all local children, freed idle rank and consumed idle
rank give the **two-slot relaxation**

`Delta H = e1 + e5 - 2 e7 + e_(r+8) - e_r`.

One `-e7` is the changed local path and the other is the consumed idle slot.
Both child count and rank mass are unchanged. The inherited child-count
surcharge would therefore be unchanged under this exact relaxation. At the
pinned bit exponent `a = 1733427039589844234749/10^24`, an exact rational
atanh/Taylor enclosure certifies a strictly negative change in
`sum H_r * r * (64/r)^a` for all three cases (approximately -0.0042490,
-0.0088265 and -0.0121653 per local conversion). The complete rational intervals
and profile deltas are in the certificate. No root search or new exponent is
claimed. This accounts for every child in the stated slot model; it does not
establish that these slots can be occupied in the real chronology.

**Unresolved:** an actual owner/window assignment for this endpoint, native
five/nine/eleven-stage compilation, packed precision and tape invoices, and a
replacement/adaptation of H4 (which currently requires literal full-frame
cleanup of every helper). The source still has the original H1/H2/H3/H5 scalar
shape; the changed endpoint is outside the selected H4 contract. The two-slot
calculation assumes successful admission and unchanged allowances and supplies
no proof of either. The complex supplier also remains limiting. None of this
selects a new frontier, a physical supplier, a practical speedup or a complete
multiplication theorem.

## Reproduce and verification coverage

Python standard library only. From the repository root:

```sh
python3 -I -O -B research/bit-early-retirement-cut/verify.py
python3 -I -O -B research/bit-early-retirement-cut/independent.py
python3 -I -O -B research/bit-early-retirement-cut/test_package.py
```

The first command ends with:

```text
PASS_BIT_EARLY_RETIREMENT_CUT helpers=6 lost=59 least_frame_survivor=470 width=8->7 ADDs=24305->24307 mass=5129->5128 no_new_kappa
```

`verify.py` uses packed binary rows and Fraction geometry; `independent.py`
uses set-valued rows, separate Gaussian inversion, and fraction-free integer
geometry. They share the authenticated source and declarative receipt, and
neither imports the other or predecessor executable code. The second checker
independently verifies the cut classification, input pairs, full construction,
frame paths and local invoice; the analytic slot intervals are certified by
the first checker. Separate implementations written with the same AI assistance
do not constitute independent human review.

Eleven test groups include all 22 star-gate omissions, three retirement-gate
omissions, both cleanup mistakes, premature source promotion, invalid final
frame, altered input/geometry witnesses, 60 small invertible-matrix fixtures,
the returned-idle accounting check, four receipt corruptions rejected by both
checkers, source corruption, and read-only offline relocation. Decimal values
are only a diagnostic cross-check of the rational intervals. Full-frame target
and smaller-first-frame controls explicitly guard against overstating the
negative result.

`--emit NEW_PATH` regenerates the complete canonical receipt and refuses to
overwrite a file. The registered hook in [VERIFY.json](VERIFY.json) runs the
three commands on Python3.12. Standalone replay also works from a source-only
export containing this package and its one declared input. Metadata provenance
checking additionally needs the pinned Git history.

No full `make verify`, selected cold replay, native supplier replay or Lean
compilation is claimed. This package changes no generator or selected input;
its focused checks cover the new evidence. Hosted CI status is separate from
local validation. The registered Python3.12 replay and all eleven test groups
passed locally; both checkers and all eleven groups also passed on CPython3.9.6.
Receipt regeneration on CPython3.14.6 was byte-identical. The selected-record
integrity check and all five selected-result tests passed. The final overlap
refresh covered 845 open PRs and 17 discussions, with complete pagination; it
found the explicitly credited neighboring work above. Refreshed main
`dadfea6e8a78ff6ba901705f87532a71c6f5bbb8` retains the exact input blob and the
same selected result.

## Open next questions

1. Can the rank-seven endpoint pass the native recursive and owner/window
   contracts? Start by emitting helper470's `0,79,186,513` path and checking an
   exact rank-seven idle window, including pending source access. A positive
   slot moment is useful only after the H4 and physical admission gaps close.
   Compare with PR1043 before investing: its helper deletion may remain better.
2. Can helpers465/466/468 be restored after their single blocking target read
   while retaining a favorable complete profile? Start with targets122/208/144
   respectively, recompute the inverse-row cut at the corresponding B boundary,
   then check every dirty column and subsequent target dependency. The present
   fixed-after-scatter theorem does not cover those later cuts. No search there
   was performed.

Structured next steps and the deliberate H2/K-to-H4 scope change are recorded
in [TASK.json](TASK.json).

## Attribution and source status

Ross Richardson prepared this contribution with substantial OpenAI Codex
assistance in mathematical reasoning, code, tests and writing. New material is
Apache-2.0, the repository license.

Credit DreamingOfClouds (PR589/545), eumemic (PR555/543 and the interleaved
interface), their retained E8/native supplier lineage, and Ali Romman
(PR1128's two-sided boundary conditions and PR1043's earlier helper470
source-deletion construction). Sagar Thakrar's PR1023 motivates width-seven
hosting. Hanson Sun's PR1079 independently identifies helper470 in the distinct
source-substitution class. Adam Gall's PR1179 changes a kernel entrance;
that mechanism is not imported or combined here. Frozen sources and their
original notices remain untouched.

Exact Git/SHA256 input and historical context pins are in [SOURCES.json](SOURCES.json).
Pending PRs are research predecessors, not accepted replacements for the
selected source. [CLAIM.md](CLAIM.md) records task choice and overlap coverage.
