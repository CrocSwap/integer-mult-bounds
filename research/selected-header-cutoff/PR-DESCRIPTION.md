## What changed and why

The published selected rank controller received a supplied unary stopping
cutoff. This package implements that input edge from the actual retained
Gamma(p)Gamma(d) header, links the producer to the unchanged controller, and
retires the generated cutoff after the completed call.

The selected gate uses stop=g=1/10^14, distinct from its outer be=1-3g.
The producer preserves this source distinction and constructs
`C=min(ceil(d^(1/Q)),e+1)`, Q=10^14. Because every descendant width is at
most root width e, the cap preserves all source stopping decisions and
remainder hooks.

## Exact result and complete costs

The emitted machine has eleven fixed tapes and the predecessor's finite
alphabet. It reads the header symbol by symbol, skips Gamma(p), converts
Gamma(d) to unary by paid doubling, performs saturated unary multiplications
for fixed-Q powers, and compares successive trials with the active WIDTH.
All private guard markers are physically established and retired. No runtime
host arithmetic, callback or host recursion chooses machine actions.

With `h=|Gamma(p)Gamma(d)|` and `R_Q=bit_length(Q)+popcount(Q)`, the complete
controller and prefix satisfy

```text
T <= 200(P+1) sum_v e_v + 1000(R_Q+1)(h+dC+1)
S <= K0+(5+N/(N-1))e+5d+4h+40.
```

Every copied symbol, failed trial, head return, input access and erasure is
paid. Unary d leaves O(d) historical backing after erasure; it is not hidden
in a root-width-only bound. For the actual selected epsilon=1-1/Q,
`dC=O(p^(1-1/Q^2))=O(p)`. Thus the prefix and retirement fit O_Q(V) using
the admitted nonempty record and w>=p+2. No new supplier rate is assumed.

The selected-Q prefix has 5,649 instruction locations. The N=3,P=2 joined
demonstrator has 5,951 locations and six symbols. The general fixed-N/P
composition is proved; the enormous actual selected final template is not
materialized.

## Sources, novelty and credit

Scientific base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The two frozen executable inputs are unchanged copies from the
[published selected-rank-control package](https://github.com/CubeJerry/integer-mult-bounds/tree/9dfe6747b8553fd11b408f2b045c5954ef1e6eaa/research/selected-rank-control),
with exact Git blob and SHA256 pins. Linking relocates fixed jump targets and
replaces only its completed halt edge.

Retained outer setup already supplies ordinary exact rational-power
comparisons. No novelty is claimed for integer-root arithmetic. The advance
is this source-specific finite-symbol producer and exact completed-call
composition. #5158 supplies earlier fixed-bank recursion; #6719/#6739 supply
richer natural-root/grant work from supplied depth. #5515 studies the
different historical QQ16 root cutoff. #2310/#2386 retain their paid control
preparation credit.

## Reproduction and checks

```sh
python3 -B research/selected-header-cutoff/verify.py
python3 -O -B research/selected-header-cutoff/verify.py
```

Expected: `PASS_SELECTED_HEADER_CUTOFF_PREFIX`. Normal and optimized receipts
are identical. The replay covers 357 parameter cases, 27 exact-power boundary
cases, seven selected-Q cases, 204 saturated products and six separate dense
CPU runs. Main cases execute 3,573,948 transitions and 1,324 controller nodes.
Thirteen controls exercise invalid exponents, header/head restoration, cap
equality, strict power boundaries, decoder and saturation faults, retirement,
wrong exponent, false time/space bills and source corruption. Hostile ancestor
prefixes and shifted origins are preserved.

The all-input theorem is the written loop/stack proof. Finite executions are
corroboration, not extrapolated universal correctness or formal-kernel proof.

## Limitations and kappa status

**No new kappa; all five selected foundational assumptions remain.** The
selected conditional kappa stays 0.00363005817. Header validity, active WIDTH
from the Q0 reservation, actual final paid/owner manifest, complete row grants
and payload/remainder consumers remain inherited. This closes the cutoff
input edge of that admitted interface, not the entire external-root dispatcher.
No complete multiplier, selected cold replay, native payload execution,
independent human review or formal-kernel acceptance is claimed.

Prepared for @CubeJerry with substantial OpenAI assistance. Credit the
published predecessor and the retained physical/native/compiler contributors,
including JoyboyBrian, thu-nmrc, ToikY, commdata2338, Ali Romman, David Arias
and Jose Manuel. New work is Apache-2.0; frozen notices are retained.

## Independent acceptance checks

[REVIEW.md](REVIEW.md) records the orchestrator's universal-loop and source
review plus a fresh dense eleven-tape CPU and direct integer-root oracle.
It passes 117 cases and 1,015,704 transitions, including long p headers, tiny
d, shifted origins, hostile exterior, the actual fixed Q, completed cleanup
and three semantic mutants. [PEER-REVIEW.md](PEER-REVIEW.md) independently
checks all source pins, the symbolic control proof, exact helper instruction
counts, and the complete time and historical-space sums without executing
the author verifier. These are separate AI reviews, not human or formal-kernel
acceptance. All reviewed scientific hashes are recorded in the evidence.

```sh
python3 -I -W error -B research/selected-header-cutoff/independent_check.py
```

The full Markdown PR description is committed in `PR-DESCRIPTION.md`.
