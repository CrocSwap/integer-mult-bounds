# Independent root review of the header/cutoff prefix

**PASS at the declared control-interface scope.** The root independently
read the complete source and proof, inspected the selected exponent/header
sources, derived the loop invoices and ran a separate dense CPU. Prepared
for Jerry Chen / @CubeJerry with substantial OpenAI assistance; independent
AI review does not establish human or formal-kernel acceptance. Apache-2.0.

## Frozen snapshot

Scientific base: `e54523517d0f03e58352e647c403a5af3e525a57`.

- `cutoff_prefix.py` SHA256:
  `1f67f85d14f472e94e05072c4d9840ff9b79ee7d944e2fb1699c44e4b9b8687d`.
- `PROOF.md` SHA256:
  `5cfa6f6c0a3c3eca790c7c155dcdff3b769dc320d3a5a9a31c7356cfe2d72262`.
- Unchanged controller dependency:
  `9dfe6747b8553fd11b408f2b045c5954ef1e6eaa`, with exact file pins retained.

## Source, loop and cost review

The selected gate assigns stop=g and epsilon=1-g, g=1/10^14. Its different
outer variable be is not the stopping exponent. The retained layer provides
Gamma(p)Gamma(d), d<=b_d*p^epsilon and V=2Mrw>=2(p+2). The claimed budget
therefore uses actual source parameters rather than a generic epsilon<1.

The Gamma decoder consumes exactly the tail length recorded by its leading
zeros. Unary updates v -> 2v+delta decode d; earlier prefix values have total
below d. TRACE logs every header move and reverses exactly that distance.
Private guard cells begin owned and blank, and their establishment and
retirement are literal instructions. HEADER is never written.

For the saturated product z=min(ab,d), positivity and a,b<=d imply
z>=max(a,b). Thus even terminal rewinds of operands are O(z). Direct loop
counting supports 40z+40; copying, product, two erasures and transfer give
77z+62<=160d per power step. The saturation identity proves the fixed binary
power chain for all inputs, including equality. The sentinel e+1 is accepted
without a power; all actual power operands satisfy t<=e<=d. C<=d then gives
C^2<=dC, paying all failed-trial scans and increments. Marker work, all head
returns, arithmetic retirement and cutoff cleanup fit the stated complete
1000(R_Q+1)(h+dC+1) envelope. Historical backing includes the unary d banks
after erasure, as well as the trace, guides, cutoff and suspended stack.

Fixed jump relocation preserves every selected instruction except replacing
its completed HALT by one cleanup jump. That program accesses only tapes
0..3; HEADER and restored private banks remain stationary. Its completed-call
restoration supplies exactly the cleanup entry. READY/RETIRED are finite
control edges, not runtime callbacks or a stored transcript.

Finally epsilon*(1+1/Q)=1-1/Q^2. Hence dC=O(p), with b_d incorporated into
the fixed constant, and h<=|E|=O(p). The nonempty retained array pays O_Q(V)
for the complete root prefix and retirement. Additional O(d+log p) history
also fits O(p). This uses the selected coupled exponents; it is not a claim
for arbitrary epsilon and stopping beta. No new supplier rate is introduced.

## Independent executable evidence

From this directory:

```sh
python3 -I -W error -B independent_check.py .
```

The JSON report records **117 cases and 1,015,704 transitions, PASS**. This
checker imports the compile-time builder and uses its own dense eleven-tape
CPU, input encoder and exact integer-root oracle. It never calls the author's
Machine, input constructor, verifier or expected-event function. Selected-Q
fixtures explicitly have d<2^Q, so their exact ceiling root is one or two;
the universal written invariant, not those tests, covers larger d.

Coverage includes Q=2,3,5 and the selected Q, perfect-power neighborhoods,
caps, long Gamma(p) with tiny d, shifted origins, hostile inaccessible
exterior cells and joined cleanup. Wrong header return, skipped retirement
and a substituted exponent each fail at the expected semantic boundary.
The frozen receipt is `evidence/independent.json`. Tests corroborate the
written theorem; they do not establish it by extrapolation.

## Residual obligations

Header validity and active WIDTH after Q0 reservation remain premises. The
actual final N/P/owner manifest, row grants, chronological scalar/frame and
payload/remainder consumers, native contracts and analytic endpoints remain.
The result closes this cutoff input edge; all five selected assumptions and
kappa are unchanged. No complete multiplier or native payload run is claimed.
