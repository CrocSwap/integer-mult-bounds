# Sources and credit

Ali Romman (@aliromman) prepared the new block schedule, exact bill, block
selector and checks with substantial OpenAI Codex assistance in research,
implementation, verification and writing. New material uses Apache-2.0.

C. H. Bennett supplied the classical reversible checkpoint method in
[Time/Space Trade-Offs for Reversible Computation](https://research.ibm.com/publications/timespace-trade-offs-for-reversible-computation).
This work applies that method to a particular sampler. It claims no new
general reversible-simulation theorem.

Ali Romman supplied the unchanged finite-window circuit, arithmetic and
ordered stopping contract in [PR #7773](https://github.com/CrocSwap/integer-mult-bounds/pull/7773).
Its [proof](https://github.com/aliromman/integer-mult-bounds/blob/c1fe18fbca499b50c3bbfb12e11218ee9b6acf01/research/inverse52-window-circuit/PROOF.md),
[gate operations](https://github.com/aliromman/integer-mult-bounds/blob/c1fe18fbca499b50c3bbfb12e11218ee9b6acf01/research/inverse52-window-circuit/window.py),
[checks](https://github.com/aliromman/integer-mult-bounds/blob/c1fe18fbca499b50c3bbfb12e11218ee9b6acf01/research/inverse52-window-circuit/verify.py)
and entire source package are retained byte for byte. The new checker reuses
its packed and scalar gate interpreters and arithmetic checks. It compares
the new circuit with both a residue-based reference and the old ordered source.

Nick Petalas (@petalas) supplied the underlying Boolean primitives in
[PR #7746](https://github.com/CrocSwap/integer-mult-bounds/pull/7746).
JoyboyBrian supplied the actual inverse residue domain in
[PR #6096](https://github.com/CrocSwap/integer-mult-bounds/pull/6096).
zxv supplied the ordered decision graph in
[PR #6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072).
Their exact source files and notices remain in the retained predecessor.
The [predecessor credits](https://github.com/aliromman/integer-mult-bounds/blob/c1fe18fbca499b50c3bbfb12e11218ee9b6acf01/research/inverse52-window-circuit/CREDITS.md)
give the full chain. None of their results is claimed as new here.

Tekalign's [PR #3122](https://github.com/CrocSwap/integer-mult-bounds/pull/3122)
and [PR #3129](https://github.com/CrocSwap/integer-mult-bounds/pull/3129)
apply checkpointing to batched lifting and price a different machine contract.
They are related repository work, not consumed code or a physical tariff
for this sampler. No runtime dependency or admission claim is transferred.
