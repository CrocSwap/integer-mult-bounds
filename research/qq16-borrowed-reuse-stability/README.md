# Sharp borrowed-field stability under QQ16 decoder reuse

The unchanged PR2540 added decoder writes each of its 112 borrowed current Y
fields exactly twice, by a native line and its inverse. It never writes the
112 borrowed current X fields. This package independently checks that write
projection and proves the sharp restoration-error bound under repeated use.

For `N >= 1`, completed native relative error `u >= 0`, and initial borrowed
Y norm at most `B`,

```text
borrowed X error = 0
borrowed Y error <= B * ((1+u)^(2N) - 1).
```

The Y bound is attained by an admissible coherent bias in both native
instructions, at every positive payload tensor depth. Thus a one-invocation
precision allowance cannot be reused for an unbounded number of decodings.
For example, PR2628's sufficient local allowance `u = 2^(-b-21)` permits
restoration error greater than `B*2^-b` after `N = 2^20+1` uses, for every
integer `b >= 0`. This is not a defect in PR2628, which explicitly limits its
claim to one invocation and leaves controller composition open.

A sufficient reuse-aware allowance is

```text
u <= 2^-b / (4N),
```

or, for a binary local-error parameter, `b + ceil(log2 N) + 2` bits. This
controls borrowed restoration only, not all outputs or every interior cut.
The per-use invoice remains 224 rank-one children, 16 rank-eight children,
480 native wrappers, 208 cover maps and 17,472 real scalar primitives.
Repeated decoding pays that bill N times, in addition to inherited work.
No supplier, new kappa or selected-frontier change is proposed.

## Exact contract and proof

### Source binding and reuse boundary

The source word is PR2540 commit
`630d557af5088f66b45c447969cee9576600e50b`. The error contract is PR2628 commit
`e64a7babb285f22baeee89a9d88f5e79c512909a`, PROOF sections 1, 2, 4 and 5.
Byte-exact copies, original paths, Git blob IDs and SHA256 hashes are in
[SOURCES.json](SOURCES.json). Neither predecessor's interpreter is imported.
The newer PR2651 early/output-bank coalescing proposal is a different word;
this receipt intentionally remains pinned to PR2540 and does not certify it.

The independent audit examines all 2,463 events, including allocations and
retirements. The single history boundary is event 32. After that boundary,
each Y_p has precisely one positive and one negative line instruction with
the same port label p. No ADD, CLEAR, cover map or other operation writes any
borrowed current field. The X fields are read-only. The earlier X capture
reads are distinct temporal observations, not extra current-field writes.
The complete list of pair positions is in [RESULT.json](RESULT.json).

A reuse means another execution of the post-B1 added decoder body on the
same retained current observations, with those borrowed fields carrying their
previous returned values. Owned output and scratch banks have the source's
charged CLEAR semantics. Earlier records are supplied independently for each
use. No intervening F0/B1 call, retention fault, external borrowed-field write
or reinitialization is included. This is an explicit possible caller boundary,
not evidence that any existing whole controller executes N such decodings.
Genuine F0/B1 trajectory constraints and a useful output consumer remain open.

Use PR2628's maximum-over-owners payload Hilbert norm. For each native
instruction on actual input v, its result is `Uv + d`, with `||d|| <= u||v||`.
Its frames, labels, wrappers and addressing are exact. Other instruction
errors cannot change this borrowed-write projection. No such statement is
made for the output banks. The ideal native line is unitary at every owner
and payload depth, and each audited pair composes to the identity.

### Upper bound and sharpness

For one borrowed Y field, enumerate its native instructions over N uses as
`U_1,...,U_(2N)`. Their exact trajectory has constant norm at most B. Let e_k
be the difference between the actual and exact values after k instructions.
Unitarity and the local defect premise give

```text
||e_(k+1)|| <= ||e_k|| + u * ||actual v_k||
             <= (1+u)*||e_k|| + u*B.
```

Starting with zero error, induction gives
`||e_k|| <= B*((1+u)^k-1)`. Every ideal inverse pair returns the original
borrowed field, so k=2N proves the claimed restoration bound. With B=0 the
same argument gives zero error. Read-only X fields have no added error.

