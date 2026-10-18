# Two additive cyclic filters, no borrowed data array

This replaces PR929's four-call product and one dirty connector with **two
additive stable filters and zero borrowed length-L data arrays**. Each call
restores the source bit for bit. Reversing the calls and signs restores the
target exactly, including arbitrary nonzero lowest working bits.

The inverse is split into its nonnegative and strictly negative Laurent
parts. Their disjoint coefficient supports bound both numerator norms by
the full inverse Wiener norm. A grouped Bezout solve computes the two
numerators without separating repeated roots inside either group. Each
stable filter evaluates its numerator using the causal source and a short
homogeneous-state history, including the initially negative indices.

Polynomial, scalar, numerator, phase-window, gauge and matrix preparation
all have explicit rounding budgets. Exact fraction-free solves are charged
at their wider intermediate precision. [PROOF.md](PROOF.md) gives the
all-length error and restoration argument and the all-size cubic budgets.

For prime-power r>=3, target precision p, incoming grid w, and source/target
component norm |Re|+|Im| bounded by 2^m, put

    A = max(p,w) + 2m + 64r^3.

With exactly supplied rational unit phases of bit size at most B_phi, the
neighboring-cycle bill is

    soft-O(rL*(A+B_phi) + r^3 log L*(A+log L) + r^4*(A+log L)).

Working fractional precision is at most max(p,w)+12r^3. Clean scalar
workspace is O(r^3(A+log L+log r)) bits, additional to source and target.
It can exceed a length-L array for short cycles. Zero borrowed data arrays
does not mean zero clean workspace, a bit-reversible implementation, or an
unconditional runtime improvement. The Python reference does not claim
measured soft-O integer-arithmetic performance.

## Replay and evidence

Python 3.11+, standard library only, offline:

```sh
python3 -I -O -B research/additive-cyclic-no-connector/verify.py
python3 -I -O -B research/additive-cyclic-no-connector/test_package.py
```

The main marker is `PASS_ADDITIVE_CYCLIC_NO_CONNECTOR`. Default verification
checks the complete file manifest, all 19 retained source SHA256/Git blobs,
module locations and every field of the recomputed mathematical receipt.
`--out /absolute/new/result.json` writes a fresh external receipt only after
comparison; `--bindings-only` checks source bindings. `--write` is an explicit
authoring mode, not an admission check. The expected receipt is compressed;
mathematical comparisons use its decompressed content.

Evidence covers 140 bounded complex cases, 48 original-kernel cases using
all ten pinned fixtures through radix 16, 16 actual uniform-budget executions
at radices 3/4/5/7, 12 additional edge cases, 2,322 integer budgets and eight
exact nonnegative polynomial identities. All original-kernel cases meet the
128-bit target with coefficient preparation charged. Tests include repeated
and zero inside roots, empty groups, both directions, L<k, degree loss after
rounding and nonzero rounding in every newly prepared component.

Separate dense rational oracles check the original factor map. All 140
bounded cases also compare normal execution with the audit path exactly.
Three boundary/precision defect families, 18 additional rejections and 3,005
direct-width boundary checks are included. Finite execution evidence and the
written universal argument are distinct; neither is independent human review
or proof-assistant verification of a multiplication theorem.

## Scope and sources

Prepared roots and unit phases are immutable and distinct from mutable data.
The common Wiener bound is a certified premise; the kernel bridge verifies
its complete-polynomial hypotheses before using it. Arbitrary-stride tape
routing, irrational phase preparation, scalar-space hosting, common-label/
Clifford realization and the full multiplication reduction remain separate.
**No new kappa.** Selected certificates and `upstream/` are unchanged.

Credit Ali Romman for PR621's kernel and inverse bound, Chafik Boukhalfa for
PR628/862/905/929's restoration and precision development, and the classical
partial-fraction, Wiener/Laurent, companion-state and Bareiss methods.
Consumed sources and notices are retained unchanged and pinned in
[SOURCE-PINS.json](SOURCE-PINS.json). See [NOTICE.md](NOTICE.md).
