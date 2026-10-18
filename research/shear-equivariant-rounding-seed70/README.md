# A bounded rounder cannot carry an infinite-order shear exactly

**Adversarial mathematical audit and scoped negative result; no new kappa.**
There is no fixed globally bounded grid rounder, even an arbitrary coupled
nonlinear one, that is exactly equivariant under
`Q = [[1,1],[0,1]]` on all half-grid outputs. On the particular orbit below,
the sharp error allowance through 70 frames is **18 grid units**. Ordinary
toward-zero and nearest-even rounding give small reversible dirty echoes
whose carried and eager outputs differ while scratch restores exactly.

This supplies a boundary for a possible rounded implementation of Sagar
Thakrar's [PR1537](https://github.com/CrocSwap/integer-mult-bounds/pull/1537).
That predecessor explicitly uses exact rational arithmetic and integer
readers; it does not assert the false rounded implication. Its binary-return
halvings undo their own doublings exactly. **No defect in that construction
or the selected PR1094 supplier is alleged.**

## Audited implication and dependencies

PR1537's child contract is `C(D,W)=(D+R W,P W)`, where
`P=diag(Q,...,Q)` and `RP=QR`. Carrying phases uses
`Q^(-i) R P^i=R`. The proposed extension being tested is:

> An exact equivariant reader can be replaced by a reader rounded to one
> fixed grid, with a fixed absolute rounding allowance, while retaining
> that same exact equivariance for arbitrary source values.

The test reader is the rational subcase `m=1, R=I/2`, so `RQ=QR` holds
exactly. For source inputs in `delta Z^2`, its outputs cover
`(delta/2) Z^2`. This reader changes the predecessor emitter's integer-reader
premise; it is not one of its 81 ternary fixtures. The question is a bridge
for the broader rational contract, not an audit of those integer fixtures.

The only external proof source consumed here is the unchanged PR1537 README
at head `407f00df6ca0bf86b455b5640f18ec2f62ee77b9`, Git blob
`b9800377dae28f3dd85c15def0db34fa36a11ff2`, SHA256
`4f405ae489ef03616a6b26b0180a1005db9cdca88923f68ebbddc1c3f387953f`.
It is retained in [references/](references/pr1537-README.md) with its credit.
No predecessor executable is imported. [SOURCES.json](SOURCES.json) also
pins the base, selected record and originating task catalogue as historical
provenance. Those historical pins do not claim a current cold replay.

## Written proof: the infinite orbit

Fix any `delta>0`. Let
`q : (delta/2) Z^2 -> delta Z^2` be any function. Suppose there is a finite
constant `C` with `||q(v)-v||_infinity <= C` for every v, and suppose
`q(Qv)=Qq(v)` for every v. No linearity, continuity, coordinatewise rule,
nearest-point property or identity-on-grid property is assumed.

Take `v_0=(0,delta/2)` and write `q(v_0)=delta(a,b)` with integer a,b.
Equivariance gives, for every nonnegative integer k,

    v_k = Q^k v_0 = delta(k/2,1/2),
    q(v_k)-v_k = delta(a+k(b-1/2), b-1/2).

Since integer b cannot equal 1/2, the first-coordinate error is unbounded
as k grows. This contradicts C. One-step equivariance on the entire domain
already implies the iterated equality, because that domain is Q-invariant.
The contradiction therefore covers every finite error allowance, not only
nearest rounding. It applies separately at every positive grid spacing.

Equivalently, an equivariant error moves as `e(Q^k v)=Q^k e(v)`. Bounded
shear orbits require `e(v)` to lie in `ker(Q-I)`, meaning zero error in the
second coordinate. The half-grid supplies a point where that is impossible.

## Written proof: sharp finite-orbit allowance

For a fixed nonnegative K, prescribe only the values on
`v_0,...,v_K`, requiring `q(v_k)=Q^k q(v_0)`. This finite restriction is
weaker than a globally equivariant rounder. Its exact minimum maximum error
is

    C_K = delta * max(1/2, K/4 + dist(K/4,Z)).

Indeed, for a seed output `delta(a,b)` the radius in grid units is

    max(|a|, |a+K(b-1/2)|, |b-1/2|).

