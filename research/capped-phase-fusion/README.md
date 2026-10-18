# Capped phase-cell fusion: conditional final kappa = 0.001677160151714381

This package gives the conditional final integer-multiplication bound

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{1677160151714381}{10^{18}}=0.001677160151714381.
\]

The contribution changes the **outer Gaussian resampling reduction**. It uses
shallow in-place Toeplitz circuits, a common Hadamard schedule for multiple
axes, recentered and capped Gaussian cells, and explicitly charged sparse
boundary operations. The finite supplier is the unchanged, pinned
[PR1661](https://github.com/CrocSwap/integer-mult-bounds/pull/1661) T74 construction.
Its complete native verification was run afresh, including both new provider
words and the retained parent. The final exponent is a conditional theorem
from the written transfer argument; finite checks alone do not prove it.

Read [the proof](phase_fusion_note.tex), especially its T74 substitution section,
and the [independent substitution review](frontier_fusion/INDEPENDENT-SUBSTITUTION-REVIEW.md).
The proof's earlier numerical specializations remain valid historical cases.
“Independent” in this package means separate agent implementations/reviews,
not an independent human referee or a proof-assistant verification.

The [14 October review response](review20261014/REVIEW-RESPONSE.md) addresses the inherited supplier admission and the outer proof separately. It includes a complete written outer review, pinned external checks reused from PR2044, fresh semantic regeneration and mutation controls on our actual supplier, and the corrected mixed-rank recurrence. The bound is unchanged.

## Exact paid inputs and result

| Quantity | Value |
|---|---:|
| Retained bit saving c | 0.001733427039589844234749 |
| Chosen complex saving b | 0.00167971337478 |
| Effective tensor saving q | b - 10^-10 |
| Effective bit saving a | (q+b)/2 |
| Native dimension m | 73 |
| Native live width W | 66304 |
| Final kappa | 0.001677160151714381 |

The complete native profile is
`{1:1559766, 2:337668, 3:278058, 4:84912, 5:54612, 8:5328, 48:22748}`.
All decimals above are exact rationals. Exact epsilon, xi, beta, every outer
cost power and all 45 strict inequalities are in
[FRONTIER-FUSION-ARITHMETIC.json](frontier_fusion/FRONTIER-FUSION-ARITHMETIC.json).
Five deliberate bad variants reject. The native moment has an outward rational
upper bound below one; a larger test endpoint is rejected.

For the same pinned supplier, PR1661's original outer reduction gives
0.0016768966690212993077507..., so the new outer transfer improves its final
exponent by about 2.6348269308e-7. This is an exponent comparison, not a measured
runtime improvement or a claim of global priority. The selected-result record
is not changed by this contribution.

The supplementary branch gives 0.001677600129305161 **only with the additional
assumption omega_C <= 9/4**, used through a fixed algebraic algorithm of exponent
19/8. That extra premise is not needed for the headline Strassen-based result.
The supplied 9/4 paper, its audit and historical local locator are recorded in
PROOF-AND-COVERAGE.md and MATRIX-SOURCE-COVERAGE.json; it is treated as an explicit
additional premise, not as a theorem certified by this package.

## Scope and remaining assumptions

Retained assumptions include the all-size compiler, exact common-label and
mutable-source realization, whole-call hosting, the semantic precision guard
with C1=1, fixed-tape/prime-packing interfaces, paid arbitrary-width equal-chunk
interchange, exact recovery, and the original analytic transfer. The construction
does not prove an unconditional multiplication theorem, a complete Lean theorem,
or a practical finite cutoff. The written proofs address the new outer steps;
finite algebra and layout checks support, but do not replace, those arguments.

Original assignment: improve the bound using broad mathematical resources.
For repository indexing this is a changed scope of `uniform-transfer-audit`:
it constructs and audits a replacement outer transfer rather than only checking
one inherited implication. [TASK.json](TASK.json) records the scope and next steps.

## Reproduce

Python 3.12, with SymPy 1.14.0, is the registered environment. The exact checks
also ran locally with the Python version recorded in PUBLICATION-CHECKS.json.
The package verifier checks its manifest and source pins, works in a temporary
copy, and compares the regenerated mathematical receipts. It does not modify
this directory. From the repository root:

```sh
python3 -m pip install sympy==1.14.0
python3 -B research/capped-phase-fusion/verify.py
python3 scripts/research_package.py --package research/capped-phase-fusion --check-only
```

The first command after installation is the bounded outer-proof evidence replay,
not a cold native-supplier replay. The native run already completed with all 12
top-level stages passing, 319680 owners, prefix 1441 charged at 2048, physical row
coefficient 19545 below 20161, and rejected controls: 114 admission, 12 bit,
23 controller, 8 independent owner, 6 geometry. The historical compact RESULT
and binding incorrectly label the controller count as 15; the actual controller
audit rejects 23 distinct mutations (7 global plus 8 for each of 2 providers).
The historical bytes are preserved; the new supplement records the correction.
The retained compact RESULT
and [native binding](frontier_fusion/NATIVE-ADMISSION-BINDING.json) record it.

To reproduce the full native dependency, obtain the exact source commit
`f852af5e178ce035cd46181a29d9330bcbcaa206` from CrocSwap/integer-mult-bounds,
install its documented dependencies (NumPy, SciPy, SymPy, a C++17 compiler and
Boost headers), and run its unmodified command without cache/reuse flags:

```sh
python3 -B /absolute/pr1661/research/gmx-t74-p566-ep400/verify.py \
  --work /absolute/new-native-work --audit-shards 4
python3 -B research/capped-phase-fusion/verify.py \
  --native-source /absolute/pr1661/research/gmx-t74-p566-ep400 \
  --native-work /absolute/new-native-work
```

After the second command, replay the new admission supplement on the same completed run:

```sh
python3 -B research/capped-phase-fusion/review20261014/native_validation.py \
  --native-source /absolute/pr1661/research/gmx-t74-p566-ep400 \
  --native-work /absolute/new-native-work \
  --output /absolute/new-native-supplement.json
```

The package verifier binds a completed external native run to this package's
source and mathematical result. It compares regenerated proof-relevant content;
fresh timings and log bytes need not match the historical run. The full 121 MB
assembly and vendor tree are not duplicated here. The receipt capsule adds canonical hashes for 46 JSON receipts. The 58 hashes
in the historical native binding identify external run artifacts; they are not all bundled files.
The original bind_native_admission.py is retained as historical provenance;
use the new top-level verifier for portable binding.

PACKAGE-MANIFEST.json is the authoritative publication manifest. MANIFEST.json,
MANIFEST-UPDATE.json and earlier review receipts are explicitly historical
snapshots. The copied upstream CLAIM.json is immutable and contains older pending
language; the later completed native RESULT records this contribution's replay.
Hosted CI and independent human review are separate from the local checks.

## Sources and overlap

Prepared by **Vlado Vojdanovski with substantial AI assistance**. New material is
Apache-2.0. The original manuscript and source-specific notices retain their
licenses. This is not an official OpenAI release or endorsement.

The main research snapshot was `e6f9716621f4e01fc190617934cdfaf072bd976f`;
the publication base is recorded in SOURCES.json. Exact T74 source pins are in
PUBLICATION-SOURCES.json and the source manifest.
The [unaltered T74 NOTICE](target002_upstream/pr1661/research/gmx-t74-p566-ep400/NOTICE)
is included. The original
OpenAI #109 framework and the Harvey–van der Hoeven reduction remain inputs.

The in-place algebra builds on Giorgi–Grenet–Roche,
[*Fast In-place Algorithms for Polynomial Operations*](https://arxiv.org/abs/2002.10304),
and Dumas–Grenet, [*Fast in-place accumulation*](https://arxiv.org/abs/2302.13600).
SHALLOW-TOEPLITZ.md distinguishes their results from the new parity-split,
low-displacement and prefix-stability arguments. The Gaussian factorization
also relates to
[PR489](https://github.com/CrocSwap/integer-mult-bounds/pull/489), which already
gives a branch-free local Gaussian inverse but leaves joint evaluation,
routing and boundary composition open. The present package supplies a different
in-place tensor compiler and capped boundary transfer for those outer costs.
[PR1141](https://github.com/CrocSwap/integer-mult-bounds/pull/1141) concerns a
reversible quadratic phase stream and is related background, not a dependency.
The overlap check does not establish novelty beyond these identified sources.

## Open next questions

1. Can a new finite supplier exceed the present complex rate by a substantial
   amount? Even a lossless outer transfer cannot reach 0.002 from b<0.00168.
   First step: emit a complete side circuit for a lower-cost decoder and measure
   its actual rank profile, helper storage and restoration. The missing piece is
   the physical circuit, not an idealized central-rank estimate.
2. Can the capped Gaussian transfer be independently checked or formalized with
   its complete fixed-tape schedule? First step: independently reconstruct the
   sparse-union and support-local routing lemmas. Existing finite tests cover
   algebraic identities, not an end-to-end all-size tape implementation.
3. Can the same outer transfer consume a future reviewed supplier without
   changing its proof? First step: rebind the endpoint, prefix and completed-call
   restoration contract, then replay the exact ledger. The supplier must satisfy
   the full functional interface; a numerical endpoint alone is insufficient.
