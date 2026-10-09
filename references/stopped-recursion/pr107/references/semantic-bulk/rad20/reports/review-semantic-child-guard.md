# Independent review of the linear semantic child guard

The proposed linear guard in
[downstream-semantic-child-guard.md](downstream-semantic-child-guard.md)
is valid for the retained exact recursive layer. The conclusion is
`C1=1`, with the conservative fixed constant `C0=32*m*(s+E)^2`.
This is a changed estimate for the same program. It uses no smaller child
word, inner rounding, value compression, new arithmetic primitive or new
finite phase circuit. Review date: 2026-10-08. Original conditional input:
CrocSwap/integer-mult-bounds
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; the compact-control revision
`6e564879f51ae16f23d392e9e196c605f36d90df` preserves the relevant interfaces.

## The exact boundary that permits the estimate

Original `05-layers.tex`, equations `phase-C`, `phase-inverse-child` and
the paragraph headed `The exact recursive contract`, give

```
C = ((1+i)I+(1-i)X)/2,
(C^-1)^tensor f = (-i)^f Z^tensor f C^tensor f Z^tensor f.
```

Every completed forward child is exactly `C^tensor f` on every original
row and role. Endpoint phases, corrected source/sink signs and physical
bank exchange restore the proper roles. The contract explicitly permits
arbitrary scratch values. The completed inverse has the displayed unit
phase wrapper. Its coefficients are in `2^-f Z[i]`, and either completed
operator has maximum absolute row sum `(sqrt(2))^f <= 2^f`.
These are algebraic all-input statements, not unit-disk approximations.

Consequently an incoming grid `2^-(p+b) Z[i]` and magnitude bound `2^b`
give completed grid `2^-(p+b+f) Z[i]` and magnitude bound `2^(b+f)`.
The individual kernel formula, including every half, is exact in the
single guarded word format. The original layer truncates only once,
after completing `b^D S_D C^tensor D S_D`. Inverse wrappers, source/sink
phases and `b^D` are Gaussian dyadic scalar operations; the unit wrappers
do not enlarge the completed norm or denominator bounds.

At a call boundary the parent sees only the returned role streams and
its parked operands. The retained fixed-tape procedure explicitly pushes
inactive role streams, copies the active child stream to its input area,
and returns its result before popping them. It does not expose an internal
child intermediate as a later parent operand. Address permutations and
exceptional corrections return complete encodings before coefficient
arithmetic resumes. Dead work-tape strings need no semantic interpretation
as returned coefficients. These details matter: knowing only a selected
output of a partially completed call would not justify the estimate.

## Internal and whole-layer bounds

Let `A(e)` be the additional common exponent sufficient for every
intermediate magnitude and dyadic denominator of an exact e-axis call,
relative to arbitrary incoming bounds. At a leaf `A(e)<=8e`. At an
internal node each of s calls acts on `f=e/m` selected axes, while all
nonchild arithmetic is charged by the independently retained fixed E.

Before an active child, all previously completed calls together increase
the semantic exponent by at most `s*f`. Any retained earlier parent input
has no larger bound. Scalar gates have accumulated at most E additional
units. The active child may then require its internal `A(f)`, which gives

```
A(e) <= A(e/m)+s*e/m+E.
```

After that child returns, its internal excess can be replaced in the
*bound* by f, because its returned values satisfy the exact completed
interface. No operation discards those fine-grid bits. Cancellation has
already made them zero in the same integer encoding. This controls
additions and subtraction with saved parent operands as well as sequential
calls in different slots. The grouped scalar schedule is evaluated from
saved inputs and has coefficients `0,+/-1,+/-1/2`; its accepted
`E=64*(W+m+1)^3` charge includes inverse and endpoint corrections. It is a
fixed constant for the selected finite motif, independent of p and d.

For j actual internal levels, including any retained stopping rule,

```
A(e) <= 8e/m^j+s*e*sum_(v=1)^j m^-v+E*j
     <= [8+s/(m-1)+E]*e <= 2*(s+E)*e.
```

