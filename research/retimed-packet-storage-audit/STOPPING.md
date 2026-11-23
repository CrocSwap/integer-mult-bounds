# Source-bound stopping-control audit for the retimed supplier

Status: authored supplemental audit, cross-reviewed by the packet-audit agent. This is model-assisted review, not independent human acceptance. No new kappa and no removal
of a canonical foundational assumption are claimed. The main purpose is to
check the source-to-proof interface requested in #8042, rather than relabel
that PR's existing `OuterStop.lean` inequalities as new mathematics.

## Exact scope

The audited runtime is Ali Romman's #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. The resolved `positive.py`
provides `power_le`; `retimed_supplier.py` supplies the real recursive caller.
The seven-stage `RESOLUTION` profile in `installations.py` passes
`D = 10^21` through `band_product.production_supplier` to that caller.
Canonical selected main remains `e54523517d0f03e58352e647c403a5af3e525a57`.

Fix a nontrivial test at width e, with original root width h and carrier M.
The source short-circuits at e <= M. At a root, h=e. At a genuine recursive
child, e=floor(z/M), where the parent width z failed the stop test, so
h < z^D. In particular z < M(e+1). A nontrivial child has e>M, hence M<=e.
The complete field geometry retains at least e active binary coordinates,
so there are at least 2^e actual positions, with all spectator factors kept.
We use this actual field volume, not a helper-zero or normalized-volume credit.

**Claim.** On this domain the source predicate is exactly e^D<=h. There is
a fixed-tape serial-bit lowering of this predicate whose work and temporary
cleanup fit `2^32*(bit_length(h+2)+2)^3` elementary transitions. This is at
most one scan of 2^e positions whenever e>=1024 and the above root or genuine
child relation holds. The physical field/storage and entry-header contracts
remain premises; this local control audit does not prove the full runtime's
movement tariff or allocation history.

## 1. Exact capped arithmetic

At each exponent position, the algorithm stores the power of e capped at
h+1. It stores the exact product of selected powers as long as that product
is <=h, and rejects immediately otherwise. For positive integers, replacing
an intermediate factor greater than h by h+1 preserves whether any subsequent
positive product exceeds h. This proves the invariant and the final predicate
by induction on the binary exponent, including the equality endpoint.
The fixed D has 70 bits and 29 set bits, hence at most 69 squares and 29
selected multiplications. The path e=h=1 executes all 98 products.

The invariant is false with cap h: e=2,D=2,h=3 then falsely accepts. Replacing
the stop relation by strict less-than is also wrong at e=2,D=3,h=8. The checker
executes these semantic mutations or their exact witness predicates.

## 2. Sequential lowering with owned control scratch

Let W=bit_length(h+2). Current factors and the accepted running product fit
W bits, and each temporary product fits 2W+1 bits. The input and cap registers
are bounded strips with endpoint markers; h+1 is produced by a finite-carry
increment. A fixed number of strips suffice because one product strip is
cleared and reused before the next arithmetic operation. The 70 exponent
bits are fixed finite control, so their tests do not require growing-rank
random access or a growing exponent tape.

`verify_stopping.py` implements multiplication by Horner's rule, reading a
multiplier from its highest bit. For each bit, it shifts the whole product
strip left once and conditionally adds the multiplicand with a one-bit carry.
Each pass is a literal serial scan. After a prefix b' has been read, the
product equals a*b'; this proves correctness and absence of overflow by
induction, since 0<=a,b'<2^W. Inputs are restored with their original values
and heads. Comparison scans from low to high, retaining the latest differing
bit in finite control. Every product scratch strip is zeroed on both the
accept and early-reject paths. No input field or suspended parent is touched.

A product needs fewer than 64(W+2)^2 charged data reads, writes and unit head
moves, including initializing its bounded strip and input head restoration.
The bound follows by counting a shift pass and an optional addition pass
per multiplier bit; each has length at most 2W+1. Copy, comparison and wipe
are linear scans. Across at most 98 products and four registers these data
operations are below 2^20(W+2)^2. The checker corroborates these bounds; the
universal justification is the pass count, not extrapolation from its cases.

Endpoint tests and finite loop control can be implemented with at most 16
transitions per counted data operation. If binary loop indices are preferred
to endpoint markers, service each index with a complete scan of at most W+2
control cells, including restoration. Initial header/cap construction and
final control-strip removal have an additional bound 2^20(W+2)^2. Both
implementations therefore fit 2^32(W+2)^3. The code's tick receipt counts data
head operations only; it is not a claim that Python wall time or its big
integers themselves are that literal machine. The lowering is an available
implementation of the exact predicate and returns all its control scratch.

## 3. Why the root-sized limit fits a genuine child field

For a root, h=e and W+2<=e+4<=(3D+2)e. For a genuine recursive child,
M<=e and e+1<=2^e imply

    z < M(e+1) <= 2^(2e),    h < z^D < 2^(2eD).

Consequently h+2<2^(2eD+2), W+2<=2eD+4<=(3D+2)e for e>=4.
The exact integer coefficient satisfies

    2^32*(3*10^21+2)^3 < 2^256.

At e=1024, 2^256*e^3<=2^e. For every e>=4,

    2e^3-(e+1)^3 = e^3-3e^2-3e-1 >= 0.

Writing e=4+u gives u^3+9u^2+21u+3, which has nonnegative coefficients.
Induction therefore gives 2^256*e^3<=2^e at every e>=1024. Combining the
inequalities proves the claimed one-field-scan upper bound. The actual
nontrivial profile widths exceed M>=2^1024, much more than this sufficient
1024-axis threshold. The source's Lean theorems already prove the same
abstract volume comparison; this audit supplies its executable-caller and
serial-control bridge and independently checks its arithmetic.

The parent condition cannot be omitted. Taking e=5, M=2, z=11 satisfies
e=floor(z/M), but h=2^4096 has no comparable small control width. Such a
configuration is not reachable after a parent failed the test with D=3.
The checker rejects the bound on this deliberately inadmissible instance.
This control distinguishes the real descendant theorem from an invalid
claim about every independently chosen root-sized header.

## 4. Executed checks, coverage, and remaining obligations

Run `python3 -B verify_stopping.py --runtime RESTORED_RUNTIME` or the complete
`python3 -B verify.py` driver. The driver restores the hash-checked source offline. Expected marker: `PASS_STOPPING_CONTROL_AUDIT`.
The current receipt records 5,460 complete small serial products, 74,496
source-predicate comparisons with an independent repeated-multiplication
oracle, 371 lowered predicate cases, and 2,240 genuine child-relation cases.
Boundary cases include all-ones and power-of-two ceilings, equality, early
rejection, and the full fixed-exponent path. Every modeled historical
scratch strip is checked for zero and every input head is restored.

The checks corroborate the specified invariants and source binding. They
do not exhaust arbitrary widths or establish the universal theorem on their
own. They also do not validate the full outer recurrence, the seven ordinary
price constants, all-size header encodings, blank backing grants, or global
pending/answer storage; those remain separate obligations. The comparator
fits a local scan budget under the declared entry/field contracts, and the
separate packet audit studies its own named runtime invariants.

Credit Ali Romman for the retimed supplier, original stopping argument and
Lean inequalities, and the credited authors of the inherited positive
runtime. Prepared for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. Model-assisted cross-review is not independent human or formal
kernel acceptance.
