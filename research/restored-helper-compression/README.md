# Compress restored helpers without changing the paid word

**Result:** an exact `k`-call scalar-idempotent word with `t` nonidentity
data targets and any number of exactly restored helpers can be realized
with

\[
 w=\operatorname{rank}_{\mathbb F_2}(V^TU)
 \le\left\lfloor\frac{k-t}{2}\right\rfloor
\]

helpers, while preserving every paid frame, call order, data component of
every scalar vector, and scalar pairing. Here `U,V` are the helper parts
of the call vectors `x_j,y_j`. The data endpoint is unchanged, and all
new helper registers return to identity on arbitrary inputs.

For three nonidentity data targets and five calls, **at most one restored
helper suffices**. Thus arbitrary restored-helper populations do not add
another width parameter to that five-call question. Citing David Govea's
[PR #720](https://github.com/CrocSwap/integer-mult-bounds/pull/720), which
excludes the zero-helper case for three invertible `2x2` targets, the
remaining restored-helper case uses four scalar registers. This is a
width reduction, not a new five-call construction or paid-call lower
bound. It changes no kappa, selected supplier, or retained assumption.

## Model and proof

A paid call is `I+([A_j]-1)x_j y_j^T`, over the binary group algebra of a
torsion-free additive exponent group. The coefficient `[A_j]-1` is
nonzero; `x_j,y_j` are binary vectors with `y_j^T x_j=1`. The endpoint is
an equality of whole matrices:

```
product = diag(d_1,...,d_t,I_r),    d_i != 1.
```

Correctness only on zero-initialized ancillas is insufficient. Arbitrary
nonidentity helper endpoints are also outside this surplus bound.
Original rational rank-one address frames remain unchanged. No target
flag, frame-span restriction, target commutativity or fixed address
dimension is needed.

[PROOF.md](PROOF.md) gives the complete argument. The ordered product has
`P-I=X H Y^T`, with invertible triangular `H` over the Laurent fraction
field. Because the endpoint update has precisely the data-coordinate
column and row spaces, `rank X=t+rank U` and `rank Y=t+rank V`.
Sylvester's inequality gives `rank U+rank V<=k-t`.

The compression quotients the span of the helper `x` components by the
directions invisible to all helper `y` components. It changes both sides
of the pairing together. This preserves all scalar contractions and
therefore the same ordered-product matrix `H`. Fixed left and right
projections then carry each zero data/helper cross block and the zero
helper update block to zero. Consequently the proof establishes the
whole new endpoint, not just its data block.

An arbitrary nonminimal replacement that preserves pairings can introduce
new helper output terms. The proof uses its particular quotient projections;
[REVIEW.md](REVIEW.md) gives an exact counterexample to omitting that step.

The number `w` is **minimal under the stated preservation contract**:
any smaller realization of all the same pairings would factor the same
matrix `V^TU` through fewer than its rank dimensions. It need not be the
minimum helper count among every possible word for the endpoint.

## Constructor and its preconditions

[compress.py](compress.py) exposes

```python
smaller_calls, helper_count = compress_calls(calls, data, registers)
```

Pass a finite list or tuple of calls. Each call is `(frame, x_mask, y_mask)`. The masks encode binary vectors;
the frame is retained unchanged. The constructor validates scalar
idempotence and dimensions, and computes a rank factorization of the
helper pairing matrix. It accepts opaque frames and does **not** certify
the old endpoint, nonzero address coefficients, or the count of
nonidentity data targets. Those hypotheses must be established before
applying the call-surplus bound. In particular, a zero-address call can
have a nonzero scalar pairing while its formal operation is identity.

The reference bit-operation cost is `O(r k^2+k^3)` and storage is
`O(rk+k^2)`. This is preprocessing for a word in the formal alphabet;
it is not a physical register-allocation or native-mixing invoice.

A nontrivial zero-helper example is

```
t=1, r=2:
(E11, 1, 1), (E22, 3, 5), (-E22, 3, 5).
```

Both original helper spans have dimension one, but they pair to zero.
The constructor removes both helpers, preserves the three frames and
data components, and keeps the endpoint `diag([E11],I_2)` on the original
roles and `[E11]` on the compressed data role. The verifier also supplies
examples with both helper spans of dimension two but paired rank one,
and examples attaining the `floor((k-t)/2)` bound.

## Reproduction and exact evidence

From the repository root:

```sh
python3 -I -W error -B research/restored-helper-compression/verify.py
python3 -I -O -W error -B research/restored-helper-compression/verify.py
python3 -B scripts/research_package.py --package research/restored-helper-compression --check-only
python3 -B scripts/research_package.py --package research/restored-helper-compression
```

[verify.py](verify.py) uses only the standard library. Its rank oracle
explicitly enumerates binary spans, independently of the kernel's
elimination. Its endpoint oracle multiplies matrices in the exact formal
binary group algebra, without using the proof's `X H Y^T` factorization.

| Check | Executed scope |
| --- | --- |
| Binary helper factorization | All 4,096 pairs of `2x3` binary helper matrices |
| Paired-rank distribution | Rank zero: 274; rank one: 2,058; rank two: 1,764 |
| General data-block identity | 64 predetermined legal three-call words, without assuming restored endpoints |
| Structured restored words | 16 cases, including sharpness, zero paired rank, two-sided invisible directions, a mixed nonadjacent commutator and a no-data cancellation |
| Nested inverse words | 64 bounded words with random rank-one `2x2` integer frames, seed `2026110617` |
| Rejection controls | Corrupted pairing, invalid idempotence, nonidentity helper output, counted identity data target, mutated cleanup frame, zero address update, and preservation of self-pairings alone |
| Separate review implementation | 448 factorizations through 65 helper bits; 181 complete Laurent-matrix words; 121 strict reductions; six counterexamples to broader claims |

The unrestored control is particularly direct: with `t=1,r=1`, calls
`(E11,1,1),(E22,2,2)` have paired helper rank one, whereas
`floor((k-t)/2)=0`. Their helper endpoint is `[E22]`, so they do not
satisfy the theorem. A zero-address helper call and an incorrectly
counted identity data target provide separate failures of other premises.

The primary normal and optimized modes print
`PASS_RESTORED_HELPER_COMPRESSION`. The separately implemented
[independent.py](independent.py) prints
`PASS_C_INDEPENDENT_COMPRESSION_REVIEW` in both modes and reports the
reviewed proof and constructor hashes. It uses its own rectangular binary
elimination and one-variable Laurent matrix oracle. The review was not
blind; the mathematical argument and code were supplied to the reviewer. These are finite corroborating
controls. The universal statement rests on the written proof. No
`120^5` word census or predecessor search engine is run.

[VERIFY.json](VERIFY.json) declares a self-contained replay.
[SOURCES.json](SOURCES.json) pins the cited sources as provenance; none
is a live scientific input to the verifier. The shared selected-baseline
attempt was blocked by a missing checkpoint certificate in the sparse
lead checkout. No selected-baseline PASS or full selected replay is
claimed here.

## Open next questions

1. Decide the four-register, five-call case for three invertible `2x2`
   targets, span three, and one restored helper. Begin with exact scalar
   symmetries and the two-relation/address-realizability conditions. The
   raw `120^5 = 24,883,200,000` ordered words are not a finished search
   plan. The broader arbitrary-nonidentity-helper question in
   [PR #4118](https://github.com/CrocSwap/integer-mult-bounds/pull/4118)
   remains outside this application.
2. Determine whether retaining only the contractions needed by increasing
   call paths permits a smaller realization than the rank of the full
   pairing matrix. Any proposed reduction still has to preserve legal
   scalar idempotence and every endpoint block; matching self-pairings
   alone fails an explicit control.

The complete original seed-68 card and scope refinement are retained in
[TASK.json](TASK.json). This package supplies no native implementation,
physical cleanup tariff, supplier admission, complete multiplication
result, human acceptance, or proof-kernel verification.

## Credit and license

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance,
including separate proof/kernel and independent verifier work. New work
is **Apache-2.0**. Credit eumemic's #288 model; Ali Romman's #468 ordered
rank factorization; waynenilsen's arbitrary-register dirty-auxiliary
arguments; David Govea's #720 zero-helper result; and unpaidmoon's #4118
remaining block question. The source metadata confirms the #720 and
#4118 attributions. Classical rank inequalities and bilinear quotients
are not claimed as new. The contribution is the preservation of the
complete restored endpoint together with the explicit call-surplus
bound and its bounded-width application.
