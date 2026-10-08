# Translated partial-swap and phase frames: κ > 2^-18

The conditional final multiplication saving is

**κ = 5499/10^9 = 5.499 × 10^-6 > 2^-18**, in
`T(n) = O(n (log n)^(1−κ))` on the retained fixed finite-alphabet multitape model.
This exceeds both 2^-19 and 2^-18, but not 2^-17. It is an asymptotic exponent result.

The branch starts from upstream main `6e564879f51ae16f23d392e9e196c605f36d90df`, retaining PR10 and the complete text sources of [icekylinx's PR18](https://github.com/CrocSwap/integer-mult-bounds/pull/18), pinned at `f2ab41aebad47861caf6316282c1793e5513845e`. Every source hash recorded by PR18 matches. The new result is in this directory and `notes/translated-partial-*.tex`; the PR18 construction files remain unchanged.

## What changes

For every dedicated stage-two auxiliary in PR18's bit network, choose source frame `D_P0` and sink frame `D_(I−P0)`. Arbitrary dirty scratch is restored logically and the physical endpoint remains `D_I`. Nested projections give terminal residual `D_(I−P1+P0)`, of rank 32752, while the entrance becomes identity. The existing prescribed common basis supplies contiguous widths **23 and 32729**, replacing **575, 31625, 23 and 529**. Rank sum, role count, scalar circuit and all other edges are unchanged. The new bit moment supports **a_b=11/10^6**, with strict gap greater than 1.59e-8.

The independent complex network uses the **PR7/PR16 physical schedule**, without adding PR18's separate complex data-entrance movement. Source operator `C_D0` and sink operator `C_I C_D0` cancel the old entrance and give the exact terminal operator `C_(E-perp)`. Its explicit orthonormal basis includes all sign corrections; a zero-polarization argument and all 21952 coordinate checks prove the phase identity on the full binary address space. All actual physical edges and stage boundaries are counted directly. The complex saving is **a_c=18/10^6**, with strict moment gap greater than 6.66e-9.

The complex source change requires a new precision guard: path rank budget **22876**, maximum child rank **21924**, and `rho=2`. This gives **C1=19991/10000** at beta=1/1000. The former guard is not reused for this different circuit.

## Exact assembly

Take epsilon=1000000/2000011, c=1, beta=1/1000, delta=10^-16,
λ=1−a_b+10^-20 and λ′=1−a_b+2×10^-20. All 29 strict constraints and seven final margins pass exact rational arithmetic. The final absorption margin exceeds **9×10^-10**.

The complete written proof is [translated-partial-note.tex](../../notes/translated-partial-note.tex), with a [compiled PDF](../../artifacts/translated-partial-18-note.pdf). It includes the retained PR18 scalar construction and common-basis proof, the new endpoint and complex phase proofs, and the final assembly. The retained generic basis and analytic/tape arguments are written mathematical dependencies; this is not formal verification or external review.

## Reproduce

From the repository root:

```sh
python3 scripts/partial_swap_producer.py --work-dir build/translated-partial-producer --output research/translated-partial/producer-certificate.json
python3 research/translated-partial/bit_controls.py
python3 research/translated-partial/complex_physical.py
python3 research/translated-partial/complex_controls.py
python3 research/translated-partial/verify.py
python3 -m unittest discover -s tests
```

The producer was regenerated once from portable source for dimensions 25, 23 and 57, including scalar coefficients, carrier dependencies, positive frames and complete histograms. The same run reconstructed the retained h28 complex histogram. Already passing unchanged checks are reused by source hash; the stored report does not need to be regenerated for an arithmetic-only review. The new boundary and phase checks, and their exact rational certificates, are included separately.

## Attribution

**Zhihao Chen (jacklightChen)** contributed the new translated partial-swap endpoint and compatible corner, the operator-correct complex source translation, complete physical accounting and revised precision guard, and the assembled witness, with substantial **OpenAI Codex assistance**. The earlier **GPT-6 Astra** attribution is preserved as recorded; it does not identify the runtime model of this continuation.

This builds on **icekylinx's PR18** partial-swap network, selected binary producers and prescribed basis; **eumemic's PR13** source-frame idea (with Claude assistance); **Zhihao Chen's PR7 and PR16** finite network and nested-basis work; **icekylinx's PR10** batching and tape interfaces; and the preceding authors in NOTICE. Rohan Arun's PR14 independently supplies overlapping data-corner refinements. Their constructions are not claimed as new here.

Future research using these contributions should explicitly acknowledge **Zhihao Chen (jacklightChen)** and cite the relevant contribution, while crediting the other dependencies used. This request adds no license condition. No worldwide-first or exclusive priority claim is made.
