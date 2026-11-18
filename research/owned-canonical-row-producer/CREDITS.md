# Credit and exact sources

Ali Romman supplied the new row controller, complete ownership and cost proof,
two-path row verification and package, with substantial OpenAI Codex assistance
in research, implementation, verification and writing. Apache-2.0.

The consumed point service is Ali Romman's
[PR #7735](https://github.com/CrocSwap/integer-mult-bounds/pull/7735), head
`460eb0c026649b28ab3b00f45de136599d0570fa`. Its
[program](https://github.com/aliromman/integer-mult-bounds/blob/460eb0c026649b28ab3b00f45de136599d0570fa/research/linear-tape-rotation-switch/program.py),
[proof](https://github.com/aliromman/integer-mult-bounds/blob/460eb0c026649b28ab3b00f45de136599d0570fa/research/linear-tape-rotation-switch/PROOF.md),
loader, source pins and credits are retained unchanged. The graph constructor
is called directly. Every source instruction is preserved under relocation;
its two halts become jumps into the controller.

Jerry Chen supplied the builder, physical ABI, Tape operations and point
cleanup in [PR #7593](https://github.com/CrocSwap/integer-mult-bounds/pull/7593),
head `56335a406469fad85e88ff72820d506d8bea6f63`. His
[notice](https://github.com/CubeJerry/integer-mult-bounds/blob/56335a406469fad85e88ff72820d506d8bea6f63/research/literal-canonical-rotation-switch/NOTICE.md),
source files and license are retained. The dense row interpreter calls the
unchanged Tape operations; it does not alter the source fourteen-owner CPU.

Nick Petalas supplied the endpoint and child formulas in
[PR #7504](https://github.com/CrocSwap/integer-mult-bounds/pull/7504). The
[source proof](https://github.com/petalas/integer-mult-bounds/blob/7efb9a84277ec31abe2a934aeef8c8a70548aa5b/research/canonical-rotation-switch-query/PROOF.md)
is the mathematical predecessor. Ali Romman's closed descent in
[PR #7734](https://github.com/CrocSwap/integer-mult-bounds/pull/7734), head
`57bb6efed1be1dda9eb1a0f622ec2773bc8b0047`, supplies the retained wider oracle
and the point-service formula.

Cinna Davis supplied the canonical compiler and padded rotation in
[PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100), head
`337d04939571a637aeab54a0f58f54fde811663a`. The unchanged
[compiler](https://github.com/CrocSwap/integer-mult-bounds/blob/337d04939571a637aeab54a0f58f54fde811663a/research/unconditional-batched-crt/check_batched_crt.py)
and original notice supply the independent finite canonical-table oracle.

Ali Romman's [PR #7740](https://github.com/CrocSwap/integer-mult-bounds/pull/7740),
head `913d61fd9bd5d3d65a11c04f1baf50fc24ceb858`, supplies the retained
[three-rectangle proof](https://github.com/aliromman/integer-mult-bounds/blob/913d61fd9bd5d3d65a11c04f1baf50fc24ceb858/research/rotation-row-rectangles/PROOF.md)
and the physical row-producer question. Its sharper arithmetic stream is
related work, not an algorithm called by this row graph.

JoyboyBrian's [PR #5092](https://github.com/CrocSwap/integer-mult-bounds/pull/5092)
supplies a complete generic all-layer producer and fixed key-service join.
Its [contract](https://github.com/JoyboyBrian/integer-mult-bounds/blob/af3030a82d22cb1d897d891eb872e927dc322db3/research/crt-encoded-benes-rom-producer/README.md)
credits ToikY's arena lowering and the retained CRT lineage. It is related
work with a different workload, not an imported or replayed dependency.

All eighteen retained files have exact byte pins. The base manifest records
canonical provenance only; no unmerged dependency ancestry is asserted.
