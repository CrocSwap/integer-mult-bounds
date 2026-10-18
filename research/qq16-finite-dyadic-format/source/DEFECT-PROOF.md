# Completed-instruction defects for the zero-retention decoder

This lemma concerns ywz65's PR #2707 at
`efa51a6c7ffec6edd556a98deedfe9deeba65809`, specifically its unchanged
3,823-event [word](source/WORD.json). The retained [proof](source/PROOF.md)
establishes its ideal frame and logical semantics, building on Arham Tahir's
PR #2681. Those semantics are inherited here, not independently recertified.

## Norm and ownership contract

Fix any positive common payload tensor depth. For each full-cover array A,
write

`||A|| = max_owner ||A(owner)||_2`,

where the inner norm is the complex payload Hilbert norm. A signed native
line is unitary. Each affine full-cover map permutes owners and applies a
unitary payload permutation/translation. Consequently these ideal operations
are isometries in this norm at every tensor depth. Norm preservation, not
commutation or cancellation between these operators, is the only native
property the error argument uses.

All 224 supplied current X/Y arrays have norm at most B, with B > 0. They
may be arbitrary and are borrowed read-only. The 224 Z/W output banks and
at most sixteen F/G scratch arrays are owned, exclusive and may start with
arbitrary dirt. A first exact CLEAR initializes a field; uninitialized dirt
is excluded from the magnitude and error claims. No instruction may read
uninitialized dirt. Exact CLEAR also removes accumulated errors. All scratch
fields are exactly cleared before their private scope ends. No error or
side effect may affect a field other than the declared destination.

A completed `line` includes its signed native recipe and both monomial
wrappers. Its defect bound must hold for the complete instruction, not just
its positive child. Likewise, the cover-map contract includes its entire
owner/payload action. These are supplied caller assumptions, not physical
implementations proved by this package.

## Absolute completed defects

Let the corresponding ideal and implemented executions start with the same
supplied X/Y arrays. At every completed ADD, line or map instruction, allow
an arbitrary additive vector error in its destination, measured in the norm
above. The defect can depend on state and previous errors. Suppose its norm
is at most `eps_add`, `eps_line` or `eps_map` according to instruction type.
CLEAR and the scope/checkpoint markers are exact. Then every initialized
field at every cut satisfies

`error <= 67401 eps_add + 32711 eps_line + 33464 eps_map`.

This statement includes errors in scratch before a later CLEAR. It is not
an endpoint-only estimate. The output fields can accumulate errors even
though the borrowed inputs have none. Final scratch is exactly zero.

The counts are 2,704 ADD sites, 336 line sites and 464 map sites. Thus there
are 3,504 permitted defect sites. The complete certificate covers 3,816
changed-field boundaries, including all 312 CLEARs. Every unchanged field
retains a previously checked bound; the 224 initial borrowed fields have
ideal load one and error zero throughout.

## State-relative completed defects

Here all norms in the local defect premise are norms of the actual
implemented operands immediately before that instruction:

- ADD `d += c s` has defect at most `u (||d|| + |c| ||s||)`.
- A completed line or map has defect at most `u ||d||`.
- Owned CLEAR is exact.

The ADD coefficients are the literal `+1`, `-1`, `+1/4` and `-1/4`.
These contracts do not assume linear, independent or unbiased errors.
For

`0 <= u < 1/199144`,

the all-cut error and magnitude satisfy

`error <= B * 2919388 u / (1 - 199144 u)`,

`magnitude <= 32368 B + B * 2919388 u / (1 - 199144 u)`.

In particular, for every integer b >= 0,

`u <= 2^(-b-22)`

suffices for strict all-cut error less than `B 2^-b` and magnitude less
than `32369 B`. Borrowed arrays are exactly unchanged, even with these
errors, because there are no instructions targeting X or Y. This differs
from the retained-record decoder's temporary borrowed native/inverse calls.
It does not permit approximate implementations to write to borrowed fields.

Twenty-two is the smallest uniform integer guard furnished by the displayed
majorant and local error premise. This is not a minimum for the actual
physical decoder, another error analysis or a component-rounding format.

## Exact positive recurrence

For each initialized field d, keep six nonnegative rational weights

`(p_d, j_d, k_d, a_d, l_d, m_d)`.

Initially every X/Y has `(1,0,0,0,0,0)`; other fields have no initialized
state. CLEAR sets all six weights to zero. For an ADD, first transfer all
six weights by `row_d += |c| row_s`, using the pre-event rows. Put

