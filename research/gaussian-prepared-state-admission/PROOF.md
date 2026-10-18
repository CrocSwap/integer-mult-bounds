# A certificate must bind the prepared Gaussian state

## Precise source-bound failure

The source is Mason Hale's PR [#2313](https://github.com/CrocSwap/integer-mult-bounds/pull/2313),
commit `190637e62401516c72b267859c0dd51cac607f6d`. Four unmodified files are retained
under `vendor/`; `SOURCES.json` records both Git blob IDs and SHA-256 digests.
This note concerns reuse of a mutable `GaussianLine` after certification.
It does **not** invalidate the PR's fresh committed configurations or its
Gaussian analytic identities. No selected supplier or selected exponent changes.

The original `uniform_certificate` only invokes `line.certify_operator()` when
`line.operator_error is None`. `GaussianLine.transform` has the same condition.
The matrices, selector, precision and scale are mutable and there is no cache
key binding the cached errors to those fields. This is an ordinary data mutation,
without monkeypatching methods, changing files or injecting a mutation option:

```python
line = GaussianLine(5, 8, 5)  # p=256, Q=448
before = uniform_certificate([line], 4)
line.compression = [[2 * x for x in row] for row in line.compression]
after = uniform_certificate([line], 4)
value, receipt = multiply(1, 1, [line], 4, input_bits=4)
```

The exact retained source returns `before == after`, `value == 8`, coefficients
`[8,0,0,0,0]`, and an accepted radius below `1/2`. The full rational radius and
certificate are in `result.json`. `input_bits=4` is a legal declaration for
the operands and lets the wrong value pass the output-width guard. Omitting it
would declare one bit and the output-width guard would reject this particular
witness. This detail matters: the reproducer does not disable that guard.

Doubling compression doubles the computed transform. There are two forward
transforms, their pointwise product, and one opposite transform, hence the
factor eight. Quantization could complicate a general scaling identity; we
claim the exact executed witness, not an identity for all operands. The
independent process repeats factors one, two and three, observing one, eight
and twenty-seven respectively. Resetting `operator_error=None` before a fresh
certificate rejects both modified maps. The failure is stale error reuse;
fresh operator certification detects it.

## Immutable admission and reuse proposition

Under ordinary Python API use, with the retained runtime unmodified, an object
returned by `prepare(lines,b)` uses the **same data and certified bounds** at
every subsequent multiplication as those checked by its admission. Subsequent
changes to the source lines or returned certificate dictionaries cannot affect
the object. This proposition closes the prepared-state implication. The
Gaussian approximation and error analysis remain those of the pinned source;
this is not a new independent proof of that entire analysis.

Admission performs these steps:

1. Copy every field read by normal `certify_operator`, `transform`, and the
   caller: `s,t,alpha,p,bits,gamma,selector,expansion,compression`. Scalars are
   exact integers; each interval becomes an immutable integer endpoint triple;
   matrices and selector become recursively immutable tuples.
2. Recheck the original integer, alpha/theta, power-of-two and working-precision
   domains. Bind `gamma=2 alpha^2` and the prescribed nearest-point selector.
   Check complete matrix shapes, ordered interval endpoints, common interval
   precision and both interval row-sum absolute norms strictly below one.
3. Materialize a private original-class line from that captured data with both
   cached errors set to `None`. Invoke the actual source `certify_operator()`
   unconditionally. Retain only its newly computed exact rational errors.
4. Run the actual `uniform_certificate` on the freshly certified private
   lines. It checks common precision, pairwise coprime axes, transform disk
   margin and uniform unique-integer recovery margin. Freeze its certificate
   as bytes, and bind source head, digit width, all snapshots and fresh bounds
   in a canonical SHA-256 fingerprint.
5. At each call, create disposable private source-class lines from those exact
   immutable tuples and bounds, and invoke the unchanged original `multiply`.
   No input object, mutable matrix or mutable certificate is retained. Do not
   expose the source's deliberate `mutation` test option. Restrict declared
   input widths to the admitted finite width and operands to nonnegative
   integers in that declaration.

For the proposition, step 1 makes all subsequent computation depend on copied
values; steps 2-4 validate those values rather than a prior object's claims.
Step 5 reconstructs them exactly. The source's normal operator and transform
methods read no omitted instance fields: `inverse`, `diagonal`, correction
tails and constructor diagnostics are not read along these paths. `diagonal`
is read only by the source's deliberate `omit_correction` mutation, which is
not exposed. The exact source methods, FFT, grid, selector, scale, and error
rules therefore coincide between the checked and reused state. Freshly
computed rational bounds and integer endpoints have no mutable descendants.
Certificate properties return decoded copies, so mutating a returned object
does not change the stored bytes.

The implication to correct multiplication is conditional on the pinned source's
analysis of its checked operator bound, contracting real maps, normalized FFT,
grid rounding, tensor error sum, coefficient recovery and carry scan. Our
wrapper does not replace those with an integer-product oracle. Integer products
and schoolbook coefficient convolution occur only in `verify.py` as test
oracles. Arbitrary newly admitted matrices need not be original Gaussian
formula values: their complete operator is freshly checked against the same
Fourier target and their contraction norms and rounding widths are rechecked.
A positive control negates both maps: `(-B) FFT (-A)` is unchanged, fresh
admission succeeds, and its different data gives a different fingerprint.

## Boundaries

The interface handles a finite dense reference configuration, not an
asymptotically efficient tape implementation, uniform compiler or all-size
supplier. It is not a cryptographic sandbox against reflection, deliberate
`object.__setattr__`, malicious replacement of loaded Python modules, altered
source-plus-manifest pairs, or arbitrary process memory writes. Only ordinary
API use of a returned object is claimed. Private snapshot materialization is
an implementation detail, not a new untrusted-deserialization API. Source
byte authentication occurs before loading; it does not prove the source
correct. The manifest is a reviewable pin, not a signing infrastructure.

The finite test suite gives coverage of the demonstrated failure and admission
contracts; it does not enumerate every admitted configuration or operand.
The immutable reuse proposition follows structurally from the complete field
capture above. Fresh original fixtures remain useful, and this finding does
not claim they ever exercised mutated prepared state.
