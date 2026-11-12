# Independent review of the header-derived literal phase sweep

**Decision: accept the scoped literal phase-sweep theorem.** No change to
the frozen scientific program was required. One historical-space wording
ambiguity was identified and corrected in the proof: a sum of maximum
reached extents per role applies to repeated calls at fixed origins;
arbitrary changing origins require the union of absolute visited windows
and separately paid caller head transport. The reviewed proof contains
that distinction.

This review is additional OpenAI-assisted evidence. It is neither human
acceptance nor proof-kernel certification. It supplies no tensor-C service,
native arbitrary-column admission, source allocator, failure cleanup,
general phase provider, complete multiplier, or new kappa.

## Reviewed bytes and method

- `phase.py`: `9a360817b80e869398927f38a4f110de0b5a1f9620eeb23b19e166f112b83f23`.
- Generated table: 2,146 instruction locations, SHA256
  `50505d6bd350224021d88d8e7e142a3188649a1d391c34ade732fced19336624`.
- Corrected `PROOF.md`: `05581d135d43df6e7e9a1b9c2fd93b91a5ab1e10fc631a78ba7245c32c083aaf`.
- Canonical dependency base: `e54523517d0f03e58352e647c403a5af3e525a57`.

I inspected the entire generator, the frozen elementary instruction
semantics, and the complete universal proof. The accompanying `check.py`
executes the generated graph in a separately written interpreter. It does
not call the author's `Machine`, `Tape`, arithmetic oracle, or verifier.
The frozen Builder only supplies the table under review; every transition
thereafter is independently interpreted as a local read, one-cell write,
unit move, fixed jump or halt. Static checks reject variable tape selectors,
nonunit moves, unknown opcodes and nonliteral branches. All verification
observations are outside the measured program and never choose its steps.

The lead's independently constructed dense Gaussian/address oracle is
complementary evidence and is not claimed as this review's execution.
This review deliberately uses zero payloads to isolate geometry, repetitions,
phase-state invariants, costs, public-owner installation and retained history.
Signed Gaussian correctness was also checked directly from the finite cases
in the source, as explained below.

## Universal control and geometry argument

The nine Gamma decoders operate on the supplied header, including r,P,S.
Each following binary digit replaces unary v by unary 2v+b through explicit
copy, erase and return loops. The old prefix values sum to less than the
final value. Decoding therefore costs linear work in the decoded values
plus encoded header length, without a hidden binary-to-unary constant-time
step. On admitted complete packets, r,P,S are each at most N, while D,K and
rho+1 are at most L=DK. The p,d terms remain explicit until the source-band
specialization. HEADER is never written; its movement is exactly 2E.

For each chunk, SELECT reaches its blank immediately after rho+1 unary
symbols, writes the unique active mask bit, and stops affecting subsequent
positions. BLOCK then finishes exactly K cells. Both unary heads return at
each chunk boundary. The DIM loop creates exactly D chunks, hence L cells
on both MASK and COUNT. Reversing the ordering of whole chunks in the LSB
counter does not alter the sum of the selected bit of every chunk. The
lexicographic source order and generated counter are consistent.

The finite phase state is q=sum(MASK[j]*COUNT[j]) modulo four. Each flip
of an old bit b changes it by (1-2b)*MASK[j]. A complete wrap returns the
counter to zero and necessarily returns q to zero. COEFF performs exactly
r pairs per spectator entry; SPECTATOR performs exactly S entries before
one counter increment; OUTER advances only after a whole 2^L domain.
These loops give P*2^L*S*r pairs without an externally supplied N.

The final read of DATA requires a blank immediately after the last header-
derived component. Every missing component instead rejects during a literal
load. This check occurs before any DATA write, so the complete cardinality
guard is not merely a host-side fixture check.

## Independent amortization and constant audit

For L>=1 and Q=2^L, one complete domain has exactly 2Q-2 counter-bit flips,
including its final wrap. An increment changing t bits advances COUNT and
MASK by t cells each. Each rewind traverses only that changed prefix, with
t+2 unit moves per tape, not the remaining counter suffix. Consequently
each tape uses 2t+2 moves for that increment. Including initialization,
geometry generation, final clearing and guard operations, the *exact*
successful-program move count for each of COUNT and MASK is

```
4L + 8 + P(6Q - 4).
```

This census is derived independently of the author verifier and checked
against every executed transition. It directly detects a hidden full-width
scan in a carry return, even if all numerical outputs remain correct.

