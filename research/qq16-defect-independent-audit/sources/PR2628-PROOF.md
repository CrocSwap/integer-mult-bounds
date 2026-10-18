# A local stability contract for the complete QQ16 decoder

This is an application of the Hilbert-defect/feedback method of PR2096,
PR2166 and PR2503 to the different, unchanged PR2540 decoder. Those P104
constants are not transferred. PR2603 gives exact dyadic caller grids and
real-component box bounds for this decoder; its children are exact. Here the
new object is propagation of arbitrary completed-instruction defects.

## 1. Domain and chronological premises

Use the byte-exact 2,463-event PR2540 word at commit
`630d557af5088f66b45c447969cee9576600e50b`. The retained verifier rebuilds the
word, checks its 240 temporal-input operator map, native kernels, full-frame
cover identities, complete invoice and twelve controls. New sensitivity
interpreters do not import its replay function.

An array is a field over the finite regular owner cover, with a complex
payload at each owner. Its norm is the maximum over owners of the payload
Hilbert norm. The payload may have any positive tensor depth. The norm is
not an addresswise component maximum and is not the Hilbert norm of the
concatenation of all registers.

There are sixteen earlier selected X1 input arrays and 224 current X/Y
input arrays. Treat these 240 temporal entries as independent, each of norm
at most B. This relaxation includes the genuine F0/B1 observations but
does not prove their bounds. The first sixteen capture ADDs can be inexact.
Their record errors survive the history boundary. At that boundary current
X/Y values are supplied as specified entries; the intervening B1 execution,
its errors, and retention errors are outside this contract. They are not a
free zero-cost step. Current-entry perturbations can separately be propagated
by the computed ideal input map, but are not included as instruction defects.

Owned outputs, retained banks and local scratch have the same explicit CLEAR
and lifetime semantics as PR2540. CLEAR is exact and may discard arbitrary
owned contents. Initial owned dirt and a newly allocated private field before
its first CLEAR are not bounded, but are never read. Statements about live
prefix states concern initialized fields and supplied borrowed entries.
Private-body scratch is local to an owner; representing all owners' separate
executions as a field does not grant additional full-cover storage or change
the inherited invoice. It is never routed during a private body.

At every completed ADD, native line/stage, and full-cover map, allow an
arbitrary additive defect in the written destination, measured after that
instruction. Each execution may select defects adversarially and as a
function of the actual preceding state. Addressing, frames, branch sequence,
wrappers and all other writes are exact. This is a local contract for a
completed child, not an implementation of such a child or its private work.

## 2. Why signed logical propagation bounds physical errors

For a binary translation involution X, the native line is

    C = (I+X)/2 + i (I-X)/2.

The two projectors are orthogonal, so C is unitary. Its inverse and tensor
powers are unitary too. All declared frames are products of commuting
translations' phase operators, hence unitary at every owner and depth.
The retained full-frame identities prove the actual cover maps become the
specified owner pullbacks in the common current frame. Their payload
translations and orthogonal owner maps are retained, not dropped based on
constant-vector tests.

Conjugate each physical defect at its injection boundary into that field's
logical frame. Its norm is unchanged. The same is true of every temporal
input and of the output frame at any later boundary. ADDs have matched
frames and act by their rational coefficients. A native frame change keeps
logical content fixed. A current cover map sends each row's owner operator
g to h g in the exact chronological order. No commutativity is assumed.

Thus each initialized prefix field has the exact operator expansion

    sum_(v,g) c[v,g] D_g v,

where v is one temporal input or one distinct injected defect, and D_g is
an isometric owner pullback. Terms with the same (v,g) are combined before
taking absolute values. For every field, the triangle inequality gives the
sum of absolute coefficients times the individual source norms. Different
g terms may cancel on a restricted subspace; the bounds below are therefore
claimed as certified sufficient envelopes, not attained operator norms.

