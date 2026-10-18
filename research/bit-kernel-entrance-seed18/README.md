# A kernel entrance gauge for the selected R439 bit word

**Finite bit frame-word construction; no new kappa or hosted supplier admission.**
Adam Gall (@adamgall), with substantial OpenAI Codex assistance. Apache-2.0.

The selected PR589 word has an explicit nonzero helper entrance after a change
of helper coordinates. Helper **444** starts at frame **79**, rather than zero;
helper 470 is its restored decoding donor. The final helper frame remains full,
so this helper's local residual width is **seven instead of eight**. All 661
arbitrary source, target and helper inputs have the same final scalar map.

The complete local ADD invoice falls **24,305 -> 24,252**, including both new
shears and every scatter addition. Nine COPY/ERASE pairs are unchanged. The
local paid profile changes only by **-H1**, from rank mass **5,129 to 5,128**.
This is a changed entrance contract, not a drop-in replacement for the selected
hosted supplier. No missing entrance conversion is priced as free.

## Reproduce

Python 3.10+ and the standard library, offline, from the repository root:

```sh
python3 -I -B research/bit-kernel-entrance-seed18/verify.py
python3 -I -O -B research/bit-kernel-entrance-seed18/test_package.py
```

Expected verifier marker:

```text
PASS_BIT_KERNEL_ENTRANCE supports=80 viable=1 columns=661 ADDs=24305->24252 local_mass=5129->5128 controls=6 no_new_kappa
```

`CERTIFICATE.json` contains all 80 supports, their exact rational common-frame
intersections, both pivot orientations, complete local profiles, positive-prefix
invoices and controls. `SOURCES.json` pins immutable input and credited
implementation conventions. The verifier imports no repository code, contacts
no network, and regenerates no selected artifacts. `--write-certificate` only
creates a missing certificate and refuses to overwrite one. The candidate is
the deterministic `construct()` transformation; its canonical full-word hash is
in the certificate rather than a redundant compressed copy.

## Question, scope, and novelty

Research base **c0e3631dc24e3c24a861f7d3d79e0608481cccec**, OS seed **18**
(bit-supplier track). The selected conditional result at that base is PR1094,
kappa 0.001672660197076918, with unchanged PR589 on PR555. The complex side
binds. The selected certificate, manifest, actual assembly, review, status
note and PR ledger were read before choosing this task.

Three candidates were compared:

1. PR589 z-program triangle rewriting: rejected as overlapping PR1127.
2. Restored helper mixing inside D: rejected as substantially overlapping
   PR686/733/742/967/1062/1122 and their semantic replacement proofs.
3. **Kernel entrance gauges**: chosen. Change the helper-basis hypothesis of
   PR1128 rather than repeating its fixed-basis boundary replay.

The bounded search covers every nonempty compensation-kernel support of size
at most four among all 439 helpers, then every rational common entrance frame
for each support. There are 4 weight-two, 22 weight-three and 54 weight-four
supports; no weight-one support. Exactly one has a nonzero intersection of
its helpers' first raw contact frames: **{444,470}**, the line of frame79.
Either member can be the pivot; the even seed selects 444. Both finite
orientations are checked. Supports of size five or more are not covered.

PR1043 (Ali Romman) and PR1079 (Hanson Sun) already construct/classify deletion
of helper470 using source77. This package does **not** claim a new deletable
helper or to beat that construction's bit bound. It keeps all 439 helpers and
uses a different boundary contract: a compensated nonzero entrance plus basis
restoration. Its new evidence is this finite width-seven witness and complete
sparse common-frame kernel census. PR1128 is not contradicted: it fixes the raw
helper basis and expressly leaves changed bases outside its scope. Prior Adam
Gall PR1098 and PR1114 are not reused.

Response-kernel entrance gauges themselves are prior work: PR254 constructs
132 pairs on PR249, and Chafik Boukhalfa's PR382 ports shared-donor kernels to
the earlier PR370 E8 bit word. The final 788-open-PR body refresh recovered
these older predecessors, which the initial recent-PR scan did not include.
This contribution transfers that credited mechanism to the selected PR589
word and adds the exact sparse-kernel/frame-intersection classification. It
does not claim invention of kernel entrances, nor reuse those predecessors'
hosting or precision admission.

## Exact boundary construction

Write z=(x,s), with source inputs x and dirty helper inputs s. The unchanged
raw A/scatter/B map has target output `y + x + K s`, and z output U z, with
no target-to-z edges. Original C is U inverse over F2. Original D adds K s at
frame zero. The equal columns are K[:,444] = K[:,470], each of weight 55.

Put p=444 and q=470, and let S act by `s_q <- s_q + s_p`. Then S inverse = S,
and K S has zero column p and otherwise agrees with K. Perform:

