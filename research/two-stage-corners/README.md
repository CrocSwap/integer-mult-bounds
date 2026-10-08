# Two certified data-corner blocks

The conditional saving is **κ=15878574/10^12=1.5878574×10^-5 >2^-16**, about **2.205% above PR29's1.5536×10^-5**. In its fixed (55,53) basis, the interstage data profile improves from107 singletons +2701 to **11 singletons +51,45,2701**.

Read the [proof](../../notes/two-stage-corners-note.tex), [PDF](../../artifacts/two-stage-corners-note.pdf), [detailed argument](a5-residual-two-stage-proof.txt), [exact certificate](certificate.json), and [validation receipt](validation.json). The new method certifies2265 augmented-minor zeros by **weight-independent rank-partition identities**. All4530 ranks are checked by exact integer elimination. A normalized rational witness establishes107 nonzero prefix pivots; the retained GL-family argument makes the conditions available simultaneously. These identities are stronger evidence than sampled zeros, while remaining conditional on the written inherited theorem.

The51-block occupies rows1..51 and physical columns2863..2913; the45-block occupies rows58..102 and columns2812..2856. Both are disjoint from middle107..2807. No gather or basis reordering is required. The histogram removes192N singleton calls and adds2N children of each width51 and45. The paid N endpoint-copy corrections remain, as do every producer, source/terminal frame, role volume, total rank mass and maximum child width. The entire finite semantic bridge is unchanged, including joint row degree47000.

```sh
make two-stage-corners-certificate two-stage-corners-patch
python3 -m unittest discover -s tests -p 'test_two_stage_corners.py'
make two-stage-corners-identities
make two-stage-corners-note
make verify
```

`independent.py` reconstructs every required augmented minor, checks all partition ranks directly, and reproduces the normalized rational pivot values. The optional identity target regenerates the search-derived certificates too. `witness.py` validates live pinned parent sources, runs PR29's exact checks and changes only the stated data profile and parameterized assembly. Generic inherited module names are isolated from the new arithmetic modules. Fresh unchanged producer replay remains part of full `make verify`; its completion is reported separately in validation.json.

The focused source patch applies to PR29 commit9d963275075fa98f1da821e27757b238dafd6b3c, not original OpenAI upstream. The next bit grid failure only says this sufficient upper enclosure does not certify it; no global optimum is claimed.

New corner-identity method, proofs, exact certificates and refinement: Rohan Arun with substantial OpenAI Codex assistance. Retained unequal two-stage composition: Zhihao Chen PR29; topology and paid copy correction: Paureel; retained-total producers and prescribed bases: icekylinx; two-stage development route: Swapnil Jain; semantic composition: Zhihao Chen PR23 inheriting RaD/PR20; source-frame contributions: eumemic; all prior NOTICE attributions remain. All inherited analytic, uniformity, exact-recovery and fixed-tape assumptions remain.
