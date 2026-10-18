# Three owner exchanges after PR638

The exact conditional saving is **κ = 0.001636461592777116**, or
`409115398194279/250000000000000000`. This exceeds pinned PR638's
`0.001636456810414854` by `0.000000004782362262`; the conservative calculation
is `0.001636461589906939`.

Three literal exchanges consolidate idle dimensions 35 and 1 into one
idle dimension 36. The 2,229 idle dimension-48 rows remain unchanged. Ten
serialized rows differ after offsets are compacted. Both native suppliers,
all construction recipes, 23 core verification files and the 71 JP8 / 1 CK
dispatch remain unchanged from PR637. CK is at time 5, stage 2, replica 0,
forward orientation. All 35,424 roles retain valid physical owners and intervals.

**The final fresh end-to-end replay is pending.** Discovery rebuilt the bound
controller, all 23 controller mutations, invoice and both exact moment engines
using previously audited native suppliers. All 114 admission controls passed,
as did the separate native-width/owner/rational checker. These checks are not
represented as a completed fresh replay. The parent README and validation
folder record subsequent execution status.

Reproduce with Python 3.10 or newer, a C++ compiler and Boost headers:

```sh
PYTHON=python3 sh research/pr638-improvement-20261013/witness638/verify.sh /tmp/pr638-improvement-fresh
```

The wrapper rebuilds the baseline and both native chains, checks frames,
arbitrary dirt, exact phases, physical ownership, invoice and outer inequalities.
It then runs the independent native/owner/rational checker and five mutations,
declaration reconstruction, literal row-patch and three-exchange exporters,
four exporter mutations, and the independent PR637 U4 proof with six mutations.
The admission checks use Python's standard library. Solver dependencies are
needed only for historical search reproduction.

`PROVENANCE.json` records source pins and unchanged core files. `owner-search/`
contains both exact owner reconstruction methods. `README-UPSTREAM.md` preserves
the inherited construction explanation, not the new owner result. All six
external source packages are vendored. The parent proof states any optimality
conclusion only for its explicit fixed packing inputs.

Chi Zhao prepared the exchanges and validation with substantial OpenAI Codex
assistance. Jeremy Kothe supplied PR637's CarrierBypass native construction;
Jeremy Diviney supplied PR627's factored ends; Jeremy Kothe supplied PR629's
h4a lineage; DreamingOfClouds supplied the cold-end framework; Chafik Boukhalfa
supplied the PR626 interval engine; eumemic supplied the inherited PR543 bit
supplier. Original notices and licenses remain in `NOTICE.md`.

This is a conditional finite certificate. All-size compilation, common labels,
mutable-source realization, whole-call hosting, precision/tape/exact recovery,
analytic transfer and bit H1–H5 remain inherited premises. PR543 is repriced,
not rebuilt. No unconditional theorem, practical speedup or unrestricted global
optimality claim is made.
