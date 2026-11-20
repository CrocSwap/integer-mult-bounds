# A parity-mixing requirement for smaller forward Gaussian rounding slack

**Any total injective error-one rounder for the four-coordinate Hadamard
map that beats one half in forward radial slack must change infinitely
many inputs whose ideal images are already integral.** The required
changes satisfy an explicit linear count. For forward slack at most
3/10, at least \(8m\) even-sum inputs of norm at most \(4m+2\) must change,
for every integer \(m\geq0\).

This is a universal necessary condition for the unrestricted all-lattice
problem. It rules out repairing only finitely many exact-valued inputs.
It does not settle the unrestricted optimum, construct a new rounder,
or supply a fixed-tape cost lower bound.

## Exact result

Let \(U=H_4/2\). A total injection \(F:\mathbb Z^4\to\mathbb Z^4\)
must satisfy, at every input,
\[
\|F(x)-Ux\|_2\leq1,\qquad
\|F(x)\|_2-\|x\|_2\leq\delta<1/2.
\]
With \(E=\operatorname{diag}(1,1,1,-1)U\), let \(K_N\) count even-sum
inputs changed from their exact ideal images whose transformed outputs
\(E^TF(x)\) lie in \([-N/2,N/2]^4\). The theorem is
\[
K_{N+2}-K_{N-2}\geq8
\quad\hbox{if }N\geq3\hbox{ is odd and }
\delta<N-\sqrt{N^2-N+1}.
\]

The [proof](PROOF.md) has two ingredients. Opposite colors of a half-grid
cube contain equally many points, but eight output corners have no
allowed internal predecessors below the stated threshold. Every input
that escapes this obstruction by changing parity forces a nearby
exact-valued even input to change, because its old output has been taken.
The resulting annular inequality telescopes.

No surjectivity, inverse provider, exact Gaussian sum, phase covariance,
finite iterate identity or periodicity is imposed. Leaving all integral
ideal images unchanged is equivalent to preserving total parity in the
error-one class. The lower bound therefore establishes forward supremum
at least one half for that subclass. The explicit parity-preserving
bijection in [#7569](https://github.com/CrocSwap/integer-mult-bounds/pull/7569)
supplies the matching upper bound; its upper theorem is credited prior work.

The signed-permutation equivalence with Ali Romman's ideal Gaussian pair
transfers error, injectivity, parity and radial slack exactly. The cube
coordinates and their relation to the original Gaussian coordinates are
given in the proof.

## Why this question remains distinct

[#7571](https://github.com/CrocSwap/integer-mult-bounds/pull/7571) gives
the finite lower threshold \(\sqrt{78}-\sqrt{73}\), and Nick Petalas's
[#7651](https://github.com/CrocSwap/integer-mult-bounds/pull/7651) attains
it through radius 24. The present theorem does not extend that finite
calculation. It identifies a mechanism that any global extension at the
same threshold must possess: changes to exact-valued inputs at unbounded
radii, with the stated quantitative count.

Ali Romman's [#7696](https://github.com/CrocSwap/integer-mult-bounds/pull/7696)
solves the different exact-sum optimum. The subsequent
[#7714](https://github.com/CrocSwap/integer-mult-bounds/pull/7714) and
[#7743](https://github.com/CrocSwap/integer-mult-bounds/pull/7743) impose
iterate and least-period conditions. Those requirements are absent here.
Targeted live searches found no matching claim; their coverage does not
constitute a novelty guarantee.

## Verification

From the repository root, using Python 3.12 and the standard library:

    python3 -I -B -W error research/gaussian-forward-parity-flux/verify.py
    python3 -I -O -B -W error research/gaussian-forward-parity-flux/verify.py
    python3 -B scripts/research_package.py --package research/gaussian-forward-parity-flux

The direct checks print JSON with status
PASS_GAUSSIAN_FORWARD_PARITY_FLUX. The registered hook additionally
checks the pinned catalogue and selected-record provenance. Runtime
verification has no predecessor imports or external input files.

The retained [receipt](RESULT.json) records:

- Complete original-coordinate error-one neighborhoods on 2,401 inputs.
- Cubes with \(N=3,5,7,9\), each with an exact eight-output deficit at
  slack 3/10; every possible escaping unit edge is rejected at slack 1/2.
- All 32 corner edges at equality for each cube. These show why the
  theorem requires a strict comparison with \(c_N\).
- 49,664 two-edge choices, including a concrete counterexample to
  charging the second edge to the original cube without widening it.
- A separately checked 3,121-input radius-five injection at slack 3/10.
  Requiring all even inputs to stay exact reduces the maximum matching
  to 3,113. An explicit 321-input/313-neighbor Hall witness proves the
  upper bound independently of the matching search. This is a control
  against falsely claiming an unrestricted finite lower bound of one half.
- 9,600 rational onset comparisons, large integer onset checks through
  2,048 bits, and rejecting collision/nonlocal-edge mutations.

The finite matching search and its direct error/injectivity checker are
separate routines. The proof author also wrote the primary verifier;
these finite checks are corroboration, not an independent universal proof.
Root review is recorded separately when completed. No independent human
or formal-kernel acceptance is claimed.

## Scope, costs and kappa

This changes no selected source, caller, certificate or implementation.
The result is a generic precision-interface obstruction linked to
precision_tape and analytic_recovery, with no selected caller binding.
The catalogue card originally asks for assumption discharge at an actual
caller; this narrower side problem is explicitly recorded as changed
scope in TASK.json.

The changed-input count is not a tape-time bill or an asymptotic
positive-density lower bound. There is no new multiplier exponent:
the selected conditional value remains
\(\kappa=363005817/100000000000=0.00363005817\), with all five
foundational assumptions retained. Exact sources and their roles are
recorded in SOURCES.json.

## Open next questions

Can an all-lattice matching attain the finite unrestricted threshold
while performing the forced parity exchanges? The next useful step is
a radius-independent construction or Hall argument that covers all
cuts, not another larger finite ball. The current inequality is only
necessary.

Before treating a new rounder as assumption progress, identify an actual
selected caller that tolerates changes at integral ideal images and
specify its inverse, algebraic identities, range, ownership and complete
cost. None is supplied here. TASK.json records both questions and their
blockers.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The new contribution is the cube-corner counting argument, the nearby
injective charge and the resulting linear parity-mixing requirement.
#7569 supplied the half-grid coordinates and upper construction; #7571
and Nick Petalas's #7651 supplied the unrestricted finite Hall question.
Ali Romman's #6509 supplied the ideal Gaussian pair; Nick Petalas's #6619
and ywz65's #2589 supplied the earlier radial-obstruction context.
The exact-sum and period results keep their distinct predecessor credit.
Apache-2.0; no predecessor executable is copied or modified.