The first-coordinate error is affine, so its maximum is at an endpoint.
For b outside {0,1}, its endpoint maximum is at least `3K/4` and its
second-coordinate error is at least `3/2`. Such a b cannot beat the
b=0 construction: for K>=2 that construction is at most `K/4+1/2`,
and K=0,1 have radius 1/2 directly. For b=0 the first-coordinate maximum
is `K/4+|a-K/4|`; choose an integer nearest K/4. The b=1 case is symmetric.
Including the second-coordinate error proves the formula and attainment.

In particular `C_0=C_1=delta/2`, `C_2=delta`, `C_70=18 delta`, and
`C_160=40 delta`. These are optima for this single prescribed finite orbit,
not precision optima or a globally compatible rounding construction. The
written proof supplies all K; the replay corroborates K=0..160.

If exact equivariance is relaxed, a bounded rounder still has the following
necessary defect on this orbit:

    ||q(Q^K v_0)-Q^K q(v_0)||_infinity >= max(0, K delta/2 - 2C).

To prove it, expand the first coordinate as
`e_1(v_K)-e_1(v_0)-K e_2(v_0)`. Each endpoint error is at most C, whereas
`|e_2(v_0)|>=delta/2`. This is a lower bound on a commutation defect, not a
complete numerical-error or recursive-cost recurrence.

## Literal rounded echo witnesses

Let `f(w)=q(w/2)` componentwise, using toward-zero or nearest-even q, and
let each child perform `D+=f(W); W=QW`. It is reversible: its inverse first
undoes Q, then subtracts the same deterministic f. The target is never read
by f. A restored two-child eager group implements

    F_e(W)=2f(W).

The carried group, including both terminal frame returns, implements

    F_c(W)=f(W)+Q^(-1)f(QW).

Both groups restore W. Their complete dirty echo is exactly
`U+=X; group(D,U); U-=X; inverse_group(D,U)`. Thus the increment is
`F(U+X)-F(U)` and U restores even when f is nonlinear. Every source load,
unload, frame return and reversed inverse appears in the replay. No macro
count is presented as a primitive arithmetic or physical cost saving.

For delta=1, D=(2,-1), U=(1,1), X=(0,1), toward-zero rounding gives eager
output `(2,1)` and carried output `(1,1)`. Both return U=(1,1).
Nearest-even has a separate witness: U=(0,1), X=(1,0), with the same D,
gives eager `(2,-1)` and carried `(3,-1)`. Both return U=(0,1).
All inputs and all rounded states lie on the integer grid. The unchanged
exact reader `f(w)=w/2` gives `D+=X` under either complete echo. In particular,
the differences are rounding-interface failures, not omitted restoration.

## Evidence, domain and stopping rule

[EXPECTED.json](EXPECTED.json) records every horizon, all minimizing integer
seed outputs, the completed census size, literal words, scaled witnesses,
coverage counts and ten semantic controls. The primary rational interpreter
checks chronological attaining orbits. A separate integer implementation
enumerates every seed output within a concrete incumbent radius; any omitted
output fails an entrance-coordinate constraint and cannot improve it.
Both were written in this same AI-assisted session.

The complete finite domains are:

- All horizons K=0..160; the integer-output bounds and counts are recorded
  separately at each K. This is a finite exact optimization, not a random search.
- Signed powers -80..80 at all grid spacings `2^-p`, p=0..12.
- The defect inequality for both ordinary rounders, p=0..12, K=0..20,
  first half-grid numerator -3..3 and second numerator in {-3,-1,1,3}.
- Complete echoes at p in {0,1,7,12}, both rounders, all 625 source/dirt
  pairs with each grid coordinate -2..2 and fixed D=(2delta,-delta).
  Target translation invariance follows from the displayed word; the finite
  replay does not enumerate all possible target dirt.
- Exact-reader echo controls, literal rounded inverses, the compatible
  restricted domain below, and a finite-order sign-frame control.

