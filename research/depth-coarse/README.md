# Exact depth-coarse family and adaptive recursion barrier

[The finite-family adaptive barrier](PROOF-BARRIER.md) proves that switching
among these 64 complete profiles cannot improve their best scalar recursion
power under the stated leaf-work and complete-tree accounting assumptions.
It includes exact root and balanced-assembly headroom bounds; it is a scoped
family theorem, not a lower bound for arbitrary multiplication machines.
[The local construction proof](PROOF.md) gives the disjoint-support grammar
and finite validity argument. An independent checker imports no package
arithmetic and rederives the complete profile, exact root, all 47 constraints,
seven margins and 63 competitor exclusions.

Concurrent [PR #79](https://github.com/CrocSwap/integer-mult-bounds/pull/79),
at `9a58e62cf9e8954a4dde3c9b1372d733c276a6d1`, reports the stronger conditional
κ = 5.1745625472866e-5 using a per-cell grammar, unit completion and carry
exchanges outside this family's frozen compiler.
[PR #80](https://github.com/CrocSwap/integer-mult-bounds/pull/80), at
`a9ed157ff106fd35557b5896197f66a1272f7f13`, reports κ = 5.1778825456819e-5.
These are submitted comparison values; this package establishes a bounded
family result and makes no priority or strongest-known-bound claim.

This adds a finite conditional witness by composing eumemic's PR69 coarse-column
factorization with Chafik Boukhalfa's PR71 anchored split/next-use compiler.
The depth grammar allows row factoring independently at the first three
internal weighted-exclusion construction levels, with columns below them.
All eight words at each axis have been physically checked; all 64 complete
profile combinations are compared exactly. The selected h=23 word is `rcr`
and h=25 word is `rrr`, in construction-level order.

The selected witness gives exact kappa
`5164326938841/10^17 = 5.164326938841e-5`. Its role counts are
27,309 / 35,798 and physical width is 134,355,558. Complete PR #71 and #75 profiles are
excluded at the new bit saving, using immutable comparison certificates.
See `certificate.json` for the accepted complete moment, all 47 assembly
inequalities, seven margins, next-grid rejection and arithmetic cutoffs.
Every other 63 finite-menu profile is strictly excluded at the selected saving.

From the repository root:

```
python3 research/depth-coarse/verify.py
python3 research/depth-coarse/verify.py --regenerate
python3 research/depth-coarse/verify.py --arithmetic-only
python3 research/depth-coarse/verify.py --menu-choice ccc
python3 research/depth-coarse/menu.py
python3 research/depth-coarse/independent.py
python3 -m unittest discover -s tests -p test_depth_coarse.py -v
```

Default verification independently binds every literal scatter port and exact
terminal inventory, replays every source/target/arbitrary dirty basis in both
orientations, reconstructs frame transitions, regenerates actual fixed-I+J/CRT
profiles and checks exact arithmetic. `--regenerate` additionally recompiles
the selected DAG/matching/reclamation word and compares decompressed bytes.
`CXX` can select a working C++17 compiler, as in inherited checks. Temporary
files and logs are outside scientific certificates.
`--menu-choice` regenerates both axes of any one menu word and compares their
canonical word hashes, full dirty/frame receipts and actual CRT profiles with
the frozen menu. The 16 recipe/profile receipts and hashes are shipped without
duplicating all 16 large words. The default arithmetic path verifies all 64
exact moment brackets, assemblies and strict nonwinner exclusions.

This package changes no root headline, notice, Makefile or historical witness.
It remains conditional on the inherited all-size framed-word/residual compiler,
finite-alphabet tape, analytic, routing, prime selection, precision and recovery
contracts. Arithmetic cutoffs are not a complete operational threshold. No
global optimum, unconditional theorem or practical speedup is asserted.

Prepared for Joseph Demarest with substantial OpenAI Codex assistance. Original
code is retained byte-for-byte with source hashes and contributor notices in
`vendor/`; root Apache-2.0 terms apply. PR69 supplies uniform column factoring;
PR71 supplies split/anchor/next-use composition; Rohan Arun PR65/67 supplies
schedules/profile costs/directed arithmetic; Dominik Scholz PR68 supplies live
controls; Rohan Garg PR59 supplies split operation; eumemic PR57 supplies joint
reversible compilation; Avi Eisenberg PR62 supplies interval/core-aware graph.
rfu08 PR64 supplies explicit literal-scatter verification precedent. Earlier
community, OpenAI and Harvey–van der Hoeven attribution remains in retained
notices. The contribution is the independently verified depth factoring
family, its exact optimum, and its scoped adaptive-recursion barrier.