The finite induction follows exactly the actual opcodes. A CLEAR removes
only its destination row; already propagated effects survive elsewhere.
The history boundary replaces only current X/Y rows, preserving retained R
errors. Private allocation creates no readable input; private retirement
checks all its rows have been cleared. This proves the expansion for all
payload sizes from a finite coefficient/owner computation.

## 3. Complete finite coefficients

There are 2,136 defect sites: 1,688 ADDs, 224 rank-one lines, sixteen
rank-eight stages and 208 full-cover maps. Every changed initialized field
is inspected, including all 224 replacements at the temporal boundary:
2,680 boundaries in total. Unchanged initialized fields keep their previous
bound. Supplied initial entries have coefficient one.

Let P be the maximum absolute row sum for temporal inputs, A the maximum
for defects of unit norm, and K the maximum for defects weighted by
`1+abs(a)` at ADD coefficient a and one at native/cover operations. The exact
signed coefficient computation gives

| Envelope | All initialized cuts | Final fields only |
|---|---:|---:|
| P | 240 | 121 |
| A | 1529 | 818 |
| K | 2298 | 1253 |
| Native defects only | 192 | 96 |
| Cover-map defects only | 280 | 140 |

All five all-cut maxima occur in local scratch F0 after zero-based event
1717. Each peak row has 2,545 nonzero input/defect-owner terms. Reverse
covectors independently reproduce all five peak rows and every final
borrowed/output row: 66,101 coefficient equalities. The complete forward
boundary table is bound by its canonical digest, and the unchanged ideal
endpoint agrees with the retained full routed decoder, not just samples.

For independent absolute defects bounded by epsilon, every initialized
prefix error is at most 1529 epsilon. For native-only or cover-only defects
the corresponding sufficient envelopes are 192 and 280. The exact input
trajectory has norm at most 240 B.

An actual invariant constant-owner/payload execution with signed unit
defects gives F0 error 841 at event 1717, exceeding the *entire final-field*
envelope 818. This is a concrete failure of substituting the final bound
for an interior bound, even though the conservative 1529 envelope is not
claimed attained. Independent literal scalar executions test nonzero faults
at all site kinds and a state-dependent relative-fault run.

## 4. State-relative feedback and sufficient precision allowance

At a native/cover operation require local defect norm at most u times its
actual input norm. At an ADD require at most

    u (norm(actual dst) + abs(a) norm(actual src)).

Let M be the largest initialized operand/result norm in this finite run,
including supplied entries. The weighted row bound gives error at most
2298 u M, hence

    M <= 240 B + 2298 u M.

When 2298 u < 1,

    M <= 240 B / (1 - 2298 u),
    all-cut error <= 551520 u B / (1 - 2298 u).

For every integer b>=0, `u <= 2^(-b-21)` implies `2298u <= 1/2` and
`2*240*2298 = 1103040 <= 2^21`; therefore all-cut error is at most
`B*2^-b`. The 21-bit guard is sufficient, not minimal, and is a bound on a
specified relative local-error parameter. It is not automatically an
addresswise fractional-bit format, especially when converting component
rounding to a payload Hilbert norm. PR2603's box-grid result and this norm
contract are separate obligations.

## 5. Restoration and remaining admission limits

An error introduced by the first native line survives in its borrowed Y
field after the nominal inverse. Borrowed restoration is approximate under
this contract. An error at the first C accumulator ADD reaches 56 final
outputs although C itself is later cleared; clearing scratch does not undo
its prior effects. Both are exact rational execution controls.

The exact owned CLEAR premise does allow the declared private retirement;
there is no claim that approximate inverse uncomputation would supply it,
that arbitrary borrowed fields may be erased, or that a physical machine
can discard for free. The original invoice remains unchanged and paid.

This is a source-bound local implication, not a changed decoder construction,
a physical rounded child, all-size supplier admission, a new recursive
profile or kappa. Inherited F0/B1 numerical bounds, retention/movement costs,
exact control/clear implementations, and conversion to a whole-controller
precision budget remain open.