Here `m>=3`, `j<=log_m(e)<=e` and `B=s+E>=8` suffice. No inequality
involving `s*A(f)` is needed; that would concatenate temporary excess
after it has vanished at the exact call boundary. This bound remains
valid when an entire root is a leaf.

The retained base-m decomposition partitions the remaining selected axes
into disjoint pieces whose sizes sum to at most d. Even concatenating
their new linear bounds costs at most `2B*d`. Row preprocessing applies
individual C kernels on different selected axes; its charge, the two
outer phases, and the exact final denominator shift are covered by the
original additional `18d`. Zero rows return to zero at a completed call
and can be removed then. Arbitrary intermediate scratch is still allowed.
Therefore

```
A_layer <= (2B+18)d < 32*m*B^2*d,
Delta = ceil(32*m*B^2*d).
```

The unchanged representation has `p+Delta` fractional bits and `Delta+3`
integer/sign bits per real component. With any fixed `epsilon<1`,
`d=floor(b_input^epsilon)` and retained `p=6*b_input`, Delta is eventually
at most p. The proposed compact cutoff using
`ceil(bit_length(2*C0)/(1-epsilon))` is conservative: it implies
`b_input^(1-epsilon)>=2*C0`, hence `C0*d<=b_input/2`; the ceiling and
initial retained cutoff leave ample room under `p=6*b_input`.
Neither the record width nor its exact linear scan cost changes.

## Independent fixed-integer controls

[review_semantic_guard.py](../code/review_semantic_guard.py) imports no
producer and uses no Fraction simplification. Every value is an integer
Gaussian numerator on a preallocated common fine grid. Every halving
asserts that both numerator components are even; the fractional width
never changes during a run. The executed toy recursion has six child
calls per internal node, including two forward/inverse cancellation
pairs, and a genuine temporary three-bit halving excursion. Its completed
map is independently checked against the closed tensor coefficient
formula. This exercises the semantic boundary; it is not a replay of
the enormous actual finite phase network.

The fresh [run](../runs/20261008T025235Z-review-semantic-guard/) passed
44 forward/inverse basis probes, 24 arbitrary-grid probes, 2,220 exact
output values, 1,130,200 exact fine-grid halvings, 8,206,160 observed
integer components, and 594 exact stopped recurrence controls. Selected
observations on incoming grid exponent 13 were:

| Selected axes | Stored fractional bits | Maximum observed grid | Completed grid | Proven completed upper |
|---:|---:|---:|---:|---:|
| 2 | 120 | 17 | 14 | 15 |
| 4 | 224 | 17 | 14 | 17 |
| 8 | 432 | 19 | 16 | 21 |

The observed maximum includes the subsequent exact inverse restoration.
Thus actual intermediate fine-grid growth survives in the fixed encoding,
while returned values belong to the coarser semantic grid. A negative
control truncating each child immediately to its incoming p grid destroys
the nonzero C image of a `2^-p` impulse; both true `2^-(p+1)` components
would be rounded to zero. The exact-child requirement is indispensable.

Seed 503, Python 3.14.4, one worker, 3.61 seconds elapsed and 23,292 KiB
maximum RSS. Reviewer source SHA256:
`3150c40bb2791b18bbaa44e6dd5e8c33fa9072681b94edd5257afb7d8d1b9a4a`.
The protocol retains original section hashes, producer source/report
hashes, exact command, timed log and the finally-block release of the
owned finite-pool reservation.

## Scope and next interface

This positive conditional review supports the linear guard for the
accepted exact complex layer and its shared auxiliary banks. It does not
make the multiplication theorem unconditional, improve the underlying
primitive, or remove a resampling movement cost. An improved exponent
still requires the separate bulk locality and tape transfer plus new
strict parameter and normalization checks. In particular `epsilon+r<1`,
the Gaussian accuracy margins, compact reservations and K geometry remain
requirements. No literature priority or novelty is claimed.

Reproduce with `python3 -B code/review_semantic_guard.py --reference
<original-pinned-checkout> --output <fresh-path>` from the topic directory.
Only Python's standard library is required. Completed source and evidence
remain unchanged; the original inputs were read only.
