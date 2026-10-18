# Paid nonlinear repair of quadratic dirty readers

**Recursive-interface research construction and scoped repair bound; no new κ.**
Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance in
mathematics, implementation, verification and writing. New material is Apache-2.0.

An eight-call quadratic-reader batch can replace eight source restorations by
two paid source frame changes and one paid product correction. The frame changes
also restore the source. The literal exact scalar bill is **32 → 31**; a backend
with expensive product children may lose instead. This is a boundary option for
fixed calls, not an admitted supplier or an optimized squaring algorithm.

## Exact interface and result

Work over the rationals, with arbitrary incoming values of three distinct
length-`N` streams `y,a,b`. Every operation is componentwise. Child `i` is fixed:

```
y += beta_i * a^2       # observes a before this child's source drift
a += alpha_i * b
```

Eager execution immediately restores `a -= alpha_i*b` after each child. Its
terminal map is `(y + sum(beta_i)*a_entry^2, a_entry, b_entry)`. Deferred
execution retains all original children in order and repairs only at the exit.
There is no feedback from `y`, adaptive choice of coefficients, external source
write, or intermediate observation of `y` or `a`. `b` is read-only. These
sources are intended arguments of the observer: this result does not make the
output independent of arbitrary borrowed-source dirt by itself. Private scratch
of any substituted child backend must be restored by that backend.

Let `p_i = sum_(j<i) alpha_j`, and define

```
A  = sum_i alpha_i
S1 = sum_i beta_i*p_i
S2 = sum_i beta_i*p_i^2.
```

After the unchanged children, `a = a_entry + A*b`. Expanding each square shows
that the output defect relative to eager execution is exactly

```
Delta(a_entry,b) = 2*S1*a_entry*b + S2*b^2.
```

This identity is proved by expansion for every rational input and every finite
batch; the finite census corroborates the implementation. The predecessor's
linear matrix defect alone cannot certify this nonlinear interface.

For `S1 != 0`, set `t=S2/(2*S1)`. Append precisely

```
a += (t-A)*b
y -= 2*S1*a*b
a -= t*b
```

The first shift puts `a` in the entry frame `a_entry+t*b`, so the product
subtracts `b*(2*S1*a_entry+S2*b)`. The last shift restores `a_entry`. Both
frame changes and the correction are executed and paid; a separate restoration
followed by a correction gauge would be redundant. Every output and source has
the eager terminal value, and negating the coefficients in reverse event order
is an exact inverse on arbitrary dirty inputs. If `S1=0`, restore `a-=A*b` and
subtract `S2*b^2`, omitting only operations with exactly zero coefficients.

## A sharp restricted repair bound

The symmetric matrix of `Delta` is
`[[0,S1],[S1,S2]]`, with determinant `-S1^2`. If `S1 != 0`, its rank is two.
Hence no linear output correction suffices, and **one signed square of a linear
form cannot repair it**: such a square has matrix rank at most one. Source
changes consisting only of invertible linear shears do not alter this argument.
This bound concerns an appended additive correction, preserving the original
reader calls and target coordinates. It does not allow output-dependent source
updates, edits inside children or changes to the intended terminal map.

Two square queries suffice over the rationals. Let
`u=(S2/S1+1)/2`, `v=u-1`. Then

```
Delta = S1*((a_entry+u*b)^2 - (a_entry+v*b)^2).
```

From the final drifting source, use shifts `u-A`, `-1`, `-v`, with square
corrections `-S1` and `+S1` between them. The verifier executes this alternative
too. The minimum appended square-query count is therefore exactly two when
`S1 != 0`, one when `S1=0,S2!=0`, and zero for zero defect, in the stated
linear-frame/additive-square-repair class. The one-product repair meets the
corresponding one-nonlinear-query floor in a richer bilinear alphabet. Neither
statement is a global arithmetic-circuit lower bound.

## Complete cost and the seed-selected pilot

Assignment seed **55** was drawn once with OS randomness using
`secrets.randbelow(100)`. It selects the recursive-interface track and
`r=2+(55 mod 7)=8`. In the pilot, `alpha_i=beta_i=1`:

```
A=8, S1=28, S2=140, t=5/2
repair: a -= (11/2)*b; y -= 56*a*b; a -= (5/2)*b
```

The counted backend is explicit exact scalar-expression evaluation: a signed
unit ADD costs one, a square or product accumulation costs one multiplication
and one ADD, and every nonunit coefficient costs an additional multiplication.
Constants are compile-time rational parameters, not uncharged data operations.
No clean stream, copy, routing permutation, free frame relabeling or omitted
inverse is used. Source restoration is included in the two repair shifts.

