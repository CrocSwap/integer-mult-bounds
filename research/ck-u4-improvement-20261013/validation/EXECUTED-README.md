# Four additional CK cold ends

The exact conditional saving is **κ = 0.001636464689763295**, or
`327292937952659/200000000000000000`. This exceeds pinned PR639's
`0.001636461592777116` by `0.000000003096986179`; the conservative calculation
is `0.00163646468689307`.

PR637's four premix-only cold ends transfer to the CK supplier: raw helpers
233, 265, 425 and 441 now end at dimension 8. Its local profile becomes
`{1:2608,2:548,3:304,4:168,5:66,6:4,8:8}`. A literal packing derived from
PR638 consolidates the resulting slack into one dimension-40 idle row and
2,229 dimension-48 rows. Dispatch remains 71 JP8 / 1 CK, with CK at time 5,
stage 2, replica 0, forward orientation. All 35,424 roles have checked owners.

The constructor extracts PR637's 56 added premix gates and 20 added low-frame
tail gates by comparison with pinned PR635, transfers them to CK, then derives
an exact dyadic FULL-frame cleanup. Every previously ended row and column and
all four new ends remain isolated. `PROOF-CK-U4.md` describes this construction.
All 23 core verification files remain byte-identical to PR637.

**The final fresh end-to-end replay is pending.** Native frames, arbitrary dirt,
reflected local programs, independent replay, wrappers and all 3,110 CK phase
edges passed. All 51 CK raw controls, 114 global admission controls, physical
controller controls and both exact moment engines passed in discovery, using
previously audited JP8 and baseline artifacts. An independent Fraction/GF2 proof
and native-width/owner/rational check also passed. The parent README and
validation folder record subsequent fresh verification status.

Reproduce with Python 3.10 or newer, a C++ compiler and Boost headers:

```sh
PYTHON=python3 sh research/ck-u4-improvement-20261013/witness/verify.sh /tmp/ck-u4-improvement-fresh
```

The wrapper rebuilds the baseline, both suppliers and exact global certificate,
then runs independent native/owner/moment checks with five mutations, six U4
mutations for each supplier, declaration reconstruction, the owner exporter
with four mutations, and exact CK recipe reconstruction. Python admission uses
only the standard library; CP-SAT is needed only for historical owner search.

Chi Zhao prepared the CK transfer, packing and validation with substantial
OpenAI Codex assistance. Jeremy Kothe supplied PR637's CarrierBypass gates and
PR629's h4a lineage; Jeremy Diviney supplied PR627's factored ends;
DreamingOfClouds supplied the cold-end framework; Chafik Boukhalfa supplied the
PR626 rational interval engine; eumemic supplied the inherited PR543 bit
supplier. Original notices and licenses remain in `NOTICE.md`.

This is a conditional finite certificate. All-size compilation, common labels,
mutable-source realization, whole-call hosting, precision/tape/exact recovery,
analytic transfer and bit H1–H5 remain inherited premises. PR543 is repriced,
not rebuilt. No unconditional theorem, practical speedup or unrestricted global
optimality claim is made.
