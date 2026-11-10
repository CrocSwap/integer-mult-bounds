## Problem and result

The current public fine-family Gaussian interfaces return normalized common-grid
fields. Keeping that normalization across two forward transforms, one pointwise
product and one opposite transform accumulates **3Gamma**. The old Sandwich
recovery restores only the radix factor after two S multiplications because
its Tensor already restores Gamma on each call; it cannot consume this changed
channel unchanged.

This package gives a source-first sufficient precision allocation and actual
native scalar/codec/carrier/recovery endpoints for the normalized channel.
For S<2^b, set a=2ceil(log2S)+2b+7, assign each public stage restored allowance
2^-(a+2Gamma+2), and take q>=a+3Gamma+7 plus its actual source/ledger guards.
The compression-only substitution is gamma_c=K_c and
tau_comp=tau+K_f, so its z uses tau+Gamma explicitly.

All reached scalar inputs pass the half-disk guard, the rounded pointwise
product fits the opposite call's quarter-disk, and the final real error after
S²2^(2b+4+3Gamma) is strictly below 1/4, including Gamma=0. Recovery width
W=q+3Gamma+4b+6 covers the complete two-S products and pre-drop shifted
numerator. Encoded S<2^b is checked. The actual public q+3 external carrier
is converted exactly through the retained zero-drop codec and the new guarded
native q+3-to-q+2 carrier. No fractional bit is silently discarded.

## Novelty and dependencies

CrocSwap/integer-mult-bounds#4320 already proves the exact Poisson/source
identity, both Fourier signs, R cancellation and S² recovery; #4415 supplies
the generic one-M ledger. Those are credited and not republished. The new
obligation is the actual normalized return/grid/source allocation and its
paid native deferred recovery. The old Catalogue guards are not waived.

Canonical base: 7c49fe32c55de02c2c873655c804b16e4c3fef0a.
Public dependency pins: expansion ceb3947872f996789072e37a56c0758c7720b844;
middle 8db3cc1e98ba295cec4d752478431515e159c34f;
Reference join 4509310a9a58d4c41c74029f899cbf36be1af9a1;
ledger 76a84e1c4bfa4035e5ee85410dbfc4541f0da168;
diagonal b00d64b6204e83d468dde2db7480a2822e6940aa;
codec 73d5adaba2b7dc662e86eb901e81369a3f73be9f.
Complete files are bound in SOURCES.json and DEPENDENCIES.json.

## Verification

```sh
python3 -B scripts/research_package.py --package research/deferred-gaussian-recovery
python3 -B scripts/check_research_commit.py --package research/deferred-gaussian-recovery --check-modes
```

Normal and optimized checks authenticate 11 canonical/eight public files,
check 405 exact rational allocations/widths/source-order cases, and execute
real native S5 endpoints at Gamma0/q26/W44 and Gamma2/q32/W56. Both recover
[28,38,51,32,5]. The zero-Gamma endpoint on the deferred Gamma2 return gives
[0,1,1,0,0], distinguishing the missing scale. Actual wide-codec/carrier,
conjugation, complex product/drop, strict nearest recovery, borrowed origins,
pending output, extent, radius and alias controls pass. A corrected test-only
external-tape observer attribute failure is preserved in the checkpoint;
production code and inherited source were not changed for that correction.

## Limits and full costs

The new endpoint pays 10S scalar products for pointwise validation/product,
4S for recovery, and 2S per guarded carrier pass, plus all complete scans,
metadata, sign conversion, width, cleanup and historical backing. Its total
is O(S M_word(W)+SW+poly(q+Gamma+b+logS)) under the retained scalar contract.
All three production transforms, full padded T-field extraction to original
S order, CRT and carry/output are separate paid prerequisites, unexecuted
here. Every middle still includes its full three Fourier calls and source
bill. The currently admitted direct expansion is already too slow for a
new positive-kappa complete result.

**No new kappa; no complete physical multiplier or unconditional theorem.**
This supplies one conditional analytic_recovery interface and preserves all
five foundational assumptions and the selected frontier. It does not
implement broad Core or claim a new generic error/Poisson theorem.

Prepared for **@CubeJerry** with substantial OpenAI assistance. Credit Cinna
Davis, Ryanson Jonathan, Jose Manuel/@jmbarrancoml and all retained scalar,
native, Gaussian and CRT contributors in NOTICE.md. Same-team lead review
and finite independent algorithms do not imply human/proof-kernel acceptance.