`alpha_i = p_d_before + |c| p_s_before`,

`beta_i = 1 + |c|`.

Then add `alpha_i` to j, `beta_i` to k and one to a. For a line or map,
leave the ideal row transfer unchanged and put

`alpha_i = p_d_before`, `beta_i = 1`.

Add `alpha_i` to j and one to k and to the appropriate l or m weight.
CLEAR has no defect injection. For the absolute-defect premise, induction on
the events gives `error_d <= a_d eps_add + l_d eps_line + m_d eps_map`.
An ADD transfers earlier errors with coefficient absolute value; each new
defect increases exactly its type's weight. A line/map is an ideal isometry,
and CLEAR resets the error. Taking the checked maxima proves the absolute
bound. Each scratch scope starts with independent arbitrary dirt and its
own initializing CLEARs; an earlier scope's cleared state is not silently
used as an initialized new input.

The triangle inequality and ideal isometry premise show that the p weights
bound ideal field norms by `p_d B`. The a/l/m weights bound the sum of
absolute local defects. No cancellation between different native operators
is used. The exact maxima in [RESULT.json](RESULT.json) are

| Weight | All-cut maximum |
|---|---:|
| p | 32368 |
| j | 2919388 |
| k | 199144 |
| a | 67401 |
| l | 32711 |
| m | 33464 |

All six maxima occur just after event 3807, the ADD `W0 -= Z0`. Event
indices are zero-based in the literal word. These are maxima of the
nonnegative triangle recurrence, not claimed attainable operator norms.

## Feedback proof

Let E be the maximum actual error over all initialized fields and the
finite sequence of cuts. Under the stated local relative premise, an ADD's
local defect is at most

`u [alpha_i B + beta_i E]`.

Indeed its implemented operands differ from their ideal operands by at most
E, and their ideal norms have the proved p bounds. The same inequality
holds for lines and maps with `beta_i = 1`. Propagation of these defects
through the nonnegative recurrence yields, at each checked cut,

`error_d <= u [j_d B + k_d E]`.

There are finitely many cuts, so their maximum exists. Taking the maximum
and using the independently checked maxima gives

`E <= u [2919388 B + 199144 E]`.

When `u * 199144 < 1`, subtracting the last term and dividing by the positive
denominator proves the stated bound. This argument also applies to
state-dependent coherent faults. It does not replace their premise with a
promise about an ideal operand's magnitude.

For `u <= 2^(-b-g)`, the sufficient guard condition reduces to

`2919388 + 2^-b * 199144 <= 2^g`.

The hardest b is zero. Exact integer arithmetic gives

`2^21 < 2919388 + 199144 = 3118532 < 2^22`.

This proves the uniform 22-bit statement, its strict margin and the failure
of the same sufficient test at 21 bits. A failed sufficient test is not a
physical lower bound or an exhibited 21-bit failure of the actual decoder.

## Independent checking and limits

The forward checker stores all six weights at every changed-field cut.
For every one of these cuts, a separately implemented adjoint traversal
starts with unit weight on its field and walks backwards through the
prefix. An ADD sends `|c|` times the destination covector to its source;
a CLEAR deletes the destination covector. A line/map leaves its norm
covector unchanged. At each defect site the traversal sums the covector
against alpha, beta and the type indicator. Surviving input covectors sum
to p. It matches all 22,896 forward certificate entries exactly. The alpha
loads themselves derive from p at prior boundaries, which this same
all-cut comparison checks. It is a reverse check of the arithmetic
certificate, not another independent native-semantic reconstruction.

The finite tests include noncommuting rational isometries, a real scratch
error erased at a later CLEAR, state/chronology rejection and optimized
CLI source/typed-receipt corruption. Those tests are regressions for the
written argument, not substitutes for its quantified norm proof.

The result is conditional on PR #2707's ideal semantics and the completed
instruction/ownership contracts above. It does not establish entry/F0/B1
precision, a local contract inside a recursive child, per-component rounding,
address or payload precision, retention/movement/control costs, physical
hosting, a valid output consumer, full supplier admission, a new kappa or
a multiplication theorem. Other decoder words do not inherit these numbers.

New lemma and checker by Nick Petalas. Predecessor notices and licenses are
preserved in the retained source snapshots. New material is Apache-2.0.