OS seed70 selected this track and the displayed horizon70. Three candidate
tasks, the local claim and stopping rule are recorded in
[CLAIM.md](CLAIM.md) and [TASK.json](TASK.json). No pinned sprint issue existed.
[OVERLAP.json](OVERLAP.json) records live search coverage and the nearby heads.
The experiment stops after the proof, this domain and package checks; it does
not extend a closed decoder search or search for a supplier or new kappa.

## Limits and viable escapes

The theorem requires one fixed output grid, a fixed function, exact Q
equivariance, a Q-invariant domain containing the half-grid orbit, and a global
absolute error bound independent of source magnitude and orbit length.
It does not exclude stateful/frame-dependent schemes, magnitude-relative
error contracts, a bounded reachable domain, extra precision or an explicit
approximation/restoration budget. It does not prove such alternatives work.

The full-grid integer readers of PR1537 already have zero rounding error.
More generally on `R x delta Z`,
`q(v)=(delta floor(v_1/delta),v_2)` has error below delta and commutes with Q:
the exact second coordinate makes the first shift an integer number of grid
units. This positive control identifies the missing hypothesis. An odd
toward-zero rounder also commutes with the finite-order frame -I. Infinite
order alone is not a universal obstruction; the shear's nontrivial error
growth and off-grid transverse coordinate are what the proof uses.

No supplier word, physical hosting, scalar preparation, all-size compiler,
precision/tape recurrence, analytic transfer, selected cold replay, Lean proof
or independent human mathematical review is supplied. The selected conditional
kappa remains `836330098538459/500000000000000000`. This proof does not refute
the exact arithmetic construction or claim an unconditional multiplication
theorem.

## Reproduce

From the repository root, Python 3.12 and its standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/shear-equivariant-rounding-seed70
```

Expected markers:

    PASS_SHEAR_EQUIVARIANT_ROUNDING K70=18_grid_units horizons=161 ... no_new_kappa
    PASS_SHEAR_ROUNDING_PACKAGE_TESTS
    PASS_REGISTERED_RESEARCH_PACKAGE research/shear-equivariant-rounding-seed70 outcome=negative-result

The registered command checks historical Git provenance, the mathematical
receipt and focused rejection/relocation tests. Standalone relocated replay
`python3 -I -O -B verify.py` checks the mathematics and retained external
reference; historical repository provenance is additionally checked by the
registered command. Default replay writes no package files; `--emit` prints
a deterministic certificate without changing files. Executed environments,
checks and omissions are recorded in [VALIDATION.md](VALIDATION.md).

## Open next questions

1. Can a concrete child guarantee an exact transverse-coordinate grid
   invariant? That would evade this obstruction and make its carried frame
   plausible. First identify an actual indivisible reader and check its output
   lattice at every invocation, including dirty sources. No such physical
   child is supplied here; integer toy readers alone do not establish one.
2. Can a finite carried interval use a frame-dependent or finer-grid rounded
   child with a complete accumulated-error and restoration recurrence?
   First specify one child, every working grid and a fixed reset horizon,
   then compare both complete words at a common accuracy. Missing local
   error, overflow and physical arithmetic prices block an admission claim.

## Credit and disclosure

Prepared by **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex
assistance** in derivation, implementation, checking and writing. One parent
agent; no subagents or independent human review. New work is Apache-2.0.

Credit Sagar Thakrar's PR1537 for the paid infinite-order frame and explicit
precision boundary, Ross Richardson's PR1287 for cyclic output-frame dirty
echoes, and the retained PR1227/889/1203 interface lineage. @jmbarrancoidener's PR1466 (`8230e01b60d321ca10f2789e27cde037c40e6d6c`) classifies
componentwise toward-zero transport on disk inputs; this result changes to
arbitrary coupled rounding on an unbounded half-grid shear orbit. Ali Romman's
PR1135 addresses a different additivity/restoration bridge. PR1552/1563/1575
study exact reset schedules, costs and prefix bounds, rather than this rounding
obstruction. PR1490/1566 round helper-gauge exponents in a cost argument, not
data quantization; they are distinct. Nearby work is not claimed as an
independent review of this proof. Rohan Arun, Jeremy Kothe and the retained
PR589/555 contributors retain selected-construction credit.
