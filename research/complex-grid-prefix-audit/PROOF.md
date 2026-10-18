# Exact-grid prefix audit of the pending complex layer

This note independently checks the word-arithmetic implication in section 6
of Jose Manuel's PR2287, at commit
`8c60765b5dea9d862b3b190d55da102a576031bf`. Its objects are the actual
`Grid` operations in `arithmetic.py` and the charge in `bounds.py`.
The selected supplier, recursive construction and large guard constants are
the predecessor's work. We find no arithmetic counterexample to that
implication under the hypotheses below. The proofs here quantify over word
widths and dyadic inputs; finite checks in this package are regression
evidence, not their proof.

Gareth Davidson's PR1282 (`research/complex-signed-prefix-audit/PROOF.md`,
section 2) already establishes unsigned-Horner multiplier monotonicity and
the need to include coefficient scratch in a prefix norm. We credit that
prior argument. The following application checks PR2287's later literal
bit-word routines and their denominator, shift-extent and grid conditions;
it does not claim a new Horner technique or recompute PR1282's R480 maxima.

## 1. Encoding and exact shifts

Fix integers `p,t,Delta >= 0`. A Gaussian value has height at most `t` when
it belongs to `2^-(p+t) Z[i]` and its complex absolute value is at most
`2^t`. A real arithmetic temporary has the analogous component bound.
This distinction matters: separately stored real and imaginary workspace
words need not form a simultaneous logical Gaussian value.

Set `F=p+Delta`. A signed `w`-bit two's-complement word encodes the real
value `N/2^F`, where

    -2^(w-1) <= N <= 2^(w-1)-1.

Suppose every real component and arithmetic temporary under consideration
has height at most `H`, with `H <= Delta`, and

    w >= F+H+2.

Then `N` is an integer, `|N| <= 2^(F+H)`, and both signs are representable,
strictly below the absolute overflow threshold `2^(w-1)`. Addition and negation whose ideal results
obey this bound therefore pass the source's signed-overflow guards and
produce the exact ideal word. This includes zero and excludes the sole
problematic two's-complement negation, the most negative word.

For an input of height `h`, its encoded integer is divisible by
`2^(Delta-h)`. In particular, if `h+k <= Delta`, exact division by `2^k`
discards only zeros. Arithmetic right shift with sign extension implements
the quotient even for negative inputs. The source's `0 <= k < w` condition
also follows for nonnegative `k`: `k <= Delta < w` under these hypotheses.
Thus the literal `Grid.divide` guard and its bit operation implement the
rational division.

For a shift satisfying `0<=k<w`, the necessary and sufficient exactness
condition for that word is `2^k | N`. Divisibility alone does not establish
the shift-extent guard: even zero must satisfy `k<w`. The rule
`h+k<=Delta` is sufficient, not a necessary height-based test for every
value. Completed cancellation can restore extra divisibility.

PR2287 chooses `F=p+Delta` and `w=p+2Delta+3`. Consequently a genuine
all-prefix height bound `H <= Delta` has more than the sufficient signed
headroom above. This lemma does not itself establish that all-prefix bound.

## 2. The actual Horner scale and scalar ADD

Let `c=n/2^k` be a reduced dyadic rational, `k >= 0`, and put
`b=bit_length(abs(n))`. For nonzero `n`, `b >= 1` and

    |n| < 2^b,              1+|n| <= 2^b.

In `Grid.scale`, the unsigned Horner multiplier starts at zero, doubles
at each binary digit, and optionally adds one copy of the input. Every
intermediate multiplier is a nonnegative integer at most `|n|`: the
doubled prefix is at most the next full prefix, which is at most `|n|`.
The optional final negation changes no absolute value. All these words
therefore have denominator dividing `2^(p+t)` and absolute value less
than `2^(t+b)` when the input has height `t`.

The final division introduces at most `k` denominator bits and decreases
absolute value. Every real temporary of the scale thus has height at most

    t + max(b,k).

For the completed Gaussian `scalar_add(a,x,c)`, assume both inputs have
height at most `t`. The final value has denominator dividing
`2^(p+t+k)` and

    |a+c*x| <= (1+|n|/2^k) 2^t <= (1+|n|) 2^t <= 2^(t+b).

Thus the same bound covers all its word temporaries and completed Gaussian
output. It also covers `scalar_scale`. If `n=0`, reduced form has `k=0`
and `b=0`: the source's zero Horner iteration stays zero, and ADD returns
the target. The bound remains valid without a special positive charge.

The actual `bounds.scalar_charge` assigns

    2*b + denominator.bit_length() + 3 = 2*b+k+4

to each scalar ADD or SCALE. This is at least `max(b,k)`, including the
zero case. It conservatively covers the actual Horner intermediates,
final division and ADD; it is not merely a bound on the final multiplier.
No sharper reserve constant or supplier improvement is claimed here.

## 3. One C kernel and its inverse

