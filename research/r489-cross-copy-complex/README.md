# #493's R489 bit word with #448's cross-copy complex supplier: conditional κ ≈ 1.4354688·10⁻³

Composition of two published suppliers, both rebuilt here: eumemic's R489 E8 bit word (#493, bit c = 1.565442·10⁻³,
whole-residual hosting, eleven stages) and #448's cross-copy hosted #433 complex word (b = 1.437532·10⁻³).

**Result:** κ = 358867191156973/(2.5·10¹⁷) = 0.001435468764627892, complex-bound, **+4.63 % over #480**. It equals the
figure #493 lists for this pairing as information only; here the complex supplier is rebuilt from #442's verifier and
independently audited instead of cited.

## Verify

```sh
python3 -B research/r489-cross-copy-complex/verify.py /absolute/new/output
```

Runs #493's `verify.sh` unchanged (numpy, sympy, C++17, Boost headers via `BOOST_INCLUDE`; about two minutes), then
#442's complete `verify.py` (about two minutes), then the cross-copy complex generator, its audit and the assembly,
and compares every value, the emitted-program digest and the complex template hash with `EXPECTED.json`.

## Scope and credits

Conditional, like its parents. Review points: #448's cross-copy slot (complex side only) and #493's own.
Credits: eumemic (#493 word and pipeline adaptation), DaysSky (#442), chafreaky (#443–#445, #472 pipeline), icekylinx
(#433), Zhihao Chen (#425/#386), Rohan Arun (#434), Dylan Crow (#370), Jacob Sussman, and all source-pinned authors.
`research/e8-bit-carrier-skeleton` is #493's package vendored unchanged. The composition, complex audit and
assembly were prepared by higherbeing with Claude (Anthropic) assistance.
