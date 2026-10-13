# Independent verification: signed packed Gaussian convolution

**Result:** the pinned PR #489 `packed_lower` agrees with an independently
written integer-dot-product/divmod oracle for every declared input. All
**eight semantic mutants** execute and return incorrect values that the
oracle detects. This is an independent-verification contribution, not a
construction or a new kappa claim.

## Reproduce

From the repository root, with Python 3.9 or later and no third-party packages:

```sh
python3 -B research/gaussian-packed-convolution-audit/verify.py
```

Expected output begins `PASS_INDEPENDENT_SIGNED_PACKED_CONVOLUTION`, followed
by totals: 22,620 vector pairs, 45,240 packed calls, 183,212 output coordinates,
180,960 integer products, 8 semantic mutants rejected, and 3 admission
controls rejected. `EXPECTED.json` is the complete deterministic receipt;
the command recomputes and compares all of it. It does not write into the
checkout. `--output /absolute/new/receipt.json` optionally writes a new copy
only after comparison. `--record /absolute/new/receipt.json` is an explicit
bootstrap mode, not a replacement for verification against the committed
expectation. Existing output files are never overwritten.

## Completed coverage and stopping rule

The exhaustive part has n=1..4 and b in {0,1,3}. At each (n,b), BOTH input
numerator vectors range independently over {-a,0,a}^n, where
`a=max(1,2^b-1)`; actual inputs divide those integers by `2^b`.
Every pair is checked in lower and upper orientation. This is exactly
`3 * sum(3^(2*n), n=1..4) = 22,140` pairs, not a random sample.

The remaining 480 pairs are eight fixed patterns at each of 12 lengths
`1,2,3,4,7,8,9,15,16,17,31,32` and five precisions `0,1,3,17,64`.
Patterns include zero vectors, near-carry products, alternating signs,
near cancellation, endpoint impulses and SHA256-derived mixed data using
assignment seed 79. The numerators reach 128 bits; packed operands reach
8,219 bits. All retained coordinates are compared exactly. The transcript
hash commits to the ordered inputs and oracle outputs; matching source
outputs are required before a row enters that transcript.

The stopping rule was completion of this domain and the predetermined
controls. No supplier search, asymptotic execution or benchmark claim is
made. The independent written radix argument is in [PROOF.md](PROOF.md).
The finite replay is not a formal proof of that universal argument or of
the full multiplication theorem.

## Controls and scope

Six in-memory source mutants change slot width, omit a signed cross product,
flip the double-negative sign, round negative numbers down rather than toward
zero, round the four products before cancellation, or use S instead of S^2.
Two upper-wrapper mutants omit the output reversal or reverse the kernel.
Every mutation must have a passing unmodified baseline and a completed,
unequal mutated output; an exception is not counted as an arithmetic finding.
Exact witness vectors and both outputs are retained in EXPECTED.json.
Off-grid kernel/input and unequal-length admission are checked separately.

No source bug was found in the declared domain. No conclusion is drawn about
the full Gaussian approximation, Schur solve, weighted tensor evaluator,
physical tape/routing costs, or a new exponent. The selected record remains
#626 with #543, conditional kappa 0.001635527380375392 at the base commit.
`upstream/`, the selected frontier, existing generators and other research
packages are unchanged. Full repository-wide and frontier cold replays are
not required by these standalone changes and were not launched.

## Provenance and differentiation

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR #489 source: `8922e3b3f0fd7772b0fb42028eb2532984c3ab42`.
`SOURCE.json` records original paths, SHA256 and Git blob hashes; vendor
bytes were compared directly to `git show` at that commit. The local sprint
claim records seed 79 (OS randomness), three candidates and one pivot:
concurrent local symbolic Gaussian claims appeared before implementation,
so this package audits packing instead of duplicating their q-polynomial
identities. It also does not reopen #489's premature tensor-kernel rounding
negative result or duplicate #666/#668/#673 cyclic work.

See [NOTICE.md](NOTICE.md) for predecessor attribution and AI disclosure,
and [VALIDATION.md](VALIDATION.md) for actual run evidence and limitations.
