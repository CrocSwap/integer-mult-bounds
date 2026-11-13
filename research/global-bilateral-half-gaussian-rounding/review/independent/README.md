# Independent review of the odd-parity global map

This directory records an independent exact challenge of the proposed
global \(H_4/2\) parity-preserving rounder with bilateral radial slack at
most \(1/2\). The complete derivation is in PROOF-CHALLENGE.md. The exact
checker uses integer matrices and doubled half-integer coordinates; it
imports no finite-sweep generator.

The review found no counterexample. The factorization
\(F=E M R\) on odd total parity, exact \(U\) on even total parity, and the
inverse below give a global bijection:

- odd output inverse: \(R M U J\);
- even output inverse: \(U\).

For odd inputs the error norm is exactly one. For noncentral pair moves the
radial difference is strictly below \(1/2\); central moves and even inputs
preserve norm. See the proof for the score-phase and tie argument.

## Checks

~~~~sh
python3 -I -B mechanism_check.py > /tmp/odd-map-result.json
cmp /tmp/odd-map-result.json RESULT.json
python3 -I -O -B mechanism_check.py
~~~~

The checker verifies the matrix identities, all 65,536 half-lattice vectors
with doubled coordinates in \([-15,15]^4\), every odd point in precisely
the assigned balls \(R=5,9,11\), 28 explicit odd round trips up to scale
\(2^{1024}\), and large even exact-\(U\) round trips. These finite checks
corroborate the all-input algebra; they are not an extrapolation to further
radii.

This is a review artifact for the proposed mechanism, not a separate PR.
The previous finite quotient receipts remain frozen in the sibling
odd-parity-bilateral-half-sweep package.