1. Start p at frame79. Other start frames are unchanged.
2. At frame zero add (K S)s to targets: remove the 55 reads of p from D.
   No remaining D gate reads p, so its nonzero entrance is legal.
3. At frame79 perform `q += p`, applying S before the raw word.
4. Execute unchanged A/scatter/B and original C.
5. At the full frame perform `q += p` again, restoring S s to s.

The target is `y + (K S)s + x + (K S)s = y+x`. Sources and helpers are restored
exactly. This argument is uniform in every input and uses no zero-dirt
assumption. Each new shear is self-inverse over F2. The complete C remains the
literal reverse, at full frame, of the new raw z-gates.

Both p and q had first raw contact at frame79. Advancing q earlier neither
adds a frame split nor changes a later path. Starting p there removes its
original rank-one advance. The final shear is at the existing full endpoint.
Scalar cost is -55+1+1=-53. No source access, copied total, restoration or
workspace is omitted. The existing single private copy register is still
allocated, copied and erased nine times.

The line is Q times (0,1,0,-1,1,0,1,0). The verifier checks nesting by rational
row reduction, not merely equality of catalogue IDs. Its bitset frame replay
and independent set-valued COPY/ERASE interpreter check all formal inputs in
both scalar orientations. Reversing the scalar stream is **not** a second
monotone physical inverse-frame compiler.

## Completeness of the sparse census

A single pivot entrance gauge with support J has incoming pivot dirt entering
the raw helper state as `sum_{j in J} e_j`. A frame-zero compensation prefix
cannot read that independent pivot input from a nonzero entrance. Hence K
annihilates this vector. This is a necessary condition, not a statement about
arbitrary later compensation or source-dependent basis changes.

In this class, all entrance decoding shears finish before unchanged raw A,
use one common nonzero frame E, and touch precisely J. Each helper subsequently
visits its original first raw contact frame F_j. Monotonicity requires E
contained in their intersection. Unlisted rational frames are allowed. The
intersection is the nullspace of the union of F_j's annihilators. Zero
intersection excludes the gauge even when scalar work is free.

All supports up to four are found by pair-syndrome collisions and checked by
separate increasing-triple/dictionary enumeration. Zero columns give weight
one; equal columns give weight two; a pair syndrome equal to a third column
gives weight three; two disjoint equal-syndrome pairs give weight four.
Canonical sets remove the three pair partitions of a four-support. The second
method tests every increasing triple against larger fourth-column indices;
it imports neither the first method's buckets nor its results.

The stopping rule is completion of this finite domain, not heuristic
convergence. The 79 geometry exclusions concern only this common-frame,
support-at-most-four entrance-gauge class.

## Complete-cost screen and remaining obligations

The local profile is `{1:1322,2:1342,3:79,4:44,5:102,6:11,7:19}`. All scalar
instructions, source reads, two shears, frame advances, nine copies and erasures
are included. Positive forward/reverse majorants and the inherited expressions
`64 F^3 B^2` and `2^18 F^5 B^4` are recomputed from the literal stream; the
certificate records exact integers and checks strict 104/192-bit ceilings.
These are finite sufficient coefficient envelopes, not fresh physical compiler
or fixed-tape precision admission.

**Do not reuse the frozen global profile.** The start frame and residual width
changed. Retaining a width-eight host and charging its unused axis as a
rank-one idle child gives +H1, cancelling the local -H1 exactly, before further
adapters. A complete improvement needs an admissible owner/window construction
using the rank-seven residual more efficiently and pricing its entrance chart,
accesses and displaced idle work. PR1023's hypothetical width-seven headroom
is motivation, not an admission receipt. No full host or outer assembly is
claimed. The selected bit side is nonbinding anyway.

The original checker assumes zero helper starts. This package states the
changed finite contract rather than changing or silencing that guard.
Selected-supplier H1-H5 admission, native 5/9/11-stage replay, supplier binding,
a new exponent and multiplication formalization are outside this contribution.
The inherited all-size/compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape and analytic assumptions remain open.

## Attribution and coordination

Credit DreamingOfClouds for PR589 and PR545/510 ancestry, eumemic for PR555/543
and the word/checker/interface lineage, Sagar Thakrar for PR1062's literal
positive-prefix invoice convention, Ali Romman for PR1128/1043, Hanson Sun for
PR1079, Dugongue for PR254's response-kernel entrance construction, and Chafik
Boukhalfa for PR382's E8 transfer and stage lineage. Immutable packages and notices are
untouched. Neither the basis-change identity nor kernel entrances are claimed
as a new general idea.

Authenticated GitHub reported no pinned coordination issues; scope was claimed
locally and sent to the parent research coordinator. Live open PR bodies were
checked before the claim and again before submission. This package is not
stacked on another round's unmerged work. See `VALIDATION.json` for exercised
checks, environment, overlap snapshot and limits. Separate code paths do not
imply independent human review.