For Gaussian inputs `a,b` of height at most `t`, `Grid.pair` forms

    P=a+b,       Q=+i(a-b) or -i(a-b),
    outputs=(P+Q)/2, (P-Q)/2.

The intermediate complex values `P,Q` have modulus at most `2^(t+1)`;
the numerators `P+Q,P-Q` have modulus at most `2^(t+2)`. Their real
component words satisfy the same bounds. Before the final shifts, their
denominators still divide `2^(p+t)`; after them they divide
`2^(p+t+1)`. Hence every arithmetic temporary has height at most `t+2`.
Each completed C or inverse-C output has height at most `t+1`: its
absolute row sum is `sqrt(2) <= 2`, and its coefficients are Gaussian
integers divided by two.

The distinction is real. For `p=3,t=0`, take

    a=(5-5i)/8,       b=(5+5i)/8.

Both inputs lie in the unit disk. The forward first numerator `P+Q=5/2`
exceeds `2^(t+1)`, although the returned first output is `5/4` and has
height at most `t+1`. This refutes using the completed endpoint height as
an all-prefix height bound. It is not a counterexample to PR2287's larger
prefix allowance or its additional signed headroom.

After `u` elementary axes, completed C-tensor or inverse-C-tensor outputs
have height at most `t+u`. Applying the preceding temporary bound at each
axis gives the elementary sequential implementation an all-prefix bound
`t+u+1` for `u>=1`. In particular the predecessor's direct-leaf allowance
`t+8u` is sufficient for these arithmetic operations.

## 4. The closed normalization routine

Write `D=2j+o`, where `o` is zero or one, and let `b0=(1-i)/2`. The source
`normalize_b` implements

    b0^D = (-i)^j 2^-j b0^o.

For odd `D`, its real numerators `x+y` and `y-x` have absolute value at
most `sqrt(2)|z| <= 2^(t+1)`. Their division by two gives exactly `b0*z`,
whose modulus is `|z|/sqrt(2)` and whose denominator gains at most one
bit. Quarter phases preserve denominators and modulus. The final shift
by `j` gains at most `j` denominator bits and decreases modulus.

Every component temporary and the completed output therefore have height
at most

    t+j+o = t+ceil(D/2).

For `D=0` this is `t`, as the source performs only zero shifts. The
completed modulus is exactly `2^(-D/2)|z|`. This is an arithmetic statement
about this routine; it does not certify the surrounding Fourier identity,
phase evaluation, layout or complete layer.

## 5. Child returns: a bound may improve, the representation must remain

For every `p>=0`, the input pair `(2^-p,0)` followed by one forward C
axis and its inverse is an exact identity. The intermediate pair is

    (2^-(p+1)(1+i), 2^-(p+1)(1-i)).

It needs one extra fractional bit although the completed composition
returns to height zero. On a root grid with `Delta>=1`, the inverse
restores the original divisibility. Truncating both components toward
zero to only `p` fractional bits at the intermediate return instead
produces zero, so the inverse returns zero. This is an all-`p` family,
not an empirical failure at one selected precision.

In a recursive execution, a proved completed-child endpoint may therefore
replace an internal height bound by the smaller endpoint bound at return.
This is an update to the analysis, justified by the exact operator identity.
It does not change the common grid or round the stored word. Subsequent
operations may use the restored divisibility. Conversely, an endpoint
identity alone supplies no bound on the unfinished child's prefixes.

## 6. What this establishes, and what remains assumed

Together these lemmas give a source-level bridge: if the ideal chronological
execution has the asserted all-prefix height bound, the pinned word
operations, conservative scalar charges and a sufficiently wide common grid
simulate it exactly, provided every executed shift also satisfies `0<=k<w`.
An all-prefix value bound alone does not imply this syntactic extent condition:
zero divided by an arbitrarily large power of two still has height zero.
The sufficient rule `h+k<=Delta` in section 1, or a reserve dominating the
scalar denominator increments and normalization shifts, supplies both
divisibility and valid shift extent. Completed-child cancellation requires no rounding or
re-encoding. We find no contradiction in this arithmetic bridge.

The predecessor must still justify that its actual complete program obeys
the claimed recurrence

    A(e) <= A(48f) + s*f + E,       f=floor(e/73),

including all executed scalar operations, kernel prefixes, calls, remainder
work, normalization and every parked live value. In particular, charging
only a completed endpoint cannot replace the unfinished-child term. The
source's unnormalized rank mass, cover multiplicity, chronological schedule
and `E` allowance are premises for that composition, not consequences of
these primitive lemmas. Exact integer checks of `2B+18<C0` certify the
inequality only after those premises hold.

This note does not independently establish the full recursive compiler,
native monomial interpretation, hosted operator identities, row borrowing,
tape locality, all-size time bound, complete payload execution, selected
frontier or multiplication theorem. It preserves Jose Manuel's construction
and its credited supplier lineage. Prepared for AAAmirinu with substantial
OpenAI Codex assistance; no independent human or formal-kernel review is
claimed. New text is Apache-2.0, as in the repository.
