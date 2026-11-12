## What changes and why it matters

The selected #7000 application specifies one exact common-grid complex layer
followed by Gaussian normalization and a single truncation toward zero. #3127
already provides a structured encoded normalizer but leaves root truncation
and literal finite-state lowering. This package supplies that numerical egress
as one fixed 17,814-location program on eighteen tapes and four symbols.

It reads the actual nine-Gamma header, distinguishes global d from actual D,
constructs H=p+2d+4 and shift d+ceil(D/2), evaluates complete signed Gaussian
rows and projects once to the original p grid. Output is staged until all
range checks pass, then committed to the original owner with its old tail
erased. Every successful head/guard/work return is included.

## Exact result and novelty

For N complete H-bit Gaussian pairs on grid p+d, return Q_p(b^D z) in w-bit
MSB format, b=(1-i)/2. The all-input proof covers negative fractional values,
the most-negative input, odd-D sums needing extra bits, necessary-and-
sufficient signed output guards, and wider output backing. Numerical range
failure leaves DATA unchanged; head/private recovery after failure is not
claimed. No same-grid exact-division premise is imposed before the projection.

Complete literal time is at most
65536(E+p+d+D+w+N(H+w+1)+1), with header length E. Private historical backing
is at most K0+4N(H+w)+16(H+w+E+1); erased storage stays charged. These are O(V)
in the selected source bands. Finite table precompilation is separate.

## Reproduction and checks

```sh
python3 -I -W error -B research/literal-layer-egress/verify.py
python3 -I -W error -O -B research/literal-layer-egress/verify.py
```

Both emit PASS_LITERAL_LAYER_EGRESS. Exact integer/Gaussian oracles check
771 generic packets (515 acceptances, 256 range rejections), 64 exact signed
endpoints, 12 complete small C/S/H0 tensor fixtures and six semantic mutants.
The generic suite executes 5,125,983 literal instructions. Normal and
optimized receipts agree. All seven frozen source inputs are authenticated.
Independent dense-CPU and universal-proof review are recorded in the package.

## Pins, limitations and kappa

Base: e54523517d0f03e58352e647c403a5af3e525a57. Runtime notation:
CrocSwap/integer-mult-bounds#7349 at
9dfe6747b8553fd11b408f2b045c5954ef1e6eaa. All paths/blobs/hashes are in SOURCES.json.

**No new kappa; selected 0.00363005817 remains conditional.** None of the five
framework assumptions is wholly discharged. This removes one numerical
implementation implication inside precision_tape. C and both S phase sweeps,
common-grid production, valid complete caller packet/cardinality, disjoint
blank backing and stock/allocator obligations remain premises. The proof
shows Q_p commutes with the supplied signed phase permutations. This is
literal egress, not a complete layer or multiplier. A different coded/LSB
consumer still needs a priced conversion.

## Credit and next question

Prepared for **@CubeJerry**, with substantial **OpenAI assistance**. Credit
Tekalign #3127; Jose Manuel #2287/#3087/#3091/#3098; the upstream layer/stream
and retained native/precision authors; and CubeJerry's #7000/#7349/#7350 work.
Independent AI checks are not human or formal-kernel acceptance.

Next: join an actual completed C consumer and its unchanged original header
to this exact MSB API, price any conversion, and run the final S sweep on
its returned w-bit packet. Full proof, exact provenance, limitations and
review evidence are in research/literal-layer-egress/.
