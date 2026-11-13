# Draft PR title

Prove exact outward norm slack from affine periods and classify the conserved-sum Gaussian pair family

## Draft description

This scoped research package proves an exact outward-slack identity for
rational orthogonal integer maps with a full-rank affine period. It also
proves the identity fiberwise for every legal bounded center rule in Ali
Romman's #6509 sum-preserving Gaussian pair family, even though the retained
sign-based rule is not globally affine-periodic. The minimum family slack is
one, and the `c(1)=1` ray has the explicit gap bounds in `PROOF.md`.

The note applies the same lemma to inherited source results: #6534's sharp
two-axis error, #6536's sharp matched three-axis error, Nick Petalas's #6438
five-seed rotation, and @CubeJerry's #6758 native forward/inverse theorem.
Those applications derive radial outward-slack values from pinned periods
and error bounds; they do not reverify source tables or certificates.

Base: canonical main `e54523517d0f03e58352e647c403a5af3e525a57`. Exact proof
and kernel pins, including Git blob IDs and SHA-256 digests, are in
`SOURCES.json`. The unchanged #6509 kernel replay passes 72 signed ray inputs
through `t=2^256`, literal inverse checks, dyadic unit-ball witnesses for
`p=1..64`, and source/assumption negative controls. Run
`python3 -B reproduce.py`; the receipt is emitted to stdout. `RESULT.json`
changes only with explicit `--write-result`.

Credit Ali Romman (#6509, #6534, #6536), Nick Petalas (#6438, #6619), @CubeJerry
(#6758), and the finite-sphere predecessor #2589. The new proof and replay
were prepared with substantial OpenAI Codex assistance; `SOURCE-NOTICE.md`
preserves the #6509 notice.

This is not a new κ result or a change to the selected frontier. All five
global assumptions of the current conditional multiplication theorem remain
as stated. The unrestricted #6619 outward-slack question remains open; the
note establishes neither global optimality for arbitrary maps nor a physical
implementation or tariff.