For sharpness, implement every borrowed native instruction as
`U_tilde = (1+u)U`. Its completed defect is exactly `uUv`, of norm `u||v||`,
so it meets the stated contract for every actual input, not just a test
vector. The actual pair is `(1+u)^2 I`; after N pairs it is
`(1+u)^(2N) I`. Any nonzero initial field attains the bound. This bias is an
adversarial implementation allowed by the error contract, not a claim about
unbiased rounding or an actual physical native child. The literal full-word
fixtures use a common constant owner/payload vector, fixed by all native
lines, stages and cover maps. A separate two-point Gaussian-rational check
also exercises the nonconstant native action.

For the fixed local allowance, Bernoulli's inequality gives

```text
(1+u)^(2N) - 1 >= 2Nu > 2^-b
```

when `u=2^(-b-21)` and `N=2^20+1`. No enormous rational power is needed to
certify this strict failure. This counterexample violates no one-invocation
claim and does not identify an actual controller's reuse count.

For the sufficient horizon allowance, let `t=2^-b` and `2Nu <= t/2 <= 1/2`.
For integer k=2N, the binomial coefficients satisfy `binom(k,j) <= k^j`, so

```text
(1+u)^k <= sum_(j>=0) (ku)^j = 1/(1-ku),
(1+u)^k - 1 <= ku/(1-ku) <= t.
```

This proves the sufficient allowance for every integer b>=0 and N>=1.
It is not asserted to be the largest allowable u. The exact drift envelope
above, rather than this convenient sufficient guard, is sharp.

## Reproduction and evidence

Standard-library Python 3.12, no network or predecessor checkout required:

```sh
python3.12 -Werror -B scripts/research_package.py \
  --package research/qq16-borrowed-reuse-stability
```

The registered replay runs normal and optimized verification and the tests.
The checker authenticates the three consumed snapshots before parsing the
word. It checks every borrowed write and pair, then executes the complete
literal word for 17 successive uses at each of three rational biases,
including the exact positive control u=0. This gives 11,424 borrowed-field
equalities, plus 12 nonconstant Gaussian components. Seven semantic controls
reject a missing inverse, wrong sign, wrong label, borrowed clearing,
borrowed X update, Boolean label and unknown opcode. Tests add actual source
and typed-receipt corruptions through the public CLI and verify read-only,
Git-free export and overwrite refusal. The all-N result is the written proof,
not an extrapolation from these finite fixtures.

This is a source-bound conditional restoration lemma. The full selected cold
replay, native child implementation, component-rounding conversion, actual
retention, physical hosting and formal-kernel proof are not supplied. No
independent human review is claimed. The selected record remains unchanged.

Engineering constraints for this verifier are documented here. Python requires
dynamic allocation, so Rule 3 of Power of Ten has a managed-runtime deviation.
Files are capped at 256 KiB, the word has exactly 2,463 events and 112 ports,
and literal reuse is capped at 17 uses per bias. CPython 3.12.15 tracemalloc
measured a 1,041,834-byte peak for the primary verification call. This is a
local memory measurement, not a cross-runtime allocation guarantee.
No recursive code, unbounded search, subprocess or network call occurs in the
primary verifier. Tests use bounded subprocesses to exercise the real CLI. The source files remain frozen;
future wider words require a successor contract and explicit capacity review.

## Open next questions

1. Does a concrete consumer reuse these observations, and how many times?
   A real count could turn this local result into part of its precision bill.
   Start with the proposed consumer's field ownership and call chronology,
   including every F0/B1 or retention write. No complete consumer with that
   reuse schedule is established here.
2. Can a physical native implementation guarantee paired cancellation or
   another stronger error contract? That could avoid the coherent-bias witness.
   Start with the actual forward/inverse child implementation and test the
   returned borrowed field. The current norm-only completed-child contract
   supplies neither correlation nor exact restoration.
3. How should output and retention errors compose with restoration debt?
   Start with PR2628's single-call source operators and the concrete consumer,
   then propagate repeated-input and storage faults together. The local sharp
   bound does not control those outputs or discharge controller admission.

## Credit

PR2540's complete native word and lifetime contract are ywz65's work, built
on PR2511/2512, Ali Romman's QQ16 lineage, thakrarsagar's L2 work and
starship-s's F0/cut decoder. PR2628 supplies the completed-child error model
and already demonstrates failed exact borrowed restoration in one call.
Its retained P104 error-method lineage is preserved in the copied proof.
This contribution adds the independent borrowed-write projection and sharp
reuse-horizon implication, not a new decoder or single-call sensitivity bound.
Nick Petalas. Apache-2.0; predecessor text is retained byte for byte.
