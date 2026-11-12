## Result and why it matters

The canonical simultaneous layer still needs two diagonal S_D phase sweeps.
The pinned [literal egress](https://github.com/CubeJerry/integer-mult-bounds/tree/51ab0539059214fcfa044938c36a0b6017232be5/research/literal-layer-egress)
supplies b^D and the final toward-zero projection but explicitly leaves these
sweeps supplied. This package implements that actual boundary in one fixed
2,146-location program on twenty tapes.

It reads the nine-Gamma header, constructs the selected-bit mask, enumerates
implicit `[P] x [2^K]^D x [S]` addresses, repeats phases over r coefficients,
and returns exact w-bit MSB Gaussian rotations on the original DATA owner.
Every parameter, counter and payload operation executes through local-symbol
branches, one-cell writes, unit moves and fixed jumps. No runtime address,
decoded parameter, supplied mask or input-sized lookup is used.

For E header bits, N=Mr coefficients and V=2Nw payload bits:

```
T <= 65536(E+p+d+DK+Nw+1)
private historical backing <= K0+4V+32(E+p+d+DK+w+1).
```

These include all setup, source reads, coefficient work, repetition,
staging, original-owner commit, returns and erasures. Carry-prefix work is
O(P*2^(DK)); unary r/P/S acquisition is paid because each is at most N.
The complete boundary is O(V) in the selected source bands. Success returns
all heads and private banks; numerical range rejection preserves the full
public input before commit. No rejection cleanup is claimed.

## Novelty and predecessor credit

Ali Romman's #5375 proves sequential monomial phases with a supplied active
mask, fixed recipe dimension, source-level counter/consumer and one Gaussian
coefficient per record. It leaves geometry production, packed repetition,
literal lowering and complete caller binding open. The new result supplies
header-produced geometry, variable D on a fixed inventory, r/P/S grammar,
literal MSB rotations and same-owner cleanup for the specific outer S_D.
Counter amortization and Gaussian phase algebra remain credited methods.

The egress and new sweep can use distinct private banks plus two public
tapes: 36 fixed tapes total, with the phase bank reused for the final pass.
An exact C service and its paid common-grid conversion remain explicit
premises. No complete layer or multiplier is claimed.

Credit @CubeJerry / Jerry Chen; Ali Romman #5375; Jose Manuel #2250;
JoyboyBrian #5329; Cinna Davis; Ryanson Jonathan #4325; the canonical
header/layer authors; and CubeJerry's pinned literal controller and egress
packages. Substantial OpenAI assistance contributed construction, proof,
implementation and separate agent review. Human/proof-kernel acceptance
is unclaimed. Apache-2.0; predecessor notices are retained.

## Exact source and checks

Base `e54523517d0f03e58352e647c403a5af3e525a57`. Exact paths, commits, Git
blobs and SHA256 values are in SOURCES.json. Only
`research/literal-layer-phase/` is added; frozen source and selected records
are unchanged.

```sh
python -I -W error -B research/literal-layer-phase/verify.py
python -I -W error -O -B research/literal-layer-phase/verify.py
python -I -W error -B research/literal-layer-phase/compose.py
python -I -W error -O -B research/literal-layer-phase/compose.py
```

Expected: `PASS_LITERAL_LAYER_PHASE` and `PASS_LITERAL_PHASE_EGRESS_JOIN`.
The main run covers 319 packets / 29,586 coefficients, 52 geometries, all
256 signed three-bit pairs isolated at four phases, 31 range rejections,
five invalid controls, seven detected actual-program mutations and stable
history reuse after growth and shrinkage. The separate join executes both
literal phase sweeps and the pinned egress around a clearly labelled
**test-only exact C oracle**: ten disk-grid tensors / 316 coefficients
match a direct normalized Walsh tensor and one final projection.

Independent review and a separately implemented dense interpreter are
recorded in REVIEW.md and the included review receipts. The dense review
passes 24 packets and three semantic mutations. The separate universal and
structural review accepts the proof and checks 15 successful runs, 2,084
record entries and the exact counter movement census; its three controls
include a numerically correct full-width scan that violates the cost claim.
Universal claims rest on the written proof; finite checks corroborate them.
Hosted CI and formal proof-kernel acceptance are separate.

## Limits and open obligation

**No new kappa. All five global assumptions remain.** An executable exact C
consumer, canonical-order return, common-grid conversion, owner allocation,
compiler/native admission, packed permutations and integer recovery remain
unimplemented by this package. The next useful join should supply C at this
precise header/owner/width interface with a complete physical invoice.
