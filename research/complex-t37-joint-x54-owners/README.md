# Joint entrances and X54 with 37-replica whole-owner packing

Conditional **κ = 0.001675608585476885**. This combines Thomas DiFiore's
PR1148 joint-entrance supplier, Jeremy Kothe's PR1130 X54 operation and
Rohan Arun's PR1169 integer-flow certificate on the retained PR1131 wave order.
It improves PR1148's admitted `0.001675560947524449` and PR1169's draft
joint-entrance T37 target `0.001675568675201533` at the preparation snapshot.

The X54 operation changes the local paid profile by `+2 H3 - 4 H4 + 2 H5`
while preserving all 480 helper widths. The final local profile is
`{1:2364,2:498,3:414,4:126,5:84,8:8}`. The normalized flow is expanded by
exact deterministic bipartite matching into **159,840 whole-helper owners**
for 333 calls. It leaves 834 rank-one and 11,374 rank-48 idle children.
Both exact moment engines and all 47 outer inequalities certify the claim.

## Reproduce

Python 3.11+, a C++17 compiler, Boost headers and the retained baseline's
NumPy/SymPy/SciPy requirements are needed. The owner constructor uses only
the standard library; verification does not run an owner optimizer.

```sh
python -m pip install -r research/e8-bit-p111-tuned/requirements.txt
CXX=g++ BOOST_INCLUDE=/usr/include python -B \
  research/complex-t37-joint-x54-owners/verify.py \
  --work /tmp/t37-joint-x54-fresh
```

Choose a new output directory outside the checkout. On Homebrew macOS use
`CXX=clang++ BOOST_INCLUDE=/opt/homebrew/include`. The driver freshly rebuilds
the retained PR589/741/799 ancestry, the k8 and seven-slot suppliers, the
complete PR1148 eight-end/T16 and joint-entrance admissions, and the final X54
supplier. It then normalizes the pinned flow, reconstructs owners, checks the
independent geometry and five-bank parent, and runs strict controller admission.
All source staging and input-package bytes are checked before and after.

The driver includes 32 eight-end and 27 joint-entrance rejection controls,
eight X54 negative controls, eight flow controls, six owner controls, eight
parent-lift controls, fifteen controller controls, 69 admission controls and
twelve bit-supplier controls, alongside the retained ancestral/supplier tests.
`RESULT.json` binds completed stages and manifests; `MATH.json` is the portable
mathematical receipt. `PRICE.json` records the two-engine signs, all outer
inequalities and the attained fixed-family ceiling over all positive replica counts.

## Result and scope

The complex profile is
`{1:788046,2:165834,3:137862,4:41958,5:27972,8:2664,48:11374}`.
There are 33,152 live families, 33,642 physical families and deficit 11,840.
The prefix is 775 bits within the charged 1,024-bit reserve; the physical-row
coefficient is 17,495, below the retained 20,161 limit.

This is a finite conditional construction. All-size compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
analytic transfer, the PR559 recurrence correction and bit H1–H5 hypotheses remain.
The fixed-family ceiling holds for this local paid profile, helper inventory,
source capacity stock and retained bit endpoint. It does not bound different
words, mixed providers, capacity families or recursion geometries.

See [PROOF.md](PROOF.md), [NOTICE.md](NOTICE.md), [SOURCE-PINS.json](SOURCE-PINS.json)
and [CLAIM.json](CLAIM.json). All package sources and data are manifest-bound.
