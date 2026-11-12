# Verification scope and independent review

## Author proof and exact oracle

The author verifier executes the literal table through the unchanged sparse
CPU from #7349. Its separate integer oracle forms (1-i)^D by repeated Gaussian
multiplication, without reusing the production even/odd decomposition, then
performs one exact signed toward-zero quotient. It checks the entire public
and private tape maps and all head positions, not only returned numbers.

Normal and optimized, warning-strict standard-library executions pass. The
771 generic cases include 64 exact signed range endpoints; 515 are accepted,
256 reject at the explicit range sink. The suite records 5,125,983 literal
transitions. Twelve complete small C/S/H0 tensor cases cover 252 fields.
Six mutated programs are rejected. All seven frozen source files are bound
by length, SHA256 and Git blob. The immutable RESULT.json is regenerated
only with the explicit --write flag; normal replay writes no source/receipt.

## Separately written dense CPU and Gaussian oracle

The orchestrator independently wrote `independent/dense_check.py` without
executing the author CPU or verifier. It interprets the same emitted table on
dense arrays, uses a separately written direct Gaussian-integer (1-i)^D
oracle, and checks all public bytes, old-tail erasure, private cleanup and
translated origins. It passes 20 packet cases and 2,983,794 transitions,
covering all D residues modulo eight, complete 2^D rectangles, the most-
negative input, wider output, long skipped metadata and range rejection.
Three mutations fail: changed commit bits, omitted output retirement and
incorrect odd Gaussian rows. The exact receipt binds the generator SHA256.

```sh
python3 -I -B research/literal-layer-egress/independent/dense_check.py research/literal-layer-egress/egress.py
```

Long-r fixtures with short packets test the generalized numerical interface,
not an actual complete selected array. This is stated separately from the
complete small-layout tensor tests. The private universal cost proof rests
on literal loops, not measured finite counts or interpreted Python memory.

## Independent universal/source review

The separate research agent `crt_reusable_history` accepted the scoped
universal algebra, source binding, full 65536 instruction envelope and retained
backing bound. The complete review is `independent/UNIVERSAL-REVIEW.md`.
It required the coupled format-padding derivation now stated in PROOF section
1; no scientific-code change was needed. The review preserves the supplied
format conversion, complete source packet, private blank windows, C kernels
and phase interfaces.

Its independent algebra/source check executes 128 carry transitions, 174,752
signed rows, 4,106 range cases, powers 1 through 128, seven source pins and
four negative controls. It imports neither the author numerical verifier nor
a full-machine interpreter. Reproduce from the repository root:

```sh
python3 -I -W error -B research/literal-layer-egress/independent/algebra_source_check.py
```

Only this script's default path and receipt I/O were adapted for packaging;
its scientific algebra is unchanged. Default replay checks the committed
receipt without rewriting it. The dense script is retained unchanged.
These are separate AI reviews, not human or proof-kernel acceptance.
Scientific code remains bound to
`5875981b27bbb131a1e13ffca7f7eb920aa85b90699e6d40a85bd3902ff073e7`.
