# Evidence scope and check ownership

## Defined finite domains

There is no random search. No random seed is used. Each declared loop runs
to completion; the stopping rule is the end of its finite domain.

- Scalar ratios: every reduced p/q with `2<=q<=24` and `-2q<=p<=2q`.
  For each of the 716 ratios, translations run from -2q through 2q.
  The safe-lattice check uses all q residue representatives. The residue
  adapter check uses all old values and translations from -2q through 2q.
  It checks 47,340 translation classes and 3,495,180 exact responses.
  Offset averaging uses every z from -q through q, for 24,028 identities.
- Matrix quotients: the six matrices and moduli are explicit in
  `verify.py` and `EXPECTED.json`. Each check covers all vectors in its
  full residue cube. Singular matrices and composite moduli are included.
  The response partition is built separately from the residue image.
- Joint summaries: the denominator pairs (2,3), (3,9), and (3,7).
  Every old value and translation in one least-common-multiple period
  is checked. The expected state count is that period.
- Borrowed boundaries: all normalized functions on `Z/qZ`, for q=2,3,4,5.
  This gives 700 functions and 82,480 input triples. The checker executes
  the actual ten-record child subword emitted by pinned PR1057. It checks
  helper restoration separately from additivity. Exactly q functions
  pass at each group order. These finite groups check the algebraic
  equivalence; they are not used as a real-valued rounding model.
- Physical accuracy: W=0 through 8, every point in the physical grid
  `[-1,1]`, and integer slopes -2 through 4. Slopes outside this interval
  are farther from 4/3 and cannot improve the bound. The code separately
  checks the ordinary rounded map, whose error decreases with W.
- Pinned PR985: 336 signed diagonal executions for B=2 through 8,
  `b=2^-B`, eight signed source choices, and three arbitrary targets.
  Another 44 signed executions cover the complete four-factor borrowed
  word and its literal inverse. The four exact half-grid tie cases are
  checked directly against the pinned data rounder.
- Finite exact lifts: distinct optimized and balanced binary trees for factor
  counts 2,3,4,5,8,16, each at lengths 1 and 3. The 22 cases compare
  every prefix with a Fraction oracle, check the closed-form product,
  execute the integer forward/inverse pair, and check source and helper
  restoration. Each receipt gives the prefix degree, denominator, width,
  and full local arithmetic/access counts. No physical tape compiler is
  claimed for this comparison construction.

The scalar classification has a second method: the proof uses the bounded
rounding error and a subgroup argument, while the finite checker builds
all differences on complete residue periods. Matrix tests compare a
direct response partition with an independently formed residue image.
The integer lift uses a free symbolic degree bound and a separate exact
rational interpreter. All methods are AI-authored; this is not independent
human review.

## Test authoring gate

The checks protect externally stated mathematical contracts, not code
shape. The main credible faults are a wrong data tie rule, an ignored
residue, an incomplete safe lattice, a change from boundary restoration
to whole-word inversion, a physical/grid-unit mix-up, an uncharged
denominator extension, and an omitted inverse execution.

PR1057 already checks exact additive words and one arbitrary nonlinear
witness. It does not classify the rounded safe lattice or test the stated
finite rational and function domains. PR985/1054 check their retained
excluded-ancestor interface; they do not assert this borrowing contract.
The new checker owns those distinct statements. It uses no production
test seam, hidden flag, or altered predecessor implementation.

Nine mathematical controls distinguish nearest-even and truncation from
the specified data rounder, reject an ignored residue and false additivity,
detect the scaled averaging output and missing exact precision, and verify
two actual escapes: reaccess with zero saved state and different grids.
The latter two controls keep the obstruction's scope honest.

Three subprocess controls verify the real command boundary. A changed
pinned source must fail its digest check. A changed residue implementation
must fail the response equation, not an import or syntax error. An occupied
receipt path must be rejected without changing its bytes. A relocated,
read-only optimized-Python replay must return the complete expected receipt.

## Attempts and stopping decision

Three candidate approaches were considered before implementation.

1. Compute a child on a zero target, copy its increment, then uncompute it.
   This can remove target dependence if its clean array or recomputation
   is paid. It does not make the rounded source increment additive. The
   physical-range theorem rules out that stronger generic wrapper contract.
2. Keep exact rational residuals. A finite integer construction was executed.
   It works on an embedded coarse lattice and has an explicit denominator
   and width bill. The endpoint alone needs n log2(q) bits of fractional
   resolution in this representation for n repeated coprime p/q factors.
   It is not a free bounded-width
   replacement for PR1054's rounded child, and no supplier bill was built.
3. Characterize the restoration equation and its precise resource escapes.
   This is the selected result. The proof and complete finite domains are
   finished. No search was stopped merely because a first example failed.

Reaccess was checked as a concrete alternative. If the changed helper and
its displacement are readable, no saved residue is necessary. At the
borrowed boundary, an inverse C call recovers the old target. This also
undoes the output contribution. A complete changed schedule must retain,
recompute, or otherwise account for that contribution and prove its next
parent interface. No lower bound on all such schedules is claimed.

The result does not establish a new rounded recursive construction,
physical hosting rule, fixed-tape implementation, supplier moment, or
integer-multiplication exponent. Full repository regeneration, the selected
cold replay, and remote CI are outside this isolated package's validation.
