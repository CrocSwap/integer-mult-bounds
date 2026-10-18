# A collision at the rounded QQ16 child return

## Exact interface and statement

Consider only PR3250's local finite program, at its pinned commit
`02ff0bb88a2e808bb07c75722f3595861ce2b20d`. Its mathematical operations
are B1_2 event11795, the rank-one native child on L470 from frame0 to
frame5, followed by event11796, `L524 -= L470/2`. Both fields are in the
borrowed-helper index range. The program overwrites its source x with the
rounded child return xhat, overwrites its distinct destination d with dhat,
and returns its two owned buffers to zero. This is the program whose
unchanged implementation is retained as `reference.py`.

The endpoint interface comprises only xhat and dhat. The second interface
also exposes the entire integer count dictionary returned by `run`.
It excludes an entry copy, the primitive operands, discarded low bits,
a per-site rounding transcript and other input-dependent retained state.
Any such additional information belongs to the side state in the bound below.

For every integer 2 <= p <= 2046 and positive dyadic q, there are 3^256 distinct
legal local entry sources, with destination zero, producing the same
endpoint under p-bit nearest-even arithmetic. Consequently an extension
which recovers every entry from that endpoint must retain at least 406
bits of additional state capacity. A subfamily of 2^256 entries has the
same entire count dictionary as well, requiring at least 256 bits even
when that dictionary is available.

These are local-entry statements. No assertion that the whole B1 prefix
reaches these inputs while keeping all other fields constant is needed or
made. In particular, this is not a collision of the complete producer state.

## The scalar tie

Put A=2^(p+1). In the p-bit normalized binary system, the adjacent
representable numbers below and above A are A-2 and A+4. The number A-1
is the midpoint below A and rounds to A because A is the even endpoint.
The number A+1 is strictly below the midpoint A+2 above A. Therefore,
for c in {-1,0,1},

```text
RN_p(A+c) = RN_p(A-c) = A.                       (1)
```

Scaling every value by the dyadic q preserves nearest-even decisions.
There is no overflow or underflow in the inherited finite fixed lattice.

## The actual native recipe

Write the literal rank-one native child as U=L C R. Both R and L are the
source's signed complex monomial permutations, including global phases.
They are exact bijections on these component formats. In right-monomial
coordinates, independently at each of the 256 disjoint complex pairs,
choose the entry

```text
(a+ib, c'+id) = (q A, q c_j),  c_j in {-1,0,1}.
```

The original source is the inverse right monomial applied to this vector.
Its nonzero real/imaginary components are signed qA or q, all exactly
p-bit representable. Every component lies in q Z and is strictly below
M=2^(p+2)q. Thus PR3250's exact entry lattice, range and significand
conditions hold, with b-ell=p+2 and width W=p+8. Its working quantum is
q/4; both divisions by two in the child/half-ADD remain exact.

The source's pair-first implementation first computes

```text
sr=RN(a+c'), si=RN(b+d), dr=RN(a-c'), di=RN(b-d).
```

Equation (1) makes these `(qA,0,qA,0)` for every choice of c_j. The second
mixing layer, division by two and left monomial are exact on this family.
Before L, every pair returns

```text
(qA/2 + i qA/2, qA/2 - i qA/2).                  (2)
```

The destination starts at zero, so the following half-ADD returns
`dhat=-xhat/2` exactly. Both endpoints and the zero scratch state are
therefore independent of all 256 ternary choices. Right-monomial
invertibility makes the 3^256 entries distinct. The exact unrounded map
separates them; it is the specified rounding which erases the differences.

For a nonzero c_j, exactly two first-layer component operations round.
Their signs change with c_j, but their number does not. No second-layer or
half-ADD operation rounds. Thus restricting every c_j to {-1,1} fixes
every key of the actual program's count dictionary, including both
nonzero-round counters. It still leaves 2^256 distinct entries.

## Information bound and compatibility with accuracy

If K distinct entry states give one endpoint, any exact recovery procedure
must distinguish all K using its remaining side state. A side register
with B bits has at most 2^B states, so 2^B >= K. This applies to arbitrary
deterministic recovery and to an injective reversible extension, regardless
of how that side state is encoded. Here

```text
2^405 < 3^256 <= 2^406, so B >= 406;
K=2^256 with the complete count summary fixed, so B >= 256.
```

The bound counts state capacity, not a charged recursive call, tape step,
time-space product or number of required private registers. A retained
input, correlated outside field, source-assisted repair or reversible
history can supply the information. A finer or exact-grid implementation
can avoid this collision. No universal reversible-implementation barrier
follows.

On the sign family, native error norm is exactly 16q, while entry source
norm is `16q sqrt(A^2+1)`. The relative error is
`1/sqrt(A^2+1) < 2^(-p-1)`. The half-ADD's error relative to the actual
child return is zero. Thus the collision is compatible with PR3250's
proved relative-error contract, including its sufficient choice
`p>=beta+delta+104` for PR3235's local allowance. Increasing p moves A;
the theorem does not assert that one fixed input collides at every p.

For example q=2^(-p-6) bounds every sign-family source norm by one, with
all components still dyadic. A norm bound alone therefore does not remove
the collision; a fixed independently supplied entry grid can change the
available dynamic range and is a different premise.

## Relation to prior work

PR2999 by Ross Richardson already proves the analogous information-loss
principle for an adaptive P104 collector, including a diagnostic-total
refinement. This result binds it to PR3250's different literal QQ16 kernel,
uses the actual rounded child plus scalar return, and obtains the ternary
endpoint family and fixed-full-count sign family. The general principle
and its P104 application are predecessor work. PR3250 explicitly left
global dirty restoration open; no error in its local accuracy claim is
alleged. There is no new supplier or kappa result.