I recomputed the elementary instruction allowances from the table pattern:
rewind uses 3t+3, clear uses 7t+4, and a trace return uses 5t+3. The two
unary copies and old-value erasure for v->2v+b cost
47v+17b+18 <= 47v+35, before the fixed Gamma wrapper. Geometry costs at
most 35L+10 by summing the before/active/after paths and all rewinds, hence
fits the proof's 64(L+1) allowance.

The exact successful component bounds are 15w+7 for load, 7w+5 for
negation, and 9w+4 for staging/erasure/return. A pair with two negations is
therefore at most 62w+32 before repetition control. A nonwrapping counter
increment costs 12t+7 and a wrapping one 12t+10, so the complete counter
bill is below 34PQ. Full r/S rewinds cost O(N), because their total scanned
unary lengths are N and M. The two payload-head returns, two OUTPUT rewinds
and original-owner copying cost 24V+13 after the payload-end guard. That
single guard is absorbed by the remaining constant slack.

These direct loop bills fit the supplied 4096 metadata and 512 coefficient/
repetition allowances. Using V=2Nw, N>=2, w>=3 and N+w<=Nw leaves ample
margin under `65536(E+p+d+DK+Nw+1)`. This is a proof from the fixed graph's
loops, not extrapolation from observed ratios or interpreter timings.

## Arithmetic, owner return and history

The four cases are respectively (a,c), (-c,a), (-a,-c), and (c,-a).
Negation walks from the least significant end using one carry bit, retaining
the final old and new sign bits. Both are one exactly when negating the
most-negative signed integer; thus the guard rejects precisely an
unrepresentable required component. A component that is only swapped may
retain that value. No data-dependent integer arithmetic occurs outside
literal symbols and finite state.

Every transformed pair is staged privately. DATA is written only after all
coefficients and the final cardinality guard pass. The program then writes
exactly V bits on that original owner and erases the private copy. DATA has
exactly 4V moves on success; HEADER has exactly E reads and 2E moves.
All private heads and public heads return to their respective origins.
The entire private bodies and guards visited by the successful call are
erased. Failure cleanup and successful reentry after a rejection remain
unclaimed, correctly.

The eighteen-role extent table is exhaustive. Summing endpoint-plus-two
lengths gives the claimed intermediate bound
`3V+2E+2p+2d+6DK+4w+36`: the combined r/P/S contributions are at most
6N<=V. Adding entry history gives the published larger envelope. Clearing
cells never removes that historical backing. At fixed role origins,
successive calls retain the maximum reached extent on each individual role;
at changing origins the corrected proof retains absolute unions instead.
The review does not treat maximum total per-call footprint as cumulative
history and does not infer blank owned windows from a single origin probe.

## Executed evidence and sensitivity

Warning-strict ordinary and optimized runs produce byte-identical receipts:

```sh
python -I -W error -B /workspace/scratch/be42ab5b7196/reviews/c2-peer/check.py
python -I -O -W error -B /workspace/scratch/be42ab5b7196/reviews/c2-peer/check.py
```

For a copied or published package, the portable entry point retains the
unchanged checker while explicitly selecting its package directory:

```sh
python -I -W error -B replay.py /path/to/research/literal-layer-phase
```

That entry point was also executed and produced the identical receipt.

`RESULT.json` reports 15 successful runs (12 fresh geometries and three
calls on the same private objects), 2,084 complete address-record entries
and 2,175,819 interpreted transitions. Tests include variable D,K,rho,
non-power-of-two r/P/S, a unary d=257, and shifted tape origins with opaque
exterior symbols. At every record entry, direct observation checks the
generated mask, counter value, phase state, P/S positions, r reset and
complete coefficient consumption. Successful calls check exact source
reads, writes and moves, full retirement, head restoration and both published
resource envelopes.

The reuse sequence retains histories 92 -> 15499 -> 15499 -> 15505.
The small middle call takes exactly as many instructions as its fresh-bank
counterpart, despite the old larger blank tails. No private object, origin,
head or history is reset by the harness between those calls. Public source
replacement between calls is explicitly separate caller acquisition.
Extra-payload and missing-bit packets reject before any public write.

Three independent semantic mutations are detected with the intended
diagnostics: a wrong generated mask, omitted COUNT retirement, and a full-
width scan inserted into each ordinary carry return. The last mutant first
passes all functional geometry/owner/cleanup checks when the exact move
census is disabled; it fails that census when enabled. This demonstrates
that the amortization check is not just a rerun of numerical correctness.

These bounded observations corroborate the universal loop argument. They
do not replace it, enlarge the admitted ownership domain, prove successful
recovery from rejection, or discharge the remaining layer/outer interfaces.