| Complete eight-call batch, per position | Eager | Product repair | Square-only repair |
|---|---:|---:|---:|
| ADDs | 24 | 19 | 21 |
| Square multiplications | 8 | 8 | 10 |
| Cross multiplications | 0 | 1 | 0 |
| Nonunit coefficient multiplications | 0 | 3 | 4 |
| Scalar operations | **32** | **31** | **35** |
| Data reads / writes | 48 / 24 | 39 / 19 | 42 / 21 |

For arbitrary complete backend prices, write `L(N)` for a unit source ADD,
`C(N)` for an extra nonunit coefficient multiplication, `Q(N)` for a complete
unit-coefficient square accumulation and `P(N)` for a complete unit-coefficient
product accumulation. The all-positive `r>=2` family has the exact tariff

```
E_r(N) = 2r*L(N) + r*Q(N)
F_r(N) = (r+2)*L(N) + r*Q(N) + P(N) + 3*C(N).
```

The correction has two nonunit source coefficients and one nonunit product
coefficient at every integer `r>=2`. All `r` original square children and the
extra product child remain charged. Deferral helps exactly when
`P(N)+3*C(N) < (r-2)*L(N)` in this implementation. In the scalar backend,
`L=C=N` and `Q=P=2N`, so `E_r=4rN`, `F_r=(3r+7)N`. It first strictly improves
at `r=8`, ties at seven and loses below seven. This is a cost boundary, not an
impossibility result for different coefficient circuits or backends.

Each shift/square event reads its two named data values once and writes its
target once. A product reads three values once and writes once. Nonunit scaling
uses an already read scalar; it is still a paid arithmetic operation. Logical
event descriptors have four fields (kind, target, source, coefficient), or five
for a product. At the pilot there are 96 eager versus 77 repaired descriptor
fields per stream position. An addressed-machine bill adds separate prices for
these reads, writes, descriptor reads and dispatches. A separate scalar
interpreter observes every addressed read and write on all 15 priced arities;
an extra-read control preserves the mathematical endpoint but fails the invoice.
Inverse execution has
identical counts. Rational constants and ordinary expression temporaries are
not a proof of a reversible multiplication-child or fixed-tape lowering; their
complete backend scratch, precision and transport costs must enter `P,Q,C,L`
before invoking those interfaces.

## Implemented recursive composition and its full recurrence

`tree_events` supplies a precise recursive program, rather than extrapolating a
node count. A depth-`d` node of length `N=2^d` first calls two depth-`d-1`
children on the two contiguous output halves. Then it executes its complete
eight-reader batch on its own two source streams. Each active level has distinct
arbitrary dirty `a,b` streams, partitioned between siblings; output `y` is
shared. Children do not touch their parent's sources. Every local batch is
restored before its exit, so its proven endpoint composes by induction.
The identity depth-zero leaf has no events, a concrete convention of this
experiment rather than an unimplemented multiplication backend.

For the literal scalar backend, the full recurrences are

```
E_0(N)=F_0(N)=0
E_d(N)=2*E_(d-1)(N/2)+32N = 32Nd
F_d(N)=2*F_(d-1)(N/2)+31N = 31Nd.
```

Replacing the node tariff by its backend expression gives
`T_d(N)=2*T_(d-1)(N/2)+E_8(N)` or `+F_8(N)`, with every square/product
backend invocation included. The two recursive children are additional work;
the shell's square/product calls are not silently substituted for them.
This construction is an explicit multi-level boundary experiment, not a
contracting supplier recurrence or an exponent improvement.

There are `J=2^d-1` internal nodes and `2J` recursive edges. Data storage is
exactly `(2d+1)N` arbitrary initial scalars; no source is initialized to zero.
For `d=3,N=8`, the emitted programs pay **768 → 744 scalar operations** and
use the same 56 dirty data scalars. Event/materialized descriptor storage,
arithmetic, reads, writes and dispatch are in the certificate. Preparing this
literal word takes linear work in its emitted size plus the tree traversal;
an end-to-end bill must charge that preparation, `2J` call dispatches, memory
reservation and address arithmetic separately. The interpreter uses ordinary
indexed arrays. No physical tape-head traversal, controller encoding, hosting
admission or actual bit-complexity speedup is claimed.

