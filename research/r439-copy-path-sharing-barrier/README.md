# Restored sharing cannot reach the selected R439 word's copy path (no new kappa)

Assignment seed 42, structural decoder research. Base commit
`f567884aeb8851b6e794af1184119a3bfbe1e631` (origin/main); selected
conditional result #799 (X4, kappa 0.001661634653669567) with DreamingOfClouds'
#589 bit supplier, eumemic's #555 punctured R439 word (v = 111, R = 439).

The restored-temporary sharing mechanism of #708 (merged, R420 nine-total
suffix, 114 XORs) is priced against the selected R439 word along three
avenues, before any large implementation. All three fail, each for a
different recorded reason. No construction is proposed and no kappa is
claimed. No selected-frontier or supplier file is edited.

## Results

T. Decoder totals are vacuous. The nine retained totals (registers
472-480) read 27 sources across 18 late A gates (3 per total, plus 9
early single-source initializers). Pairwise source intersections are
empty, so oriented-pair sharing among totals has no positive pair.

D. The frame-zero D section is arithmetically rich but interface-blocked.
Exhaustive census over 430 non-retained helper operands: 184,470 oriented
pairs, 41,404 positive, best single-pair saving 65 (pair 277 -> 434); one
seed-42 greedy disjoint matching takes 205 pairs for 6,231 ADDs. That
figure is an arithmetic upper bound, not an achievable saving: the
unchanged interface lemma's H2 requires every D gate to write a target,
so any helper-writing preparation/restoration pair is rejected. Control
C1 exhibits this exactly (scalar operator preserved, H2 false). The only
H2-legal temps are target registers, and no target appears in any D
source set, so they save nothing (control C2, cost exactly +2).

A. Same-frame A groups are empty. Bounded greedy nomination (seed 42)
inside every same-frame multi-source A group totals 1 ADD at frame 506,
a D4 mini-node frame already covered by other work. Not pursued.

## Reproduce

Standard library only:

```sh
python research/r439-copy-path-sharing-barrier/verify.py
```

Expected final line:

```text
PASS_R439_COPY_PATH_SHARING_BARRIER totals_reads=27 d_positive=41404 d_best=65 a_sameframe=1 controls=3 no_new_kappa
```

The script pins the word and the unchanged checker (SOURCES.json), reruns
the full baseline H1-H5 check, recomputes all three censuses, runs the
three variant controls through the inherited checker, and compares the
full report byte for byte against CERTIFICATE.json. Run without `-O`.

| Control | Variant | Outcome through the unchanged checker |
|---|---|---|
| C1 | full helper-temp D wrap, best pair 277 -> 434 | complete replay passes, H2 false |
| C2 | target-temp D wrap (target 111, helper 434) | complete replay passes, H2 true, ADDs +2 |
| C3 | C1 without restoration | rejected at helper endpoints |

## Scope and obligations

Finite word-level evidence only. Inherits every assumption of the
selected review (all-size compiler, realization, hosting, precision/tape,
analytic transfer). The D figure prices source reads only; greedy
matchings are not optimal and A-group nomination covers one greedy pass
per group, so "no candidate found" is not an optimality theorem. R420 and
open PR #686 (frame-zero sharing there, different word and checker) are
outside this note's scope; whether R420's checker admits helper-writing
frame-zero gates is not examined here. Open R439 PRs (#728, #792, #843,
#844) mine mini-nodes, blocks and source sums, disjoint regions from the
copy path priced here.

## Attribution

Credit to eumemic (#543 R420 skeleton, #555 R439 word, xcheck lineage),
DreamingOfClouds (#589 tuning), Sagar Thakrar (#708 restored-sharing
mechanism reused as the priced hypothesis; #753/#754 open R420 work not
imported), mikhailramalho (open #686, credited as related frame-zero
work on a different word), and the assembly/review lineage of #741/#799.
Prepared with substantial AI assistance (via OpenCode); no
independent human review is claimed. Apache-2.0.
