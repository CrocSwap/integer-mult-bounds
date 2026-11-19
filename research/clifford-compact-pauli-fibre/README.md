# Joint compact contraction of all 256 Pauli coefficients

All 256 outputs of the four-qubit width-13 identity symplectic fibre can be evaluated together on a 104-bit affine-quadratic chart with **one Gauss sum in at most 48 variables and at most one accumulator update per Bell read**. Each of the 4,265 compiled reads contributes to one of 256 bins or vanishes. All bins use a common basis of quadratic phases on the eight singleton bits. Two sets of Walsh transforms recover the requested coefficients using at most 3,072 further complex additions/subtractions. These counts exclude chart preparation, binary linear algebra, phase evaluation and the fixed compiler. [Proof and resource model](PROOF.md) · [Consumer](fibre.py)

| Supplied observation | Exact result for the complete fibre |
|---|---|
| Affine-quadratic chart from the #5704 constructor | One shared Gauss scalar and one scan of the compiled list. Complex mixture coefficients retain their phase. |
| Full-support coupled phase mask from #7801, supplied as 104 bits | **104 symbol probes and 206 head moves**, both optimal. One mask witnesses that all 104 symbols are essential. |
| Arbitrary dense array with exact coordinate probes | Exactly **151 × 2⁵¹** probes. The sixteen X sectors have disjoint supports, each a translate of the scalar row from #7800. |

The previous compact contraction handled one identity coefficient and priced one active Walsh cell on a tape. The new procedure produces a full symplectic fibre and prices the entire output vector on the coupled-mask tape. A Gram application in #7809 operates across symplectic fibres and remains unpriced. The selected multiplication bound is unchanged. [Previous one-row contraction](https://github.com/apoursh/integer-mult-bounds/blob/9d15f66abc9ccf760ca5f7ea442adeb87b8f7115/research/clifford-chart-contraction/PROOF.md) · [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19756125)

## Reproduce

From the repository root use CPython 3.12 and the standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-compact-pauli-fibre
~~~

To evaluate a chart from a circuit, run `python3.12 -B research/clifford-compact-pauli-fibre/fibre.py input.json` with the #5704 JSON circuit format. The optional `initial` field selects a computational-basis input. The result contains 256 exact real/imaginary pairs in order $16x+z$ for $X^x Z^z$ and reports the internal support rank and operation counts. A circuit with an empty gate list gives the computational basis chart at its initial address.

The checks cover all nine possible singleton ranks, off-image inputs, complex phases, six one-hot Pauli columns, a different symplectic fibre, and dense address weights obtained directly from Bell corrections. A second checker evaluates the full 16-by-16 corrected matrix for each read on eleven rank-104 phase masks and compares every output. It also verifies the shared 104-neighbor access witness. [Sparse and dense controls](verify.py) · [Full-support controls](check_phase_masks.py)

## Open next questions

Can a batch of transported fibres share a partial Bell transform and a low-cost output layout? Begin with two distinct nonidentity actions, account for their different singleton corrections and fixed tables, and compare exact values on off-image charts. A complete application of the Gram matrix requires a proved composition across its whole coefficient domain and an observation producer supplying it.

## Credit

Ali Romman supplied the absolute-phase affine-quadratic signature and Gaussian contraction routines in #5704 and #5727, following the retained predecessor notices. The Bell compiler, coordinate support and earlier one-row contraction are from apoursh's #7800 and #7801, building on #7799 and the earlier Clifford work of Ali Romman, alephnan and Nick Petalas. The predecessor subtree is pinned to its source bytes. The shared singleton basis, sharp full-fibre access counts and verification were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. [Source pins](SOURCE-PINS.json) · [Upstream notices and license](predecessor/source/engine/source/)
