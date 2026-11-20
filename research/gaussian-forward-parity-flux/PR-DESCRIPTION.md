## Result

Any total injective error-one Hadamard/Gaussian rounder with forward
radial slack below one half must change infinitely many inputs whose
ideal images are already integral. The proof gives a quantitative bound:
at slack at most 3/10, at least \(8m\) even-sum inputs of norm at most
\(4m+2\) must change, for every \(m\geq0\).

In exact half-grid coordinates, an odd-width cube has equal input/output
color counts but eight inaccessible output corners. Each parity-changing
exit forces a nearby exact-valued input to change. If \(K_N\) counts
these changes by transformed output cube, the result is

\[
K_{N+2}-K_{N-2}\geq8
\quad\text{when}\quad
\delta<N-\sqrt{N^2-N+1}.
\]

The parity-preserving subclass consequently has forward optimum one half,
using #7569's credited upper construction. Surjectivity, exact sums,
phase covariance and period identities are not premises of the new
lower theorem.

## Why this helps

#7651 already attains the unrestricted finite threshold through radius
24. This contribution identifies what any all-lattice extension must
change: a finite repair of exact-valued inputs cannot suffice. It does
not claim the unrestricted optimum or repeat larger finite-radius work.
#7696 and #7714/#7743 concern additional exact-sum and iterate contracts.

## Checks and limitations

Run:

    python3 -B scripts/research_package.py --package research/gaussian-forward-parity-flux

The exact checks cover 2,401 coordinate inputs, four complete cube graphs,
49,664 two-edge choices, equality/escape controls, 9,600 rational cutoffs,
and a separately verified 3,121-input unrestricted finite matching.
Holding its even inputs exact gives only 3,113 matches, with an explicit
321-input/313-neighbor Hall witness certifying the upper bound separately
from the search. Collision and nonlocal-edge mutations reject. The
universal statement rests on the written proof, not finite exhaustion.

No selected caller, physical tariff, positive-density claim or
unrestricted all-lattice construction is supplied. All five foundational
assumptions remain; there is no new kappa.

## Sources and credit

Base: e54523517d0f03e58352e647c403a5af3e525a57. Exact predecessor heads,
scope, proof, receipt and remaining questions are in the package.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit #7569 for the half-grid coordinates and upper construction,
#7571 and Nick Petalas's #7651 for the finite Hall problem, Ali Romman's
#6509 for the Gaussian pair, and #6619/#2589 for the radial-obstruction
lineage. Model-assisted review is not human or formal-kernel acceptance.
