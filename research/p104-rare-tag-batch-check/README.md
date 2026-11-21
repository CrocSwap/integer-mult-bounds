# Scoped review: rare-tag RHS batches in the grouped Gaussian service

## Result and limits

The exact combinatorial and scheduling statement below is valid under the stated support, complete-field, common-page and current-value hypotheses. For one independently implemented finite example, the flagged schedule and a sequential whole-axis oracle agree on the complete 125-by-125 rational linear map. Stale-source and cross-support fault controls are detected. This checks one written step used in the analytic/precision path; it does **not** discharge any of #7830's five assumptions, prove #7846's full multiplication theorem, establish its tape running time, or produce a κ gain. The test does not execute #7830's astronomical compiler or the complete comparative replay.

## Source inventory and overlap

* [#7852](https://github.com/CrocSwap/integer-mult-bounds/pull/7852) at `41beda1d6435760dc99e38bd7e65f36798aad212` has a conditional P104 lower-bound toolkit; its Wall56/aggregate descent-plus-rise premise and other separately listed hypotheses are not resolved by this check. This work concerns an independent upper-construction consumer, and its conclusions do not imply either half of that wall.
* [#7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) at `87fbf4f7b35b0f18ab12b5767775a9a424cf0b15` is the exact comparator. Its [result](https://github.com/CrocSwap/integer-mult-bounds/blob/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier/RESULT.json) claims conditional κ ≥ `0.00387992803556` with 48 rational and 36 binary native calls. It explicitly retains `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. The relevant words are `7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48` and `d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d`.
* Open [#7846](https://github.com/CrocSwap/integer-mult-bounds/pull/7846) at `343f7b1817e26ad3f89d2ddad313b12741d53602` submits a written constructive discharge of all five for this price, with partial Lean checking; formal machine refinement and independent scientific review remain open. Its [obligations ledger](https://github.com/aliromman/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/OBLIGATIONS.md) lists the relevant claimed producers. Its [open question](https://github.com/aliromman/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/README.md) asks for review of paid-call field and shape in the compact router and grouped Gaussian core. Its [grouped Gaussian argument](https://github.com/aliromman/integer-mult-bounds/blob/343f7b1817e26ad3f89d2ddad313b12741d53602/research/mixed-rank-uniform-composition/GROUPED-GAUSSIAN.md) already states the rare-tag argument; the proof and executable check below are a bounded independent review, not a claim of priority for it.
* Open [#7849](https://github.com/CrocSwap/integer-mult-bounds/pull/7849) at `3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd` submits a different composite-axis Fourier outer construction while using #7846's native/ordinary realization; it does not make this particular check an independent validation of #7849. Targeted open-PR searches for `rare-tag`, grouped Gaussian, and RHS returned no separate exact rare-tag review; search is not an exhaustive proof of no overlap.

The source files copied beside this result were fetched at those immutable commits. `git hash-object` matches the GitHub blob identifiers: #7852 `README` `1d331673d591c677ace54bdabf82d0e38b380a91`; #7830 `RESULT` `da566a9558c46663b4f92f151dc67dddb1139e43`, `PROOF` `9bdf397a0c8477b6a0dc2bf39ea6ce8f78b794d2`; #7846 `GROUPED-GAUSSIAN` `11bdd1710eacf6bb9f3ec9d176d7866d95add57b`, `OBLIGATIONS` `49f4846f554dcb55b24c5348f3d3ee2e392d4465`, and `VERIFICATION` `1c5c7b677868a5282528ad442a85b934f40943d7`.

## Exact obligation and proof

Let the complete core be X=∏ᵢ Xᵢ, with |Xᵢ|=Lᵢ, and let Eᵢ⊂Xᵢ. An axis-i sparse operation acts on each full i-line with no matrix entry between Eᵢ and Xᵢ\Eᵢ, and is the identity on the latter. It may use dirty, correlated input values. For the price statement, lines batched together must use the same axis page. Write S(x)={i:xᵢ∈Eᵢ}, and process each x on its flagged axes in increasing original axis order.

For S⊂{1,…,m} and i∈S, a complete i-line in the S-class is determined by choosing, independently, xⱼ∈Eⱼ for j∈S\{i} and xⱼ∈Xⱼ\Eⱼ for j∉S. Thus its exact number of distinct lines is

`N(S,i) = ∏_{j≠i, j∈S}|Eⱼ| · ∏_{j≠i, j∉S}(Lⱼ−|Eⱼ|)`.

If `minᵢ(|Eᵢ|,Lᵢ−|Eᵢ|)≥W`, every nonempty such class contains at least `W^(m−1)` complete, disjoint RHS lines. Values need not be statistically or algebraically independent: distinct source/output records are enough for rectangular batching. Each sparse operation preserves every S-class. At visit j the j-th selected axis is the same throughout one S-class; on that class the preceding selected axes have already executed in their original order. Hence using **current** line values produces exactly the sequential sparse-axis word. Other S-classes are disjoint and may be interleaved. This is an algebraic/operational statement and does not bound numerical rounding or tape movement.

For a desired square width b, full batches follow only when `W^(m−1)≥b`. Given N≥b, write N=qb+r, 0≤r<b. Form q−1 batches of b and one of b+r. Its extra r columns can be padded in one additional square product and charged to the preceding b columns. No class is left with a lone short batch. In #7846, `m=Θ(p^z)` and `W=C₁ α⌈√p⌉`, while `b=Θ(W)`; both m and W grow, so the condition holds eventually. It is not true uniformly at small m: for m=2, L₁=L₂=4, E₁=E₂={0,1}, W=2 and S={1,2}, an axis has only two RHS lines; b=4 cannot be filled within that class.

Finally, every cell x is visited |S(x)| times; the exact total is `∑ᵢ |Eᵢ|∏ⱼ≠ᵢ Lⱼ`, which for Lᵢ=L and |Eᵢ|≤μL is at most `m μ L^m`. If an Eᵢ-line and a batch are tiled into b×b blocks and a square costs `O(b^(45/16))`, the elementary block arithmetic has amortized `O(b^(45/16−2)) = O(b^(13/16))` per selected cell, up to constants for padded last blocks. This arithmetic estimate assumes a common coefficient page and the claimed square-product implementation; it does not establish the separate routing, memory, precision, or page-construction bills.

## Executable check and controls

`rare_tag_check.py` uses a full 5×5×5 core, selected sizes `(2,3,2)`, three fixed invertible integer line maps and batch width 4. A complete-field direct oracle applies each axis sequentially. A separately written interpreter groups by full flag class and visit, partitions each into 4–7 RHS lines, then computes from the current field. It compares all 125 basis inputs and 15,625 output coefficients. There are 12 flag/axis groups, sizes 4–9, 75 line visits and 175 selected-cell visits. Exact arithmetic makes this equality valid for every rational or complex payload in this finite instance, including dirty and correlated values. It covers the line-batching algebra, not the actual Gaussian coefficients.

For a deterministic dirty vector, reading every stage from the original snapshot changes 56 outputs; inserting an unauthorized edge from outside E₀ into an E₀ output changes 25. A unit pulse at `(1,0,0)` in the illegal map reaches `(0,0,0)` across different flag classes. The explicit two-axis example above has two lines against width 4, and the batcher rejects it. These are deliberate violations of the hypotheses, not faults found in #7846.

Reproduce with Python 3.12 (the tests use explicit exceptions under optimization):

```sh
cd .
python3 -B rare_tag_check.py
python3 -BO rare_tag_check.py
```

The two outputs match byte for byte: [receipt.json](receipt.json) and [receipt-opt.json](receipt-opt.json). Script SHA-256 `3e9d19d07eb946c7851339db362afc939501c3c29371120e43d33d685ba12184`; receipt SHA-256 `22523e7e35871a40c4a8321b05ad80ae4064120b6b777d7acc405fb535f11de0`.

Remaining work includes proving that the actual generated Gaussian sparse pages meet the assumed per-class support/common-page contract, tracing the current values and complete original-layout restoration on the fixed tapes, validating the rectangular block and roundoff/precision bills, and independently reviewing the remaining native, erasure, compiler, precision and analytic steps. The claimed full discharge and any maintainer selection require their own complete evidence. Ali Romman and predecessor contributors supplied the construction and original rare-tag proof; this is a small independent Codex-assisted review and control.

## Open next questions

Bind the support condition and current-value route to the actual Gaussian pages.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
