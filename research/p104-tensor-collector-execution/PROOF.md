# Exact packed representation of the retained collector

This is an implementation refinement of a finite semantic evaluator. It does
not execute the conditional fast C-layer machine or change its tariff.
The original nonlinear order, both orientations, protected XOR calls and all
cleanup predicates remain in Jose Manuel's PR3131/3109 program.

## Representation and arithmetic

Let B be the payload bits per lane, R=2^B, S=2^(B+1), and N the number of
Gaussian coordinates. Represent each real and imaginary array separately as
`sum_i (x_i mod R) S^i`, with signed range `-R/2 <= x_i < R/2`.
The separator bit in every base-S digit is zero. Packing and unpacking are
bijections on that range. `Vector` is immutable; returning it from the source's
`list(values)` and snapshot operations preserves their value semantics.
The adapter does not expose element writes.

Write M for the repeated B-bit payload mask and O for the repeated unit bit.
Unsigned addition uses `(a+b)&M`. Each digit's sum is at most 2R-2<S, so
no carry reaches its neighbour. Subtraction uses `(a+(M xor b)+O)&M`;
each digit is at most 2R-1<S, so again there is no cross-lane carry or
borrow. These are addition/subtraction modulo R. The standard signed overflow
predicates `(a xor s)&(b xor s)&signs` for addition and
`(a xor b)&(a xor s)&signs` for subtraction reject exactly when a lane's
integer result is outside the signed range. Thus every accepted operation
is exact over Z, not a modular approximation. Negation is checked subtraction
from zero; in particular negating the most negative lane is rejected.

Arithmetic right shift by k retains each lane's low B-k shifted bits and fills
its top k bits with that lane's sign. It is exactly floor division by 2^k,
including negative odd inputs. Low-bit masking gives the nonnegative residue.
Left shift first masks each lane's top k bits before shifting, preventing
cross-lane contamination; it rejects unless arithmetic right shift reconstructs
the original value. A requested exact downshift additionally rejects a nonzero
residue. The mask-before-left-shift is essential: one separator is sufficient
for addition but not for an arbitrary unmasked left shift.

XOR acts independently on the represented B-bit words and agrees with Python's
signed XOR for operands and output in this range. Encoding to w bits is
accepted only when decoding the result reproduces the complete original
vector. Decoding rejects values outside the unsigned w-bit domain and
subtracts 2^w in lanes with bit w-1 set. These preserve the retained finite
signed-word headroom check. All these checks use explicit exceptions and
remain enabled under optimized Python.

B is chosen from a caller-supplied magnitude allocation plus 2n+16 bits and
rounded to a byte boundary with one separator. This is an implementation allocation,
not a new mathematical precision minimum. Every arithmetic intermediate is
checked. If this reserve is insufficient on another legal source invocation,
the adapter fails; it never silently wraps. The equivalence assertion is for
completed runs, together with the separately tested named finite domain.

## Butterflies, phases and source refinement

The address-bit mask for axis j selects the high member of every pair. Mask
and shift gather the low/high members into identical lane positions. Each
pair then executes the credited signed floor equations, or the credited ideal
numerator equations, using the checked operations above. The two disjoint
outputs are reinterleaved. Inactive lanes remain zero. Distinct valid axes
are required; the inverse reverses their order exactly as in PR3109. The
ideal numerator keeps its original axis order.

A character phase is a product of i or -1 factors selected by address-bit
masks. Quadratic factors select the intersection of two masks. Multiplying
these diagonal Gaussian rotations reproduces the original exponent sum modulo
four, including the multiplicity-scaled constant and inverse sign. The binary
affine compiler and its complete address-word schedule are unchanged.

`adapter.py` authenticates every input, then applies an explicit list of
count-checked representation substitutions. `CORE.evaluate` and
`CORE.inplace_block` retain all inverse, private-zero, source and split-field
checks. The only snapshot change is replacing a mutable-list copy by an
immutable vector value. The dense model retains `split_axes`, all block loops,
all backend calls, `address_word`, both wrapper executions in each direction,
and all collector checks. Its small executable-domain guard is widened from
n<=10 to n<=18, the precise extension attempted in PR3243.

The replaced pure primitives have the preceding componentwise proof. Each
remaining comprehension substitution is pointwise addition, subtraction,
quotient, residue or XOR on exactly the same operands. Each zero bank denotes
N Gaussian zeros. Structural induction on the unchanged call tree therefore
preserves every returned array and checked predicate on accepted executions.
No mathematical acceptance decision or intermediate computed array is cached.
Only immutable lane masks are cached. The count dictionary is compared to the
original executable on bounded fixtures and retained as an additional check,
not as a substitute for array equality.

## Verification boundary

The full-size comparison uses commdata2338's retained PR3243 column/parity
oracle, not these packed primitives. Every coordinate of entrance, sent,
returned and updated query arrays is compared before hashing. Five borrowed
sources and the entrance query are checked; private cleanup is literal zero.
This supplies finite implementation evidence and a written representation
argument, not a formal proof of the all-size multiplication theorem.

The actual fast physical backend, tape/control history, stock hosting,
all-size compiler refinement, other collectors and complete supplier remain
outside this check. The unchanged P104 consumer's 599/584 rejection remains;
verification speed does not remove any recursive-rank charge or improve kappa.

## Encoded words with implicit sign extension

The final adapter stores a w-bit encoded word by its signed representative,
plus an immutable width tag. If `E_w(x)=x mod 2^w`, then for signed w-bit
x,y, `D_w(E_w(x) xor E_w(y)) = x xor y`, where the right side is Python's
infinite two's-complement XOR. This follows bitwise below w, while all higher
bits are the XOR of the two sign bits. It also fits the signed w-bit range.
Thus encoding/decoding can leave the packed payload unchanged while retaining
and checking w. Every XOR verifies compatible tags; raw nonnegative encoded
targets are decoded with their declared width before entering this form.

The tagged representation is used only at the original word-XOR boundary;
Gaussian arithmetic always operates on decoded `Vector` values. An external
iteration over `Words` returns the original nonnegative encodings. This avoids
materializing 160 sign-extension bits at every protected oracle when the
actual fixture's integers are much smaller. It does not reduce the source
machine's word width, its space invoice or its headroom requirement.

For the final measured caller, the lane allocation uses the largest entrance
component bit length (at least eight), plus 2n+16 guard bits and the separator.
The checked-overflow rule applies to every intermediate; no
unchecked assumption about small coefficients is introduced. The declared
backend width remains 160 and is checked at every encoded boundary.

## The full-size expected receipt is not fitted to the packed run

The n=18 expected query, sent, source and entrance-query hashes come directly
from PR3243's retained promoted case. Entrance and returned hashes are plain
scalar gather and exact grid promotion; private zero is explicit. The original
compiler yields 26 wrapper gates per native direction, hence 52 gates and
104 protected address oracles. Four fast lifts per address oracle give 416.
Two original-order outer blocks give eight dense-linear oracles and another
16 fast lifts, for 432 total. In this named plan, two wrapper gates target
field zero and have no inner block. The other fifty gates give
`50 * 8 * 4 = 1600` inner oracle calls; the core's sixteen fast lifts add
64, giving **1664**. These counts are specific to the stated plan; they
neither represent physical runtime nor authorize dropping any invocation.
