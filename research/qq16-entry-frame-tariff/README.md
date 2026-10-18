# The QQ16 decoder's separate entry-frame adapters

The complete local decoder in [ywz65's PR #2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540)
returns the original 224 logical arrays in the common physical frame `F_U1`.
Recovering the original physical entry frames with separate per-field adapters
has **minimum native rank mass 3,696**, attained by 112 rank-sixteen children
and 112 rank-seventeen children. This is a sharp tariff in the operation model
below, not a lower bound on a general controller or multiplication algorithm.

The endpoint is unchanged by [PR #2651](https://github.com/CrocSwap/integer-mult-bounds/pull/2651)'s
early-output-bank reuse. That result reduces banks and scalar operations; it
does not remove this particular endpoint conversion. A caller that accepts
`F_U1` directly has no obligation to perform our adapters.

| Desired physical frame of original x, y | Added child histogram | Native rank mass |
|---|---:|---:|
| Common `F_L`, `F_L` | 224 H8 | 1,792 |
| F0 gauges `F_L`, `F_L C_q^-1` | 112 H8 + 112 H9 | 1,904 |
| Original entry gauges `C_q`, `I` | 112 H16 + 112 H17 | 3,696 |

Here `Hr` means one rank-r native child. The decoder's existing added histogram
is `224 H1 + 16 H8`, mass 352. Appending the entry adapters gives
`224 H1 + 16 H8 + 112 H16 + 112 H17`, mass **4,048**. The inherited F0/B1
calls, wrapper execution, movement, hosting, precision and scalar work remain
additional charges. This is not a complete supplier budget or an improved κ.

## Boundary and operation model

The inherited [bridge contract](../joint-query/evidence/BRIDGE-REVIEW.md)
specifies `L=<e0,...,e8>`, `E1=<e9,...,e16>`, `U1=L+E1`, and initial
frames `C_(d q)` on X and `I` on Y at cover owner d. The actual 112 labels
q have odd binary weight and lie in L. The [retained decoder proof](sources/PR2540-PROOF.md)
specifies its output `F_(d U1)` on both recovered fields. The target here is
the original x and y in a chosen frame, not replaying F0 on their values.

Each terminal field is adapted independently, with arbitrary input content.
Allowed operations are translations and invertible linear permutations of
the binary payload address, and positive or negative canonical rank-r
convolution kernels, including their conjugates by those permutations. A
rank-r kernel is a product of r independent native line factors. Products
of arbitrarily many allowed operations are permitted; rank mass is the sum
of their native child ranks. Payload-independent nonzero global scalars can
also be allowed without changing the proof.

Cross-field mixing, borrowed observations, clearing input data, shared
multi-field children, payload-dependent phase masks, changing cover owners,
and fusion into the decoder or a later consumer are outside this model.
In particular, arbitrary monomial Clifford wrappers must not be declared
free here. Only the stated affine address operations are free in the lower
bound. The construction gives explicit affine wrappers, whose physical
execution still needs payment. These adapters act in place on each owned
output bank without helpers or scratch.

## Proof of the tariff

Write `C_a=((1+i)I+(1-i)T_a)/2`. On Fourier character u it has multiplier
`i^(a dot u)`, where the binary dot product is 0 or 1 as an integer. A signed
line product and a translation therefore have phase

```text
p(u) = sum_j sign_j * (a_j dot u) + 2*(delta dot u) mod 4.
```

Normalize any constant phase to zero. There is a symmetric binary matrix B
with

```text
p(u+v) - p(u) - p(v) = 2 u^T B v mod 4,
B = sum_j a_j a_j^T over F2.
```

The line signs disappear modulo two; translations contribute zero to B.
Under an invertible linear change of payload coordinates, B changes by
congruence, so its rank is invariant. Phase multiplication adds the matrices.
Moving all linear permutations to the end of a word expresses its phase
matrix as a sum of congruences of its child matrices. The final permutation
must be identity to implement the required convolution on arbitrary data.
A rank-r child has phase matrix rank r. Subadditivity of matrix rank gives

```text
rank(B_target) <= sum of child ranks.
```

For the original entry endpoint the required multipliers are
`C_q F_U1^-1` on X and `F_U1^-1` on Y. Their matrices on U1 are respectively
`I17 + q q^T` and `I17`. Since `q dot q=1`, the first matrix has kernel
exactly `<q>` and rank 16. The second has rank 17. Identity spectators add
zero blocks. For the F0 gauges the matrices are the E1 projector and that
projector plus `q q^T`, of ranks 8 and 9. The common-F_L case has rank 8 on
both fields. Summing over the 112 independent ports proves the lower bounds.

The source's first idle child gives orthonormal axes `a1,...,a16` and a
translation delta satisfying the complete, phase-sensitive identity

```text
F_U1 C_q^-1 = T_delta * product_j C_aj.
```

Its inverse is

```text
C_q F_U1^-1 = T_(delta XOR a1 XOR ... XOR a16) * product_j C_aj,
```

because `C_a^-1=T_a C_a`. This attains rank 16. The Y inverse uses the
17 coordinate axes and translation `e0 XOR ... XOR e16`. The F0-gauge
adapters use the eight E1 axes for X and `{q} union E1` for Y, again converting
every negative line to a positive line plus translation. The common-F_L
adapter uses the X recipe on both fields. [RESULT.json](RESULT.json) gives
all 448 entry/F0-gauge recipes and orthogonal wrapper columns on the 17 active
axes. Append the 56 fixed coordinate spectators for explicit 73-coordinate
charts. Conjugating a canonical rank-r kernel by this chart realizes each
positive axis product. No phase or sign is inferred from rank alone.

For common payload tensor length lambda, the target phase matrices are lambda
diagonal copies of these matrices. A rank-r tensor child contributes rank
`lambda*r`, even if the allowed permutations mix tensor layers. Dividing the
rank inequality by lambda gives the same child-rank tariff for every positive
lambda. The constructive identities tensor exactly. Applying owner d is an
invertible coordinate change, so the identities hold at every fixed owner.
This does not supply a physical traversal of those owners.

For `0 <= a < 1`, the same separate adapters minimize the unnormalized native
moment. If one field requires rank s and uses ranks r_j, then

```text
sum_j r_j^(1-a) >= (sum_j r_j)^(1-a) >= s^(1-a).
```

One rank-s child attains equality. At width m=73, the entry tariff is
`112*(16/73)^(1-a) + 112*(17/73)^(1-a)`. Appending the unchanged decoder adds
`224*(1/73)^(1-a) + 16*(8/73)^(1-a)`. These are native terms before any
caller normalization or other charges. They do not prove that the combined
word is optimal when fusion or a different output contract is permitted.

## Reproduce and evidence

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-entry-frame-tariff
```

The registered replay runs the exact verifier normally and with `-O`, plus
the artifact tests. No predecessor Python verifier is imported or executed.
The main verifier authenticates the source archive and the retained PR2540
proof, extracts the actual 112 port recipes, and compares complete Z4 phases
at zero, every unit vector and every two-bit vector. This is 154 determining
characters per recipe. Binary parity modulo four has degree at most two, so
these checks establish the full phase identity on the active 17 coordinates.
It checks 68,992 adapter phase values and 17,248 source-hole phase values,
all orthogonal wrapper charts and the lower-bound ranks.

Six semantic controls reject a wrong translation, omitted axis, understated
rank, equal-rank wrong subspace, inverse sign and duplicate axis. A separate
test compares exact Gaussian-integer convolution coefficients on all 131,072
addresses for the actual first-port entry-X adapter. This checks the physical
kernel, including its zero coefficients, rather than using the phase checker.
Other tests exercise source and result corruption, read-only replay and
overwrite refusal. Exact pins and the task/freshness record are in
[SOURCES.json](SOURCES.json), [PREDECESSORS.json](PREDECESSORS.json) and
[TASK.json](TASK.json). The source archive is an immutable historical geometry
input, not a claim to use its older supplier as today's frontier.

This is a written scoped proof with exact finite source-binding checks.
It does not independently re-prove the decoder, recertify its native kernels,
run the selected full cold replay, establish global controller compatibility,
or prove the full multiplication theorem. No selected record changes.

## Open next questions

1. Can a complete caller consume the recovered arrays directly in `F_U1`?
   Specify its exact input/output map and frames, then identify which of these
   separate adapters disappear. The blocker is a priced physical consumer,
   including restoration, rather than another logical inverse.
2. Can coupling fields or fusing the conversion with decoder instructions beat
   this separate-adapter tariff? First supply one exact dirty-input typed word
   with a smaller complete moment. Such operations fall outside this proof;
   this tariff does not exclude them.

These are bounded reopening tests, not a decision to expand the family.
Unknown hosting and caller costs remain unknown, rather than zero.

## Credit and engineering notes

Nick Petalas. Apache-2.0. Credit ywz65 for the complete native decoder and its
PR2511/PR2512 dependencies; commdata2338 for the parallel bank reuse;
Ali Romman for QQ16; starship-s, Sagar Thakrar and Ross Richardson for the
retained reconstruction/retention work; and the geometry, compiler, owner
and selected-supplier lineage in the unchanged
[joint-query notice](../joint-query/NOTICE.md). The retained PR2540 proof
is an exact source copy. Substantial AI assistance was used; no independent
human review or proof-assistant verification is claimed.

Build the Lever led to the rerunnable source-bound tariff checker. Foundational
Thinking led to signed binary-axis phases and explicit wrapper columns as the
data model. Prove It Works led to checking actual archived labels and complete
native phases. Test Behavior, Not Implementation led to public CLI mutation
tests and the separate convolution check.

Power-of-Ten review: the checker has no recursion, callbacks or subprocesses;
loops are bounded by authenticated 112-port data, 17 active axes, fixed
154-character sets, six controls and bounded metadata. Functions fit within
60 lines. Size limits and source authentication precede scientific parsing;
invariants use explicit exceptions and remain active with `-O`. Python allocates
managed objects during checking, a rule-3 deviation. Its live inputs are bounded
by a 20 MiB pinned archive, 1 MiB JSON members/receipts and a 1 MiB result;
there is no service loop or unbounded work queue. Archive decoder and Python
runtime allocations are inherited library behavior, not independently profiled.
Follow up with streaming or a fixed-capacity implementation if this fixed
112-port checker becomes a variable-size service. Warnings and compilation
checks run in the registered test command; no additional analyzer is installed
as a package dependency.
