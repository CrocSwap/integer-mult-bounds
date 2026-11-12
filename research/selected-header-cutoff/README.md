# Generate the selected cutoff from its actual encoded root header

This package closes one input edge of the published fixed-tape complex
controller: it reads **Gamma(p)Gamma(d)** from the retained layer header,
produces the exact capped cutoff, executes the unchanged controller, and
retires the generated cutoff. Every header/WIDTH input and all eleven tape
heads are restored; marker preparation, arithmetic, copies, erasures and
returns are literal counted instructions.

The selected stopping exponent is **1/Q with Q=10^14**. It is the `stop=g`
parameter in the accepted gate, distinct from the outer exponent `be=1-3g`.
For existing unary active width e, the generated cutoff is

\[
C=\min\!\left(\left\lceil d^{1/Q}\right\rceil,e+1\right).
\]

All descendants have width at most e, so this cap preserves every stopping
decision, paid-child order and remainder hook of the source controller.
**No new kappa; all five foundational assumptions remain retained.**

## Literal implementation and complete budget

`cutoff_prefix.py` emits only local-symbol read/write, unit head moves, goto,
stationary event labels and halt. Its execution uses no host integer or host
recursion. It skips Gamma(p), converts Gamma(d) to unary by local doubling,
then tests t=1,2,... up to the first t^Q>=d or sentinel e+1. Binary exponentiation
is unrolled for fixed Q at compile time; each multiplication is a physically
streamed unary product saturated at d. The program initializes its own private
guard markers and erases them before complete return.

Let h=|Gamma(p)Gamma(d)| and R_Q=bit_length(Q)+popcount(Q). The [all-input
proof](PROOF.md) gives

\[
T_{\rm total}\le 200(P+1)\sum_v e_v
+1000(R_Q+1)(h+dC+1).
\]

Additional historical backing is bounded by

\[
(5+N/(N-1))e+5d+4h+40
\]

beyond entry history K0. **Unary d leaves O(d) retained backing after
erasure, even when e is small.** This storage is explicitly charged.

The actual selected gate also has epsilon=1-1/Q and d=O(p^epsilon). Hence
dC=O(p^(1-1/Q^2))=O(p). The complete prefix and retirement fit O_Q(p)=O_Q(V),
since the admitted nonempty record already has w>=p+2 and V=2Mrw. This uses
the coupled selected parameters; epsilon<1 alone would not justify this
unary implementation for every possible cutoff exponent.

For selected Q the prefix has 5,649 instruction locations on eleven tapes.
Its composition with N=3,P=2 has 5,951 locations and six symbols. N=3,P=2 is
a bounded demonstrator; the actual final selected N/P and owner manifest are
not materialized. The theorem is uniform over fixed N,P under the published
controller contract.

## Reproduction

Python 3.10+ and the standard library, from the repository root:

```sh
python3 -B research/selected-header-cutoff/verify.py
python3 -O -B research/selected-header-cutoff/verify.py
```

Expected status: `PASS_SELECTED_HEADER_CUTOFF_PREFIX`. Normal and optimized
receipts agree exactly. The bounded replay contains 357 parameter cases,
27 exact-power boundary cases, seven selected-Q cases, 204 direct saturated
product checks and six runs with a separately implemented dense interpreter.
The main cases execute 3,573,948 transitions and 1,324 selected-control nodes.
Thirteen controls reject wrong header return, cap equality, perfect-power
strictness, decoder arithmetic, saturation, retirement, exponent, time bill,
forgotten unary-d history and corrupted frozen source, plus invalid fixed
exponents. Translated origins carry opaque hostile ancestors.

Finite tests corroborate written loop invariants and all-input cost bounds.
They are not a formal proof kernel or full selected-payload replay. Test
fixtures construct encoded inputs outside the executing machine; no fixture
integer is read by a machine instruction.

## Source and dependency boundary

The base is `e54523517d0f03e58352e647c403a5af3e525a57`. `SOURCES.json` records
canonical source blob/length/SHA256 pins and exact predecessor code pins.
The two files under `inputs/` are unchanged copies from
[CubeJerry commit 9dfe6747b8553fd11b408f2b045c5954ef1e6eaa](https://github.com/CubeJerry/integer-mult-bounds/tree/9dfe6747b8553fd11b408f2b045c5954ef1e6eaa/research/selected-rank-control).
Their hashes are checked before import. Their selected program is relocated
and linked only at its completed halt edge.

The retained source already describes ordinary rational-power comparisons;
this is not a claim to invent integer roots. The new result is an explicit
source-bound prefix and completed-call composition with the actual encoded
header, complete costs and retained history.
[#6719](https://github.com/CrocSwap/integer-mult-bounds/pull/6719) and
[#6739](https://github.com/CrocSwap/integer-mult-bounds/pull/6739) retain credit
for richer natural-root grant/payload production from supplied depth.
[#5515](https://github.com/CrocSwap/integer-mult-bounds/pull/5515) treats a
different QQ16 root-dependent cutoff.
[#5158](https://github.com/CrocSwap/integer-mult-bounds/pull/5158),
[#2310](https://github.com/CrocSwap/integer-mult-bounds/pull/2310) and
[#2386](https://github.com/CrocSwap/integer-mult-bounds/pull/2386) retain their
fixed-bank and paid-controller credit.

## Remaining obligations and credit

Header validity, the already supplied active WIDTH from Q0 reservation, row
grants, the actual final paid-site/owner manifest, and payload/remainder
consumers remain inherited. The prefix does not implement the entire root
dispatcher or discharge native_all_columns, owned_erasure, compiler,
precision_tape or analytic_recovery. The selected conditional kappa remains
0.00363005817.

Prepared for @CubeJerry with substantial OpenAI assistance. Credit the
published selected-rank-control authors and the retained physical lineage,
including JoyboyBrian, thu-nmrc, ToikY, commdata2338, Ali Romman, David Arias
and Jose Manuel. New material is Apache-2.0; frozen source headers are
preserved. Independent human or formal-kernel acceptance is not claimed.

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
