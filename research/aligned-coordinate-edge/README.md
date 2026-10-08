# Adjacent coordinate refinement beyond PR93

**Conditional kappa = 13197734464639/250000000000000000 = 5.2790937858556e-5**.
This exceeds PR93's `13197726684911/250000000000000000 = 5.2790906739644e-5`
by **3.1118912e-11**, and PR91's `5.2789616935221e-5` by **1.320923335e-9**.
Bit saving and adjacent-grid controls are recorded as exact rational fractions
in `certificate.json`. This is a small finite improvement, not an asymptotic
breakthrough or measured practical speedup.

## Construction

Start with PR91's immutable physical words at
`264f202b52edc04d0c72ca9cb3138282ca68b9ad` and transport the following
zero-based coordinate labels consistently:

- h23: interchange **5 and 6**.
- h25: interchange **22 and 23**, and **5 and 6**.

The first h23 swap and the 22/23 h25 swap reproduce PR93's coordinate choices
at `c42039369af319a4ccc249b11efcfedecc2cc72f`. The additional h25 swap 5/6
provides the improvement over PR93. All swaps act on the already selected
PR91 coordinates, not on its original coordinate map. They are disjoint on
h25, so the resulting permutation is its own inverse.

The credited `aligned_composition_nodeops.relabel` action updates frame masks,
source triple indices, scatter rows and output targets. XOR operations,
physical slots and chronology do not change. The parent permutation
compatibility argument applies; only the fixed-I+J corner profile changes.

| Quantity | PR91 / PR93 | This witness |
|---|---:|---:|
| h23 / h25 roles | 26387 / 34772 | 26387 / 34772 |
| Physical width | 130417912 | 130417912 |
| Total recursive rank | 74988452500 | 74988452500 |
| Rank deficit | 1846900 | 1846900 |
| kappa (PR93) | 5.2790906739644e-5 | 5.2790937858556e-5 |

The saving comes from the **combined** complete paid child profile, not from
adding axis gains. Endpoint-copy, exterior-bank, data-growth and complex
transfer charges remain unchanged and paid.

## Reproduction and checks

```sh
python3 research/aligned-coordinate-edge/verify.py
(cd research/aligned-coordinate-edge && python3 -m unittest test_controls -v)
```

The verifier checks the local SHA256 closure and every file pinned by PR91's
source manifest. Both coordinate words are reconstructed deterministically
from the parent words and compared byte-for-byte after decompression. Full
ordinary/arbitrary-dirty physical replay in both orientations, independently
reconstructed XOR transitions, and fresh actual-frame C++ CRT profiles are
checked against both shipped profiles. CRT disagreements are zero.

The inherited rational search finds adjacent accepted/rejected 1e-18 saving
values. Two independent moment enclosures separate them. Balanced assembly
checks 47 strict inequalities, seven margins and next-grid kappa rejection.
Both PR91 and PR93 complete profiles are excluded at the new saving. PR93's
exact kappa is independently recovered from its supplied profiles before
comparison. The coarse 1e-11 grid result must also exceed PR93's fine-grid
kappa. `pr93-comparison.json` records the external commit, certificate digest
and supplied-profile digests; these profiles are arithmetic comparison inputs,
not a claim of independent PR93 producer regeneration.

Eleven controls cover invalid permutations, restoration of the parent under
the involution, unrelabelled sources/outputs, missing terminal operations,
aliased terminals, corrupted rank mass, exact parent arithmetic, exact PR93
arithmetic, next-grid rejection and source closure. Linux CI runs the same
interface on Python 3.11 and 3.14. Local verification used WSL Python 3.14 and
GCC; CI execution is reported separately.

## Discovery, attribution and limits

A first bounded neighborhood evaluated 19/20 proposals on PR91's axes. When
PR93 appeared with a better pair, a second neighborhood evaluated all adjacent
swaps plus rotations/reversal around its selected pair (27 h23, 29 h25
proposals). Discovery remapped transition frames; every accepted improving
candidate was materialized as a physical word, replayed, and required to
regenerate exactly the screened transition bytes. The earlier null-circuit
clearing experiments composed from PR89/PR75 did not improve the record in
four trials and are not part of this witness. No global optimum is claimed.

The PR91 producer is inherited, **not recompiled here**. Its finite words are
inputs whose full physical replay is performed. PR91's Lean companion proves
its own numbers, **not these new values**; the new bound is verified by two
rational Python enclosures, not a new Lean theorem. Analytic, all-size
framed/residual compiler, routing, recovery, prime-selection and fixed-tape
hypotheses remain inherited. No O(n sqrt(log n)) algorithm is established.

Credits: Chafik Boukhalfa's PR91/PR88/PR84 compiler; Thomas DiFiore's PR74
aligned partitions and coordinate action; Rohan Arun's PR93, PR78 and
PR65/PR67 coordinate refinement, arithmetic and pricing; all inherited
contributors, notices and Apache-2.0 licenses remain unchanged. Adjacent
coordinate search and additive verification by Maxime Fleury with Codebuff
(Buffy) assistance. No parent source or archive is modified.