For integer source inputs of magnitude at most `M`, a forward pilot source is
bounded by `9M`, and its repair frame by `(7/2)M`. The output can temporarily
contain quadratic terms of size `O(r^3 M^2)`; repaired endpoint size alone is
not a valid precision budget. The certificate records exact coefficient
one-norms and stored-coefficient denominators at every abstract event prefix.
These describe symbolic stream states only, not lower-level product temporaries
or a rounded-error theorem. Exact rational execution here requires no rounding.

## Reproduce, completed coverage and controls

From the repository root, Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/quadratic-reader-restoration
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/quadratic-reader-restoration outcome=completed`.
The registered command runs a relocated optimized replay and five on-disk
corruption rejections. Direct standalone replay also works without Git:
`python3 -I -O -B research/quadratic-reader-restoration/verify.py`.
`--emit` prints a newly recomputed certificate without writing files; ordinary
verification compares every field of [CERTIFICATE.json](CERTIFICATE.json).

The bounded domain is all **1,364** signed batches of lengths 1 through 5,
`alpha_i,beta_i in {-1,+1}`, and all 27 dirty triples in `{-1,0,1}^3` per batch.
Both product and square-only schedules, eager execution and their literal
inverses are checked. A separately implemented sparse rational-polynomial oracle
checks every coefficient, including mixed terms, without importing a predecessor
checker or the defect formula. Additional evidence covers all-positive arities
2 through 16, genuinely rational coefficients, and four literal binary recursion
depths 0 through 3. Stopping rule: finish these fixed domains; no search outside
them or unrestricted circuit optimum is asserted.

Controls expose missing/wrong-sign repair, missing source restoration, a wrong
correction frame, unsafe intermediate observation and unpaid nonunit coefficients.
A pure mixed defect `4ab` agrees with the eager map on all three coordinate basis
inputs but fails at `(y,a,b)=(0,1,1)`. Thus the basis-only test valid for linear
interfaces is insufficient here. The package test rejects changed source bytes,
changed predecessor head, an unpaid coefficient certificate, an omitted product
and an incomplete census receipt. Relocation checks independence from the repo's
working directory and Git metadata; this is independent implementation evidence,
not independent human or formal verification of the full multiplication theorem.

## Provenance and relationship to other work

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected conditional
result at that base is PR1094, `κ=836330098538459/500000000000000000`.
Its source manifest, assembly, review and actual T16 construction were followed;
the source-binding baseline passes. [SOURCES.json](SOURCES.json) pins that context
and the originating task card as historical Git provenance.

Adam Gall's PR1205 (`e2008d7ffcad464da7ec21c69e8d8a8c91de4930`) provides the
exact linear observation criterion. Hanson Sun's PR1246
(`5ed1ce17a9df4c853a93f9758ba903d2620c3443`) pays nonzero linear reader repair.
Their complete notes and original attribution are retained byte-for-byte under
`context/`; [CONTEXT.json](CONTEXT.json) records source heads, published Git blobs
and SHA256 hashes. Those are recorded fetch pins, not a GitHub-history proof.
Aaron Wang/Navinor's PR1155 and the other predecessor credit in those notes remain
with their original authors. No priority is claimed for linear deferral or repair.
This adds the explicitly quadratic defect, sharp appended-square-query bound,
fused restoring product frame and separate nonlinear child tariff.

[CLAIM.json](CLAIM.json) records the seed, three candidates and local claim.
No pinned coordination issue was present. Fresh PR/Discussion searches found
no matching quadratic/nonlinear-reader term before the claim; title/body/comment
searches do not cover every code diff and cannot establish novelty. Final overlap
metadata and validation are recorded separately. No selected construction,
review-ledger disposition, frozen package or `upstream/` input is changed.

The selected all-size/compiler, mutable-source realization, whole-call hosting,
precision/tape, analytic transfer and bit H1–H5 assumptions remain. No selected
cold replay, native supplier replay, backend scratch theorem, hosted Linux result,
formal proof or new multiplication bound is supplied by this package.

## Open next questions

Does a supported supplier have indivisible nonlinear readers whose full repair
satisfies `P+3C < (r-2)L`? This matters because the extra product child can erase
the apparent restoration saving. First pin an actual child return map and price
its frames, private scratch, coefficient preparation, precision, transport and
hosting in the displayed tariff. The blocker is that no such admitted child has
been identified. If these toy reader calls may be opened, their endpoint is just
`y += r*a^2`, which can be evaluated with one square and one scaling; both
batch implementations are then needlessly expensive. The fixed-call assumption
is therefore essential to the limited saving reported here. Structured next
questions and the refined scope are in [TASK.json](TASK.json).
